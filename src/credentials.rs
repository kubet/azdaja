//! Explicit host-private credentials. These are owner-only plaintext, not a vault.
//! The evaluator never receives paths, credential values or mutation authority.
use anyhow::{Result, anyhow, bail, ensure};
use fs2::FileExt;
use serde_json::{Value, json};
use std::{
    env,
    fs::{self, File},
    io::{Read, Write},
    path::{Path, PathBuf},
    sync::atomic::{AtomicU64, Ordering},
};

const MAX_BYTES: usize = 8192;
static NEXT: AtomicU64 = AtomicU64::new(0);

fn checked_name(name: &str) -> Result<&str> {
    ensure!(
        !name.is_empty()
            && !name.starts_with("apikey_")
            && name.len() <= 256
            && name.bytes().enumerate().all(|(i, b)| {
                b.is_ascii_alphabetic() || b == b'_' || (i > 0 && b.is_ascii_digit())
            }),
        "credentials: invalid environment variable name"
    );
    Ok(name)
}

pub fn storage_available() -> bool {
    cfg!(any(
        target_vendor = "apple",
        target_os = "linux",
        target_os = "android"
    ))
}

fn storage_error(_: anyhow::Error) -> anyhow::Error {
    anyhow!("credentials: private storage unavailable, unsafe, busy, or already occupied")
}

fn state_path() -> Result<PathBuf> {
    crate::strict_absolute_override("AZDAJA_HOME")?
        .or_else(|| crate::xdg_absolute("XDG_STATE_HOME").map(|p| p.join("azdaja")))
        .or_else(|| crate::absolute_home().map(|p| p.join(".local/state/azdaja")))
        .ok_or_else(|| anyhow!("credentials: no absolute private state root"))
}

fn missing(path: &Path) -> Result<bool> {
    match fs::symlink_metadata(path) {
        Ok(_) => Ok(false),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(true),
        Err(error) => Err(error.into()),
    }
}

fn directory(path: &Path, create: bool) -> Result<Option<File>> {
    if missing(path)? {
        if !create {
            return Ok(None);
        }
        // Only new directories are initialized. Existing unsafe modes are never repaired.
        fs::create_dir_all(path.parent().ok_or_else(|| anyhow!("invalid root"))?)?;
        match crate::create_new_private_directory(path) {
            Ok(file) => return Ok(Some(file)),
            Err(error)
                if error
                    .downcast_ref::<std::io::Error>()
                    .is_some_and(|e| e.kind() == std::io::ErrorKind::AlreadyExists) => {}
            Err(error) => return Err(error),
        }
    }
    let file = crate::open_private_directory(path)?;
    crate::validate_private_directory(&file, path)?;
    Ok(Some(file))
}

struct Store {
    root_path: PathBuf,
    path: PathBuf,
    root: File,
    directory: File,
}

impl Store {
    fn at(root_path: PathBuf, create: bool) -> Result<Option<Self>> {
        ensure!(storage_available(), "unsupported private storage");
        let Some(root) = directory(&root_path, create)? else {
            return Ok(None);
        };
        let path = root_path.join("credentials");
        let Some(directory) = directory(&path, create)? else {
            return Ok(None);
        };
        let result = Self {
            root_path,
            path,
            root,
            directory,
        };
        result.validate()?;
        Ok(Some(result))
    }
    fn validate(&self) -> Result<()> {
        crate::validate_private_directory(&self.root, &self.root_path)?;
        crate::validate_private_directory(&self.directory, &self.path)
    }
    fn key_path(&self, name: &str) -> PathBuf {
        // Stable cryptographic identity, including names near the environment-name limit.
        self.path
            .join(format!("{}.key", crate::sha256_hex(name.as_bytes())))
    }
    fn existing(&self, path: &Path) -> Result<Option<File>> {
        self.validate()?;
        if missing(path)? {
            return Ok(None);
        }
        let file = crate::open_private_file(path, false)?;
        self.validate()?;
        Ok(Some(file))
    }
    fn staging(&self, name: &str) -> Result<Vec<PathBuf>> {
        self.validate()?;
        let prefix = format!(".pending-{}-", crate::sha256_hex(name.as_bytes()));
        let mut paths = Vec::new();
        for (index, entry) in fs::read_dir(&self.path)?.enumerate() {
            ensure!(index < 4096, "credential directory entry limit");
            let entry = entry?;
            let name = entry.file_name();
            let Some(name) = name.to_str() else { continue };
            if let Some(suffix) = name.strip_prefix(&prefix) {
                let Some((pid, sequence)) = suffix.split_once('-') else {
                    continue;
                };
                if !pid.is_empty()
                    && !sequence.is_empty()
                    && pid.bytes().all(|b| b.is_ascii_digit())
                    && sequence.bytes().all(|b| b.is_ascii_digit())
                {
                    paths.push(entry.path());
                }
            }
        }
        self.validate()?;
        Ok(paths)
    }
    // Caller holds the store lock. Only this named credential's staging files
    // are considered. A symlink, hardlink or unsafe file causes refusal.
    fn recover_staging(&self, name: &str) -> Result<bool> {
        let mut removed = false;
        for path in self.staging(name)? {
            let Some(file) = self.existing(&path)? else {
                continue;
            };
            crate::validate_private_file(&file, &path)?;
            self.validate()?;
            fs::remove_file(path)?;
            removed = true;
        }
        if removed {
            self.directory.sync_all()?;
        }
        self.validate()?;
        Ok(removed)
    }
    fn read(&self, name: &str) -> Result<Option<String>> {
        let path = self.key_path(name);
        let Some(file) = self.existing(&path)? else {
            return Ok(None);
        };
        ensure!(
            file.metadata()?.len() <= MAX_BYTES as u64,
            "credential too large"
        );
        let mut bytes = Vec::new();
        (&file)
            .take((MAX_BYTES + 1) as u64)
            .read_to_end(&mut bytes)?;
        crate::validate_private_file(&file, &path)?;
        self.validate()?;
        ensure!(bytes.len() <= MAX_BYTES, "credential too large");
        let value = String::from_utf8(bytes)?;
        ensure!(
            crate::judge::safe_token(&value),
            "invalid stored credential"
        );
        Ok(Some(value))
    }
    fn lock(&self) -> Result<File> {
        self.validate()?;
        let path = self.path.join(".lock");
        let file = if missing(&path)? {
            match crate::create_private_file(&path) {
                Ok(file) => file,
                Err(error)
                    if error
                        .downcast_ref::<std::io::Error>()
                        .is_some_and(|e| e.kind() == std::io::ErrorKind::AlreadyExists) =>
                {
                    crate::open_private_file(&path, true)?
                }
                Err(error) => return Err(error),
            }
        } else {
            crate::open_private_file(&path, true)?
        };
        // A concurrent writer fails closed instead of hanging with a secret on stdin.
        FileExt::try_lock_exclusive(&file)?;
        crate::validate_private_file(&file, &path)?;
        self.validate()?;
        Ok(file)
    }
    fn attach(&self, name: &str, secret: &str, replace: bool) -> Result<()> {
        let _lock = self.lock()?;
        let destination = self.key_path(name);
        let existing = self.existing(&destination)?;
        ensure!(replace || existing.is_none(), "credential already attached");
        self.recover_staging(name)?;
        let path = self.path.join(format!(
            ".pending-{}-{}-{}",
            crate::sha256_hex(name.as_bytes()),
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        let mut pending = crate::BoundPrivateFile {
            file: crate::create_private_file(&path)?,
            path,
        };
        pending.file.write_all(secret.as_bytes())?;
        pending.file.sync_all()?;
        crate::validate_private_file(&pending.file, &pending.path)?;
        self.validate()?;
        if let Some(old) = existing {
            crate::validate_private_file(&old, &destination)?;
            fs::rename(&pending.path, &destination)?;
        } else {
            crate::rename_noreplace(&pending.path, &destination)?;
        }
        crate::validate_private_file(&pending.file, &destination)?;
        self.validate()?;
        self.directory.sync_all()?;
        Ok(())
    }
    fn detach(&self, name: &str) -> Result<bool> {
        let destination = self.key_path(name);
        let _lock = self.lock()?;
        let recovered = self.recover_staging(name)?;
        let Some(file) = self.existing(&destination)? else {
            return Ok(recovered);
        };
        crate::validate_private_file(&file, &destination)?;
        self.validate()?;
        fs::remove_file(&destination)?;
        self.directory.sync_all()?;
        self.validate()?;
        Ok(true)
    }
}

/// Exact named environment override wins, including an invalid value. JudgeEngine
/// validates syntax and refuses that value rather than silently falling back.
pub fn resolve(name: &str) -> Result<String> {
    let name = checked_name(name)?;
    match env::var(name) {
        Ok(value) => Ok(value),
        Err(env::VarError::NotUnicode(_)) => bail!("credentials: invalid environment value"),
        Err(env::VarError::NotPresent) => (|| {
            let store = Store::at(state_path()?, false)?.ok_or_else(|| anyhow!("absent"))?;
            store.read(name)?.ok_or_else(|| anyhow!("absent"))
        })()
        .map_err(storage_error),
    }
}

pub fn attach(name: &str, secret: &str, replace: bool) -> Result<()> {
    let name = checked_name(name)?;
    ensure!(
        crate::judge::safe_token(secret),
        "credentials: invalid credential syntax"
    );
    (|| {
        let store = Store::at(state_path()?, true)?.ok_or_else(|| anyhow!("absent"))?;
        store.attach(name, secret, replace)
    })()
    .map_err(storage_error)
}

fn report(name: &str, source: &str, value: Option<&str>) -> Value {
    let valid = value.is_some_and(crate::judge::safe_token);
    json!({"key_env":name, "source":source, "syntax_valid":valid,
        "fingerprint":if valid { value.map(|v| crate::sha256_hex(v.as_bytes())[..12].to_owned()) } else { None },
        "fingerprint_algorithm":"sha256-prefix-12", "storage_backend":"owner_only_plaintext_file",
        "storage_supported":storage_available(), "provider_checked":false,
        "incomplete_attachment":null})
}

/// Explicit local status only. Missing storage does not cause creation. A present
/// environment override avoids even opening the lower-precedence attached file.
pub fn status(name: &str) -> Result<Value> {
    let name = checked_name(name)?;
    match env::var(name) {
        Ok(value) => Ok(report(name, "environment", Some(&value))),
        Err(env::VarError::NotUnicode(_)) => Ok(report(name, "environment", None)),
        Err(env::VarError::NotPresent) if !storage_available() => {
            Ok(report(name, "unsupported_storage", None))
        }
        Err(env::VarError::NotPresent) => (|| {
            let Some(store) = Store::at(state_path()?, false)? else {
                return Ok(report(name, "absent", None));
            };
            let mut result = match store.read(name)? {
                Some(value) => report(name, "attached_file", Some(&value)),
                None => report(name, "absent", None),
            };
            result["incomplete_attachment"] = json!(!store.staging(name)?.is_empty());
            Ok(result)
        })()
        .map_err(storage_error),
    }
}

pub fn detach(name: &str) -> Result<bool> {
    let name = checked_name(name)?;
    (|| {
        let Some(store) = Store::at(state_path()?, false)? else {
            return Ok(false);
        };
        store.detach(name)
    })()
    .map_err(storage_error)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn names_and_fingerprints_are_stable_without_storage_or_credentials() {
        for name in ["TYPESAFE_API_KEY", "Mixed_Case9", "_"] {
            assert!(checked_name(name).is_ok())
        }
        for name in ["", "9START", "../KEY", "bad-name", "é"] {
            assert!(checked_name(name).is_err())
        }
        assert!(checked_name(&"A".repeat(256)).is_ok());
        assert!(checked_name(&"A".repeat(257)).is_err());
        let result = report("TEST", "environment", Some("abc"));
        assert_eq!(result["fingerprint"], "ba7816bf8f01");
        assert_eq!(
            report("TEST", "environment", Some("bad value"))["fingerprint"],
            Value::Null
        );
    }
    #[test]
    fn known_key_shape_redaction_does_not_access_credentials() {
        let raw = "before apikey_SYNTHETIC_0123456789 after apikey_TEST_abcdef";
        assert_eq!(
            crate::judge::redact_typesafe_keys(raw),
            "before [REDACTED_TYPESAFE_KEY] after [REDACTED_TYPESAFE_KEY]"
        );
        assert_eq!(
            crate::judge::redact_typesafe_keys("ordinary text"),
            "ordinary text"
        );
    }
}
