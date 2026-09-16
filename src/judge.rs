//! Optional, per-cell TypeSafe Jev evaluation. No persistent cache or configurable origin.
use anyhow::{Result, bail, ensure};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value, json};
#[cfg(feature = "typesafe")]
use std::io::Read;
use std::{
    collections::HashMap,
    time::{Duration, Instant},
};

#[derive(Clone, Deserialize, Serialize, Debug)]
#[serde(default, deny_unknown_fields)]
pub struct JudgeConfig {
    pub enabled: bool,
    pub model: String,
    pub key_env: String,
    pub expected_model: Option<String>,
    pub timeout_secs: u64,
    pub max_requests_per_cell: usize,
    pub max_questions_per_cell: usize,
    pub max_request_bytes: usize,
    pub max_response_bytes: usize,
    pub max_input_tokens_per_cell: u64,
}
impl Default for JudgeConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            model: "jev-latest".into(),
            key_env: "TYPESAFE_API_KEY".into(),
            expected_model: None,
            timeout_secs: 20,
            max_requests_per_cell: 8,
            max_questions_per_cell: 128,
            max_request_bytes: 131_072,
            max_response_bytes: 262_144,
            max_input_tokens_per_cell: 100_000,
        }
    }
}
impl JudgeConfig {
    pub fn validate(&self) -> Result<()> {
        ensure!(valid_id(&self.model), "judge: invalid configured model");
        ensure!(
            self.expected_model.as_deref().is_none_or(valid_id),
            "judge: invalid expected model"
        );
        let mut chars = self.key_env.chars();
        ensure!(
            chars
                .next()
                .is_some_and(|c| c.is_ascii_alphabetic() || c == '_')
                && chars.all(|c| c.is_ascii_alphanumeric() || c == '_')
                && self.key_env.len() <= 256,
            "judge: invalid key environment name"
        );
        ensure!(
            (1..=3600).contains(&self.timeout_secs),
            "judge: invalid timeout"
        );
        ensure!(
            self.max_requests_per_cell > 0 && self.max_questions_per_cell > 0,
            "judge: request and question limits must be positive"
        );
        ensure!(
            self.max_request_bytes > 0
                && self.max_request_bytes < usize::MAX
                && self.max_response_bytes > 0
                && self.max_response_bytes < usize::MAX,
            "judge: invalid byte limits"
        );
        ensure!(
            self.max_input_tokens_per_cell > 0 && self.max_input_tokens_per_cell <= (1u64 << 53),
            "judge: input token limit must be positive and exactly representable"
        );
        Ok(())
    }
}

// Private dependency seams allow real evaluation-path tests without credentials or network.
type Credential = Box<dyn FnMut(&str) -> Result<String>>;
type Transport = Box<dyn FnMut(&JudgeConfig, &[u8], &str, Duration) -> Result<Vec<u8>>>;
pub struct JudgeEngine {
    config: JudgeConfig,
    credential: Credential,
    transport: Transport,
    cache: HashMap<Vec<u8>, Value>,
    attempts: usize,
    questions: usize,
    cache_hits: usize,
    known_input_tokens: u64,
    unknown_input_usage_requests: usize,
    poisoned: bool,
    transport_available: bool,
    deadline: Option<Instant>,
}
impl JudgeEngine {
    pub fn new(config: &JudgeConfig) -> Self {
        let mut engine = Self::with_dependencies(
            config,
            Box::new(|name| {
                std::env::var(name).map_err(|_| anyhow::anyhow!("judge: credential unavailable"))
            }),
            Box::new(http_request),
        );
        engine.transport_available = cfg!(feature = "typesafe");
        engine
    }
    fn with_dependencies(
        config: &JudgeConfig,
        credential: Credential,
        transport: Transport,
    ) -> Self {
        Self {
            config: config.clone(),
            credential,
            transport,
            cache: HashMap::new(),
            attempts: 0,
            questions: 0,
            cache_hits: 0,
            known_input_tokens: 0,
            unknown_input_usage_requests: 0,
            poisoned: false,
            transport_available: true,
            deadline: None,
        }
    }
    /// Set the cell wall-clock deadline. Subsequent calls may tighten, never extend it.
    pub fn set_deadline(&mut self, deadline: Instant) {
        self.deadline = Some(self.deadline.map_or(deadline, |old| old.min(deadline)));
    }
    fn remaining_timeout(&self) -> Result<Duration> {
        let timeout = Duration::from_secs(self.config.timeout_secs);
        match self.deadline {
            None => Ok(timeout),
            Some(deadline) => {
                let remaining = deadline.saturating_duration_since(Instant::now());
                ensure!(!remaining.is_zero(), "judge: cell deadline exceeded");
                Ok(timeout.min(remaining))
            }
        }
    }
    pub fn stats(&self) -> Value {
        json!({"enabled": self.config.enabled, "poisoned": self.poisoned,
            "transport_available": self.transport_available,
            "provider_requests": self.attempts, "attempts": self.attempts,
            "questions": self.questions, "cache_hits": self.cache_hits,
            "cached_requests": self.cache.len(), "known_input_tokens": self.known_input_tokens,
            "unknown_input_usage_requests": self.unknown_input_usage_requests,
            "input_usage_complete": self.unknown_input_usage_requests == 0,
            "billing": "not_inferred"})
    }
    pub fn evaluate(&mut self, state: Value, questions: Value) -> Result<Value> {
        let started = Instant::now();
        ensure!(self.config.enabled, "judge: disabled");
        self.config.validate()?;
        ensure!(
            self.transport_available,
            "judge: typesafe feature is not enabled in this build"
        );
        self.remaining_timeout()?;
        ensure!(
            !self.poisoned,
            "judge: engine poisoned after provider failure"
        );
        ensure!(
            structured(&state),
            "judge: state must be string, object, or array"
        );
        let count = validate_questions(&questions)?;
        let request = json!({"model": self.config.model, "state": state, "questions": questions});
        let bytes =
            serde_json::to_vec(&request).map_err(|_| anyhow::anyhow!("judge: invalid request"))?;
        ensure!(
            bytes.len() <= self.config.max_request_bytes,
            "judge: request byte limit exceeded"
        );
        let digest = crate::sha256_hex(&bytes);
        self.remaining_timeout()?;
        if let Some(body) = self.cache.get(&bytes).cloned() {
            self.cache_hits += 1;
            return Ok(annotate(body, &digest, true, started));
        }
        ensure!(
            self.attempts < self.config.max_requests_per_cell,
            "judge: request limit exceeded"
        );
        ensure!(
            count
                <= self
                    .config
                    .max_questions_per_cell
                    .saturating_sub(self.questions),
            "judge: question limit exceeded"
        );
        ensure!(
            self.known_input_tokens < self.config.max_input_tokens_per_cell,
            "judge: input token limit exhausted"
        );
        self.remaining_timeout()?;
        let key = (self.credential)(&self.config.key_env)
            .map_err(|_| anyhow::anyhow!("judge: credential unavailable"))?;
        ensure!(safe_token(&key), "judge: invalid credential syntax");
        ensure!(
            !contains_secret(&request, &key),
            "judge: credential leakage refused"
        );
        let timeout = self.remaining_timeout()?;
        self.attempts += 1;
        self.questions += count;
        self.unknown_input_usage_requests += 1;
        // Every failure after this point poisons this cell, including transport and schema errors.
        self.poisoned = true;
        let raw = (self.transport)(&self.config, &bytes, &key, timeout).map_err(|error| {
            // Only our production transport's deliberately sanitized errors are propagated.
            // Injected transport errors are also sanitized, regardless of their contents.
            if let Some(status) = error.downcast_ref::<HttpStatus>() {
                anyhow::anyhow!("judge: HTTP status {}", status.0)
            } else {
                anyhow::anyhow!("judge: transport failed")
            }
        })?;
        ensure!(
            raw.len() <= self.config.max_response_bytes,
            "judge: response byte limit exceeded"
        );
        let body = serde_json::from_slice::<crate::UniqueJsonValue>(&raw)
            .map_err(|_| anyhow::anyhow!("judge: malformed or duplicate response JSON"))?
            .0;
        ensure!(
            !contains_secret(&body, &key),
            "judge: credential leakage refused"
        );
        let input_usage = validate_usage(body.get("usage"))?;
        if let Some(input) = input_usage {
            self.known_input_tokens = self
                .known_input_tokens
                .checked_add(input)
                .ok_or_else(|| anyhow::anyhow!("judge: input token accounting overflow"))?;
            self.unknown_input_usage_requests -= 1;
            ensure!(
                self.known_input_tokens <= self.config.max_input_tokens_per_cell,
                "judge: reported input token limit exceeded"
            );
        }
        validate_response(&body, &questions, &self.config)?;
        self.remaining_timeout()?;
        self.poisoned = false;
        self.cache.insert(bytes, body.clone());
        Ok(annotate(body, &digest, false, started))
    }
}

#[derive(Debug)]
struct HttpStatus(u16);
impl std::fmt::Display for HttpStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "judge: HTTP status {}", self.0)
    }
}
impl std::error::Error for HttpStatus {}
#[cfg(not(feature = "typesafe"))]
fn http_request(_: &JudgeConfig, _: &[u8], _: &str, _: Duration) -> Result<Vec<u8>> {
    bail!("judge: typesafe feature is not enabled in this build")
}
#[cfg(feature = "typesafe")]
fn http_request(
    config: &JudgeConfig,
    bytes: &[u8],
    key: &str,
    timeout: Duration,
) -> Result<Vec<u8>> {
    let client = reqwest::blocking::Client::builder()
        .https_only(true)
        .no_proxy()
        .redirect(reqwest::redirect::Policy::none())
        .retry(reqwest::retry::never())
        .timeout(timeout)
        .build()
        .map_err(|_| anyhow::anyhow!("judge: transport initialization failed"))?;
    let mut authorization = reqwest::header::HeaderValue::from_str(&format!("Bearer {key}"))
        .map_err(|_| anyhow::anyhow!("judge: invalid credential syntax"))?;
    authorization.set_sensitive(true);
    let response = client
        .post("https://api.typesafe.ai/v1/systemone")
        .header(reqwest::header::AUTHORIZATION, authorization)
        .header(reqwest::header::CONTENT_TYPE, "application/json")
        .body(bytes.to_vec())
        .send()
        .map_err(|_| anyhow::anyhow!("judge: transport failed"))?;
    if !response.status().is_success() {
        return Err(HttpStatus(response.status().as_u16()).into());
    }
    let mut raw = Vec::new();
    response
        .take(config.max_response_bytes as u64 + 1)
        .read_to_end(&mut raw)
        .map_err(|_| anyhow::anyhow!("judge: response read failed"))?;
    Ok(raw)
}
fn annotate(mut body: Value, digest: &str, hit: bool, started: Instant) -> Value {
    let original_usage = body.get("usage").cloned().unwrap_or(Value::Null);
    let object = body.as_object_mut().expect("validated response object");
    object.entry("usage").or_insert(Value::Null);
    object.insert("_azdaja".into(), json!({
        "request_sha256": digest, "cache_hit": hit,
        "provider_requests_this_call": if hit { 0 } else { 1 },
        "elapsed_ms": started.elapsed().as_millis().min(u64::MAX as u128) as u64,
        "original_usage": original_usage,
        "usage_semantics": if hit { "original_observation_reused_no_new_request" } else { "original_provider_request" },
        "new_request_usage": if hit { Value::Null } else { original_usage },
        "model_semantics": "provider_reported_identifier_not_immutable_weights",
        "billing": "not_inferred"
    }));
    body
}
fn valid_id(id: &str) -> bool {
    !id.is_empty() && id.len() <= 256 && !id.chars().any(char::is_control) && !id.trim().is_empty()
}
fn structured(value: &Value) -> bool {
    value.is_string() || value.is_object() || value.is_array()
}
fn safe_token(key: &str) -> bool {
    // RFC 6750 b64token, including common opaque API-key punctuation.
    let base = key.trim_end_matches('=');
    !base.is_empty()
        && key.len() <= 8192
        && base
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"-._~+/".contains(&b))
}
fn contains_secret(value: &Value, secret: &str) -> bool {
    match value {
        Value::String(s) => s.contains(secret),
        Value::Array(a) => a.iter().any(|v| contains_secret(v, secret)),
        Value::Object(o) => o
            .iter()
            .any(|(k, v)| k.contains(secret) || contains_secret(v, secret)),
        _ => false,
    }
}
fn object(value: &Value) -> Result<&Map<String, Value>> {
    value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("judge: expected object"))
}
fn fields(object: &Map<String, Value>, required: &[&str], optional: &[&str]) -> Result<()> {
    ensure!(
        required.iter().all(|k| object.contains_key(*k))
            && object
                .keys()
                .all(|k| required.contains(&k.as_str()) || optional.contains(&k.as_str())),
        "judge: unexpected or missing fields"
    );
    Ok(())
}
fn validate_questions(value: &Value) -> Result<usize> {
    let questions = object(value)?;
    ensure!(!questions.is_empty(), "judge: questions must not be empty");
    for (id, question) in questions {
        ensure!(valid_id(id), "judge: invalid question ID");
        let q = object(question)?;
        fields(q, &["type", "instructions"], &["criteria"])?;
        ensure!(
            structured(&q["instructions"]),
            "judge: invalid instructions"
        );
        match q["type"].as_str() {
            Some("noul") => {
                if let Some(criteria) = q.get("criteria") {
                    let c = object(criteria)?;
                    fields(c, &["true", "false"], &[])?;
                    ensure!(
                        c.values().all(Value::is_string),
                        "judge: invalid noul criteria"
                    );
                }
            }
            Some("choice") => {
                let c = q
                    .get("criteria")
                    .and_then(Value::as_object)
                    .ok_or_else(|| anyhow::anyhow!("judge: invalid choice criteria"))?;
                ensure!(
                    c.len() >= 2
                        && c.iter()
                            .all(|(k, v)| valid_id(k) && (v.is_string() || v.is_null())),
                    "judge: invalid choice criteria"
                );
            }
            Some("score") => {
                let c = q
                    .get("criteria")
                    .and_then(Value::as_array)
                    .ok_or_else(|| anyhow::anyhow!("judge: invalid score criteria"))?;
                ensure!(
                    c.len() >= 2 && c.iter().all(Value::is_string),
                    "judge: invalid score criteria"
                );
            }
            _ => bail!("judge: invalid question type"),
        }
    }
    Ok(questions.len())
}
fn number(value: &Value) -> Result<f64> {
    let n = value
        .as_f64()
        .ok_or_else(|| anyhow::anyhow!("judge: expected finite number"))?;
    ensure!(
        n.is_finite() && n >= 0.0,
        "judge: expected finite nonnegative number"
    );
    Ok(n)
}
fn probability(value: &Value) -> Result<f64> {
    let n = number(value)?;
    ensure!(n <= 1.0, "judge: probability out of range");
    Ok(n)
}
fn token_count(value: &Value) -> Result<Option<u64>> {
    if value.is_null() {
        return Ok(None);
    }
    value
        .as_u64()
        .map(Some)
        .ok_or_else(|| anyhow::anyhow!("judge: expected nonnegative integer token count"))
}
fn validate_usage(usage: Option<&Value>) -> Result<Option<u64>> {
    match usage {
        None | Some(Value::Null) => Ok(None),
        Some(value) => {
            let usage = object(value)?;
            for value in usage.values() {
                token_count(value)?;
            }
            match usage.get("input_tokens") {
                None => Ok(None),
                Some(value) => token_count(value),
            }
        }
    }
}
fn distribution<'a>(
    value: &'a Value,
    domain: &Map<String, Value>,
) -> Result<&'a Map<String, Value>> {
    let p = object(value)?;
    ensure!(
        p.len() == domain.len() && p.keys().all(|k| domain.contains_key(k)),
        "judge: probability domain mismatch"
    );
    let mut sum = 0.0;
    for value in p.values() {
        sum += probability(value)?;
    }
    ensure!(
        (sum - 1.0).abs() <= 1e-6,
        "judge: probabilities must sum to one"
    );
    Ok(p)
}
fn validate_response(body: &Value, questions: &Value, config: &JudgeConfig) -> Result<()> {
    let response = object(body)?;
    fields(response, &["model", "answers"], &["usage"])?;
    let model = response["model"]
        .as_str()
        .filter(|s| valid_id(s))
        .ok_or_else(|| anyhow::anyhow!("judge: invalid returned model"))?;
    ensure!(
        config
            .expected_model
            .as_deref()
            .is_none_or(|expected| model == expected),
        "judge: returned model does not match expected model"
    );
    let answers = object(&response["answers"])?;
    let questions = object(questions)?;
    ensure!(
        answers.len() == questions.len() && answers.keys().all(|k| questions.contains_key(k)),
        "judge: answer IDs do not cover questions exactly"
    );
    for (id, question) in questions {
        let a = object(&answers[id])?;
        ensure!(
            a.get("type") == question.get("type"),
            "judge: answer type mismatch"
        );
        match question["type"].as_str() {
            Some("noul") => {
                fields(a, &["type", "noul"], &[])?;
                probability(&a["noul"])?;
            }
            Some("choice") => {
                fields(a, &["type", "choice", "probabilities", "confidence"], &[])?;
                probability(&a["confidence"])?;
                let p = distribution(&a["probabilities"], object(&question["criteria"])?)?;
                let selected = a["choice"]
                    .as_str()
                    .and_then(|s| p.get(s))
                    .ok_or_else(|| anyhow::anyhow!("judge: choice outside domain"))?;
                let selected = probability(selected)?;
                ensure!(
                    p.values()
                        .all(|v| v.as_f64().is_some_and(|n| n <= selected)),
                    "judge: choice is not an argmax"
                );
            }
            Some("score") => {
                fields(
                    a,
                    &["type", "score", "legend", "probabilities", "confidence"],
                    &[],
                )?;
                probability(&a["confidence"])?;
                let criteria = question["criteria"].as_array().expect("validated criteria");
                let legend: Map<String, Value> = criteria
                    .iter()
                    .enumerate()
                    .map(|(i, v)| (i.to_string(), v.clone()))
                    .collect();
                ensure!(
                    object(&a["legend"])? == &legend,
                    "judge: score legend mismatch"
                );
                let p = distribution(&a["probabilities"], &legend)?;
                let expected: f64 = (0..criteria.len())
                    .map(|i| i as f64 * p[&i.to_string()].as_f64().unwrap())
                    .sum();
                let score = number(&a["score"])?;
                ensure!(
                    score <= (criteria.len() - 1) as f64
                        && (score - expected).abs() <= 1e-6 * (1.0 + expected.abs()),
                    "judge: score does not match weighted probabilities"
                );
            }
            _ => bail!("judge: invalid question type"),
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{cell::Cell, rc::Rc};
    const KEY: &str = "test-key-never-a-real-credential";
    fn questions() -> Value {
        json!({
            "n": {"type":"noul", "instructions":{"ask":"Urgent?"}, "criteria":{"true":"yes", "false":"no"}},
            "c": {"type":"choice", "instructions":["Pick"], "criteria":{"a":null,"b":"B"}},
            "s": {"type":"score", "instructions":"Rate", "criteria":["low","high"]}
        })
    }
    fn response() -> Value {
        json!({"model":"jev-latest", "answers":{
            "n":{"type":"noul","noul":0.7},
            "c":{"type":"choice","choice":"b","probabilities":{"a":0.2,"b":0.8},"confidence":0.6},
            "s":{"type":"score","score":0.75,"legend":{"0":"low","1":"high"},"probabilities":{"0":0.25,"1":0.75},"confidence":0.5}
        }, "usage":{"input_tokens":10,"output_tokens":4}})
    }
    fn config() -> JudgeConfig {
        JudgeConfig {
            enabled: true,
            ..JudgeConfig::default()
        }
    }
    fn engine(
        config: &JudgeConfig,
        bytes: Vec<u8>,
    ) -> (JudgeEngine, Rc<Cell<usize>>, Rc<Cell<usize>>) {
        let credentials = Rc::new(Cell::new(0));
        let calls = Rc::new(Cell::new(0));
        let (credential_count, call_count) = (credentials.clone(), calls.clone());
        let engine = JudgeEngine::with_dependencies(
            config,
            Box::new(move |_| {
                credential_count.set(credential_count.get() + 1);
                Ok(KEY.into())
            }),
            Box::new(move |_, request, key, _| {
                assert_eq!(key, KEY);
                let sent: Value = serde_json::from_slice(request).unwrap();
                assert_eq!(sent["model"], "jev-latest");
                call_count.set(call_count.get() + 1);
                Ok(bytes.clone())
            }),
        );
        (engine, credentials, calls)
    }
    fn fixture(
        config: &JudgeConfig,
        body: Value,
    ) -> (JudgeEngine, Rc<Cell<usize>>, Rc<Cell<usize>>) {
        engine(config, serde_json::to_vec(&body).unwrap())
    }
    #[test]
    fn all_primitives_cache_and_question_mutation() {
        let (mut e, credentials, calls) = fixture(&config(), response());
        let first = e.evaluate(json!({"text":"hello"}), questions()).unwrap();
        assert_eq!(first["answers"], response()["answers"]);
        assert_eq!(first["_azdaja"]["provider_requests_this_call"], 1);
        let second = e.evaluate(json!({"text":"hello"}), questions()).unwrap();
        assert_eq!(second["_azdaja"]["cache_hit"], true);
        assert_eq!(second["_azdaja"]["provider_requests_this_call"], 0);
        assert_eq!(second["usage"], first["usage"]);
        assert_eq!(second["_azdaja"]["original_usage"], first["usage"]);
        assert!(second["_azdaja"]["new_request_usage"].is_null());
        assert_eq!(e.stats()["known_input_tokens"], 10);
        assert_eq!((credentials.get(), calls.get()), (1, 1));
        let mut q = questions();
        q["n"]["instructions"] = json!("Changed");
        let changed = e.evaluate(json!({"text":"hello"}), q).unwrap();
        assert_ne!(
            changed["_azdaja"]["request_sha256"],
            first["_azdaja"]["request_sha256"]
        );
        assert_eq!(e.stats()["questions"], 6);
        assert_eq!((credentials.get(), calls.get()), (2, 2));
    }
    #[test]
    fn model_alias_concrete_and_explicit_expectation() {
        for model in ["jev-latest", "jev-2026-09-16"] {
            let mut body = response();
            body["model"] = json!(model);
            let (mut e, _, _) = fixture(&config(), body.clone());
            assert_eq!(e.evaluate(json!([]), questions()).unwrap()["model"], model);
            let c = JudgeConfig {
                expected_model: Some(model.into()),
                ..config()
            };
            let (mut e, _, _) = fixture(&c, body);
            assert!(e.evaluate(json!("state"), questions()).is_ok());
        }
        let c = JudgeConfig {
            expected_model: Some("known-concrete-id".into()),
            ..config()
        };
        let (mut e, _, _) = fixture(&c, response());
        assert!(e.evaluate(json!("state"), questions()).is_err());
        assert!(e.poisoned);
    }
    #[test]
    fn malformed_duplicate_extra_missing_ids_and_types() {
        let mut variants = vec![
            b"not json".to_vec(),
            br#"{"model":"jev-latest","model":"jev-latest","answers":{}}"#.to_vec(),
            br#"{"model":"jev-latest","answers":{"n":{"type":"noul","noul":0.2,"noul":0.7}}}"#
                .to_vec(),
        ];
        for mutation in 0..7 {
            let mut r = response();
            match mutation {
                0 => {
                    r["answers"].as_object_mut().unwrap().remove("n");
                }
                1 => {
                    r["answers"]["extra"] = r["answers"]["n"].clone();
                }
                2 => {
                    r["answers"]["n"]["type"] = json!("choice");
                }
                3 => {
                    r["model"] = json!("bad\nmodel");
                }
                4 => {
                    r["model"] = json!("");
                }
                5 => {
                    r["answers"]["n"]["unexpected"] = json!(true);
                }
                _ => {
                    r["answers"] = json!([]);
                }
            }
            variants.push(serde_json::to_vec(&r).unwrap());
        }
        for bytes in variants {
            let (mut e, _, calls) = engine(&config(), bytes);
            assert!(e.evaluate(json!("private state"), questions()).is_err());
            assert!(e.poisoned);
            assert!(e.evaluate(json!("another state"), questions()).is_err());
            assert_eq!(calls.get(), 1);
            assert!(e.cache.is_empty());
        }
    }
    #[test]
    fn invalid_probabilities_argmax_score_and_legend() {
        for mutation in 0..10 {
            let mut r = response();
            match mutation {
                0 => r["answers"]["n"]["noul"] = json!(-0.1),
                1 => r["answers"]["n"]["noul"] = json!(1.1),
                2 => r["answers"]["c"]["probabilities"]["a"] = json!(0.3),
                3 => r["answers"]["c"]["choice"] = json!("a"),
                4 => r["answers"]["c"]["probabilities"] = json!({"a":0.2,"other":0.8}),
                5 => r["answers"]["s"]["score"] = json!(0.8),
                6 => r["answers"]["s"]["legend"]["0"] = json!("wrong"),
                7 => r["answers"]["s"]["confidence"] = json!(1.01),
                8 => r["answers"]["n"]["noul"] = json!("0.7"),
                _ => r["answers"]["s"]["probabilities"]["1"] = Value::Null,
            }
            let (mut e, _, _) = fixture(&config(), r);
            assert!(
                e.evaluate(json!("state"), questions()).is_err(),
                "mutation {mutation}"
            );
        }
    }
    #[test]
    fn budgets_are_debited_and_crossing_retains_usage_without_answers() {
        let c = JudgeConfig {
            max_input_tokens_per_cell: 15,
            ..config()
        };
        let (mut e, _, calls) = fixture(&c, response());
        e.evaluate(json!("first"), questions()).unwrap();
        assert!(e.evaluate(json!("second"), questions()).is_err());
        assert_eq!(e.stats()["known_input_tokens"], 20);
        assert_eq!(e.stats()["unknown_input_usage_requests"], 0);
        assert_eq!(e.stats()["attempts"], 2);
        assert_eq!(e.stats()["questions"], 6);
        assert!(e.poisoned);
        assert_eq!(e.cache.len(), 1);
        assert!(e.evaluate(json!("third"), questions()).is_err());
        assert_eq!(calls.get(), 2);
    }
    #[test]
    fn preflight_limits_and_invalid_arguments_do_not_read_credentials() {
        for c in [
            JudgeConfig::default(),
            JudgeConfig {
                max_questions_per_cell: 2,
                ..config()
            },
            JudgeConfig {
                max_request_bytes: 10,
                ..config()
            },
        ] {
            let (mut e, credentials, calls) = fixture(&c, response());
            assert!(e.evaluate(json!("state"), questions()).is_err());
            assert_eq!((credentials.get(), calls.get()), (0, 0));
            assert!(!e.poisoned);
        }
        let (mut e, credentials, _) = fixture(&config(), response());
        assert!(e.evaluate(json!(123), questions()).is_err());
        for q in [
            json!({}),
            json!({"":{"type":"noul","instructions":"x"}}),
            json!({"x":{"type":"choice","instructions":"x","criteria":{"only":null}}}),
            json!({"x":{"type":"score","instructions":"x","criteria":["only"]}}),
            json!({"x":{"type":"noul","instructions":42}}),
        ] {
            assert!(e.evaluate(json!("state"), q).is_err());
        }
        assert_eq!(credentials.get(), 0);
        assert!(!e.poisoned);
        e.evaluate(json!("valid"), questions()).unwrap();
    }
    #[test]
    fn unknown_usage_is_not_zero_billing_and_bad_usage_poisoned() {
        let mut body = response();
        body.as_object_mut().unwrap().remove("usage");
        let (mut e, _, _) = fixture(&config(), body);
        let r = e.evaluate(json!("state"), questions()).unwrap();
        assert!(r["usage"].is_null());
        assert_eq!(e.stats()["unknown_input_usage_requests"], 1);
        assert_eq!(e.stats()["input_usage_complete"], false);
        assert_eq!(r["_azdaja"]["billing"], "not_inferred");
        for usage in [
            json!({"input_tokens":-1}),
            json!({"output_tokens":"bad"}),
            json!([]),
        ] {
            let mut body = response();
            body["usage"] = usage;
            let (mut e, _, _) = fixture(&config(), body);
            assert!(e.evaluate(json!("state"), questions()).is_err());
            assert!(e.poisoned);
        }
    }
    #[test]
    fn token_counts_are_integers_and_null_is_unknown_not_zero() {
        for field in ["input_tokens", "output_tokens"] {
            for value in [json!(0.5), json!(1.0), json!(true), json!(-1), json!("10")] {
                let mut body = response();
                body["usage"][field] = value;
                let (mut e, _, calls) = fixture(&config(), body);
                assert_eq!(
                    e.evaluate(json!("state"), questions())
                        .unwrap_err()
                        .to_string(),
                    "judge: expected nonnegative integer token count"
                );
                assert!(e.poisoned);
                assert!(e.cache.is_empty());
                assert_eq!(calls.get(), 1);
                assert_eq!(e.stats()["unknown_input_usage_requests"], 1);
            }
        }
        let mut body = response();
        body["usage"] = json!({"input_tokens":null, "output_tokens":null});
        let (mut e, _, _) = fixture(&config(), body);
        let result = e.evaluate(json!("state"), questions()).unwrap();
        assert!(result["usage"]["input_tokens"].is_null());
        assert_eq!(e.stats()["known_input_tokens"], 0);
        assert_eq!(e.stats()["unknown_input_usage_requests"], 1);
        assert_eq!(e.stats()["input_usage_complete"], false);
    }
    #[test]
    fn integer_token_budget_crossing_and_overflow_stay_terminal() {
        let mut body = response();
        body["usage"]["input_tokens"] = json!(u64::MAX);
        let (mut e, _, _) = fixture(&config(), body.clone());
        let error = e.evaluate(json!("state"), questions()).unwrap_err();
        assert_eq!(
            error.to_string(),
            "judge: reported input token limit exceeded"
        );
        assert_eq!(e.stats()["known_input_tokens"].as_u64(), Some(u64::MAX));
        assert!(e.poisoned);
        let (mut e, _, _) = fixture(&config(), body);
        e.known_input_tokens = 1;
        assert_eq!(
            e.evaluate(json!("state"), questions())
                .unwrap_err()
                .to_string(),
            "judge: input token accounting overflow"
        );
        assert_eq!(e.stats()["unknown_input_usage_requests"], 1);
        assert!(e.poisoned);
    }
    #[test]
    fn request_cap_allows_cache_without_new_credential_or_observation() {
        let c = JudgeConfig {
            max_requests_per_cell: 1,
            max_questions_per_cell: 3,
            ..config()
        };
        let (mut e, credentials, calls) = fixture(&c, response());
        e.evaluate(json!("state"), questions()).unwrap();
        e.evaluate(json!("state"), questions()).unwrap();
        assert!(e.evaluate(json!("changed"), questions()).is_err());
        assert_eq!((credentials.get(), calls.get()), (1, 1));
        assert_eq!(e.stats()["cache_hits"], 1);
    }
    #[test]
    fn secret_safe_errors_and_poisoned_transport_failure() {
        let mut e = JudgeEngine::with_dependencies(
            &config(),
            Box::new(|_| Ok(KEY.into())),
            Box::new(|_, _, _, _| bail!("{KEY}: raw response or private state")),
        );
        let err = e
            .evaluate(json!("state"), questions())
            .unwrap_err()
            .to_string();
        assert_eq!(err, "judge: transport failed");
        assert!(e.poisoned);
        assert_eq!(e.stats()["unknown_input_usage_requests"], 1);
        let (mut e, _, calls) = fixture(&config(), response());
        let err = e
            .evaluate(json!({"nested":[KEY]}), questions())
            .unwrap_err()
            .to_string();
        assert!(!err.contains(KEY));
        assert_eq!(calls.get(), 0);
        assert!(!e.poisoned);
        let mut body = response();
        body["model"] = json!(KEY);
        let (mut e, _, _) = fixture(&config(), body);
        let err = e
            .evaluate(json!("state"), questions())
            .unwrap_err()
            .to_string();
        assert!(!err.contains(KEY));
        assert!(e.poisoned);
        let mut e = JudgeEngine::with_dependencies(
            &config(),
            Box::new(|_| Ok("unsafe\r\nkey".into())),
            Box::new(|_, _, _, _| panic!("must not enter transport")),
        );
        assert_eq!(
            e.evaluate(json!("state"), questions())
                .unwrap_err()
                .to_string(),
            "judge: invalid credential syntax"
        );
    }
    #[test]
    fn deadline_preflight_and_transport_timeout() {
        let (mut e, credentials, calls) = fixture(&config(), response());
        e.set_deadline(Instant::now());
        e.set_deadline(Instant::now() + Duration::from_secs(30));
        assert!(
            e.evaluate(json!("state"), questions())
                .unwrap_err()
                .to_string()
                .contains("deadline")
        );
        assert_eq!((credentials.get(), calls.get()), (0, 0));
        assert!(!e.poisoned);
        let mut e = JudgeEngine::with_dependencies(
            &config(),
            Box::new(|_| Ok(KEY.into())),
            Box::new(|_, _, _, timeout| {
                assert!(timeout > Duration::ZERO && timeout <= Duration::from_secs(2));
                Ok(serde_json::to_vec(&response()).unwrap())
            }),
        );
        e.set_deadline(Instant::now() + Duration::from_secs(2));
        e.evaluate(json!("state"), questions()).unwrap();
    }
    #[test]
    fn elapsed_transport_deadline_poisoned_but_usage_retained() {
        let mut e = JudgeEngine::with_dependencies(
            &config(),
            Box::new(|_| Ok(KEY.into())),
            Box::new(|_, _, _, timeout| {
                std::thread::sleep(timeout + Duration::from_millis(1));
                Ok(serde_json::to_vec(&response()).unwrap())
            }),
        );
        e.set_deadline(Instant::now() + Duration::from_millis(50));
        let err = e.evaluate(json!("state"), questions()).unwrap_err();
        assert!(err.to_string().contains("deadline"));
        assert!(e.poisoned);
        assert!(e.cache.is_empty());
        assert_eq!(e.stats()["known_input_tokens"], 10);
    }
    #[cfg(not(feature = "typesafe"))]
    #[test]
    fn unavailable_feature_never_reads_credentials() {
        let (mut e, credentials, calls) = fixture(&config(), response());
        e.transport_available = false;
        assert!(
            e.evaluate(json!("state"), questions())
                .unwrap_err()
                .to_string()
                .contains("typesafe feature")
        );
        assert_eq!((credentials.get(), calls.get()), (0, 0));
        assert!(!JudgeEngine::new(&config()).transport_available);
    }
    #[test]
    fn response_size_http_status_and_config_validation() {
        let c = JudgeConfig {
            max_response_bytes: 5,
            ..config()
        };
        let (mut e, _, _) = fixture(&c, response());
        assert!(e.evaluate(json!("state"), questions()).is_err());
        assert!(e.poisoned);
        let mut e = JudgeEngine::with_dependencies(
            &config(),
            Box::new(|_| Ok(KEY.into())),
            Box::new(|_, _, _, _| Err(HttpStatus(429).into())),
        );
        assert_eq!(
            e.evaluate(json!("state"), questions())
                .unwrap_err()
                .to_string(),
            "judge: HTTP status 429"
        );
        let defaults: JudgeConfig = serde_json::from_value(json!({})).unwrap();
        assert!(!defaults.enabled);
        defaults.validate().unwrap();
        assert!(serde_json::from_value::<JudgeConfig>(json!({"unexpected":true})).is_err());
        for field in [
            "timeout_secs",
            "max_requests_per_cell",
            "max_questions_per_cell",
            "max_request_bytes",
            "max_response_bytes",
            "max_input_tokens_per_cell",
        ] {
            let mut value = serde_json::to_value(&defaults).unwrap();
            value[field] = json!(0);
            assert!(
                serde_json::from_value::<JudgeConfig>(value)
                    .unwrap()
                    .validate()
                    .is_err()
            );
        }
    }
}
