// Appended ONLY to an isolated exact-source judge.rs copy. Never shipped.
#[cfg(all(test, feature = "typesafe"))]
mod second_reader_probe {
    use super::*;
    use std::{fs, io::Write, path::PathBuf, sync::{Arc, Mutex}};

    fn write_new(path: &std::path::Path, bytes: &[u8]) -> Result<()> {
        let mut file = crate::create_private_file(path)?;
        file.write_all(bytes)?;
        file.sync_all()?;
        Ok(())
    }

    #[test]
    fn boundary_diagnosis_offline() {
        let domain = json!({"a":null,"b":null,"c":null});
        assert!(distribution(&json!({"a":0.1,"b":0.2,"c":0.7}), domain.as_object().unwrap()).is_ok());
        assert!(distribution(&json!({"a":0.3333333,"b":0.3333333,"c":0.3333333}), domain.as_object().unwrap()).is_ok());
        assert_eq!(distribution(&json!({"a":0.33,"b":0.33,"c":0.33}), domain.as_object().unwrap()).unwrap_err().to_string(), "judge: probabilities must sum to one");
        assert_eq!(distribution(&json!({"a":0.6,"b":0.6,"c":0.6}), domain.as_object().unwrap()).unwrap_err().to_string(), "judge: probabilities must sum to one");
        assert!(distribution(&json!({"a":true,"b":0.0,"c":0.0}), domain.as_object().unwrap()).is_err());
        assert!(distribution(&json!({"a":1.01,"b":-0.01,"c":0.0}), domain.as_object().unwrap()).is_err());
        assert!(distribution(&json!({"a":1.0,"b":0.0}), domain.as_object().unwrap()).is_err());
    }

    #[test]
    #[ignore = "explicit one-request user-authorized diagnostic only"]
    fn capture_once() -> Result<()> {
        ensure!(std::env::var("AZDAJA_SECOND_READER_ACK").as_deref() == Ok("one-fresh-diagnostic-request"), "diagnostic acknowledgement required");
        let input = PathBuf::from(std::env::var("AZDAJA_SECOND_READER_REQUEST")?);
        let directory = PathBuf::from(std::env::var("AZDAJA_SECOND_READER_OUTPUT")?);
        let expected = std::env::var("AZDAJA_SECOND_READER_REQUEST_SHA")?;
        let bytes = fs::read(&input)?;
        ensure!(bytes.len() <= 131072 && crate::sha256_hex(&bytes) == expected, "diagnostic request identity");
        let request = serde_json::from_slice::<crate::UniqueJsonValue>(&bytes)?.0;
        fields(object(&request)?, &["model", "state", "questions"], &[])?;
        ensure!(request["model"] == "jev-1.13.0", "diagnostic pinned model");
        ensure!(validate_questions(&request["questions"])? == 25, "diagnostic question coverage");
        let wire = serde_json::to_vec(&request)?;
        // Exclusive durable admission occurs before key resolution and transport.
        write_new(&directory.join("started.json"), &serde_json::to_vec(&json!({"request_file_sha256":expected,"wire_sha256":crate::sha256_hex(&wire),"max_requests":1}))?)?;
        let config = JudgeConfig { enabled: true, model: "jev-1.13.0".into(), expected_model: Some("jev-1.13.0".into()), max_requests_per_cell: 1, max_questions_per_cell: 25, max_input_tokens_per_cell: 100000, ..JudgeConfig::default() };
        let captured = Arc::new(Mutex::new(Value::Null));
        let observation = captured.clone();
        let output = directory.clone();
        let transport: Transport = Box::new(move |config, request, key, timeout| {
            let raw = http_request(config, request, key, timeout)?;
            let raw_sha = crate::sha256_hex(&raw);
            *observation.lock().unwrap() = json!({"raw_sha256":raw_sha,"raw_bytes":raw.len(),"raw_retained":false});
            ensure!(raw.len() <= config.max_response_bytes, "diagnostic response too large");
            let body = serde_json::from_slice::<crate::UniqueJsonValue>(&raw)
                .map_err(|_| anyhow::anyhow!("diagnostic JSON invalid"))?.0;
            ensure!(!contains_secret(&body, key), "diagnostic credential refused");
            // Reject the documented credential shape anywhere, including other keys.
            let decoded = serde_json::to_string(&body)?;
            ensure!(redact_typesafe_keys(&decoded) == decoded, "diagnostic credential pattern refused");
            write_new(&output.join("response.raw.json"), &raw)?;
            *observation.lock().unwrap() = json!({"raw_sha256":raw_sha,"raw_bytes":raw.len(),"raw_retained":true});
            Ok(raw)
        });
        let mut engine = JudgeEngine::with_dependencies(&config, Box::new(crate::credentials::resolve), transport);
        engine.set_deadline(Instant::now() + Duration::from_secs(20));
        let started = Instant::now();
        let result = engine.evaluate(request["state"].clone(), request["questions"].clone());
        let verdict = match result { Ok(_) => json!({"accepted":true,"error":null}), Err(error) => json!({"accepted":false,"error":error.to_string()}) };
        let receipt = json!({"schema":"azdaja.second_reader.diagnostic.v1","original_panel_repaired":false,"semantic_grade_computed":false,"request_file_sha256":expected,"wire_sha256":crate::sha256_hex(&wire),"seconds":started.elapsed().as_secs_f64(),"verdict":verdict,"stats":engine.stats(),"capture":captured.lock().unwrap().clone()});
        write_new(&directory.join("receipt.json"), &serde_json::to_vec(&receipt)?)?;
        println!("Diagnostic observation retained, not scored.");
        Ok(())
    }
}
