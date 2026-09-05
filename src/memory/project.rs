//! Repo-local storage selection for explicitly authored project memories.
//!
//! Availability is on by default inside a Git worktree. This module never
//! extracts notes, contacts a provider, or stages anything in Git. Personal
//! global memory remains an explicit, separate store.
use anyhow::{Context, Result, bail};
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

const DIRECTORY: &str = ".azdaja";
const SWITCH: &str = "AZDAJA_PROJECT_MEMORY";
static NEXT_IGNORE: AtomicU64 = AtomicU64::new(0);

pub(super) fn current_root(global: bool, write: bool) -> Result<Option<PathBuf>> {
    if global {
        return Ok(None);
    }
    let explicit_project = match std::env::var(SWITCH) {
        Ok(value) if value == "legacy" => return Ok(None),
        Ok(value) if value == "off" => bail!("project memory is disabled by {SWITCH}=off"),
        Ok(value) if value == "on" => true,
        Ok(_) | Err(std::env::VarError::NotUnicode(_)) => {
            bail!("{SWITCH} must be on, off, or legacy")
        }
        Err(std::env::VarError::NotPresent) => false,
    };
    // Preserve the existing authoritative override unless the caller explicitly
    // selects project storage. Invalid/empty overrides retain legacy validation.
    if !explicit_project && std::env::var_os("AZDAJA_HOME").is_some() {
        return Ok(None);
    }
    let cwd = std::env::current_dir().context("cannot resolve project memory directory")?;
    let Some(repo) = find_repo(&cwd)? else {
        if explicit_project {
            bail!("explicit project memory requires a Git worktree")
        }
        return Ok(None);
    };
    legacy_notice();
    let root = repo.join(DIRECTORY);
    if write {
        create_private_directory(&root)?;
        ensure_ignored(&root)?;
    } else {
        validate_directory_if_present(&root)?;
    }
    Ok(Some(root))
}

fn legacy_notice() {
    let Ok(mut path) = super::recall::state_root_for_read() else {
        return;
    };
    for component in ["memory", "scopes"] {
        path.push(component);
        match fs::symlink_metadata(&path) {
            Ok(metadata) if metadata.is_dir() && !metadata.file_type().is_symlink() => {}
            _ => return,
        }
    }
    eprintln!(
        "note: legacy scoped storage exists and is not searched by project memory; use {SWITCH}=legacy to access the previous current-directory scope. No notes were migrated."
    );
}

pub(super) fn has_ledger(root: &Path) -> Result<bool> {
    let directory = root.join(super::MEMORY_DIR);
    validate_directory_if_present(&directory)?;
    match fs::symlink_metadata(directory.join(super::GLOBAL_LEDGER)) {
        Ok(_) => Ok(true),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
        Err(error) => Err(error).context("cannot inspect project memory ledger"),
    }
}

fn find_repo(cwd: &Path) -> Result<Option<PathBuf>> {
    let cwd = cwd
        .canonicalize()
        .context("cannot canonicalize project memory directory")?;
    for ancestor in cwd.ancestors() {
        match fs::symlink_metadata(ancestor.join(".git")) {
            Ok(metadata) if metadata.is_dir() || metadata.is_file() => {
                return Ok(Some(ancestor.to_owned()));
            }
            Ok(_) => bail!("project memory refuses a nonregular Git boundary"),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => return Err(error).context("cannot inspect project memory Git boundary"),
        }
    }
    Ok(None)
}

fn validate_directory_if_present(path: &Path) -> Result<()> {
    match fs::symlink_metadata(path) {
        Ok(metadata) => {
            if !metadata.is_dir() || metadata.file_type().is_symlink() {
                bail!("project memory directory must be a real directory")
            }
            #[cfg(unix)]
            {
                use std::os::unix::fs::{MetadataExt, PermissionsExt};
                if metadata.uid() != unsafe { libc::geteuid() }
                    || metadata.permissions().mode() & 0o077 != 0
                {
                    bail!(
                        "project memory directory must be private and owned by the current user; permissions were not changed"
                    )
                }
            }
            #[cfg(windows)]
            {
                use std::os::windows::fs::MetadataExt;
                if metadata.file_attributes() & 0x400 != 0 {
                    bail!("project memory directory must not be a reparse point")
                }
            }
            Ok(())
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error).context("cannot inspect project memory directory"),
    }
}

fn create_private_directory(path: &Path) -> Result<()> {
    let builder = fs::DirBuilder::new();
    #[cfg(unix)]
    let builder = {
        use std::os::unix::fs::DirBuilderExt;
        let mut builder = builder;
        builder.mode(0o700);
        builder
    };
    match builder.create(path) {
        Ok(()) => {}
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
        Err(error) => return Err(error).context("cannot create project memory directory"),
    }
    validate_directory_if_present(path)
}

fn ensure_ignored(root: &Path) -> Result<()> {
    let path = root.join(".gitignore");
    match fs::symlink_metadata(&path) {
        Ok(_) => return validate_ignore(&path),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => return Err(error).context("cannot inspect project memory ignore rule"),
    }
    // Publish a complete rule with no replacement. Concurrent creators must
    // never observe an empty rule or overwrite a pre-existing user file.
    let (temporary, mut file) = loop {
        let temporary = root.join(format!(
            ".ignore-init-{}-{}",
            std::process::id(),
            NEXT_IGNORE.fetch_add(1, Ordering::Relaxed)
        ));
        match create_ignore_file(&temporary) {
            Ok(file) => break (temporary, file),
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error).context("cannot prepare project memory ignore rule"),
        }
    };
    let result = (|| -> Result<()> {
        file.write_all(b"*\n")?;
        file.sync_all()?;
        match fs::hard_link(&temporary, &path) {
            Ok(()) => {}
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
            Err(error) => return Err(error).context("cannot publish project memory ignore rule"),
        }
        #[cfg(unix)]
        File::open(root)?.sync_all()?;
        validate_ignore(&path)
    })();
    drop(file);
    let cleanup = fs::remove_file(&temporary);
    result?;
    cleanup.context("cannot remove owned project memory initialization file")
}

fn create_ignore_file(path: &Path) -> std::io::Result<File> {
    let mut options = OpenOptions::new();
    options.write(true).create_new(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }
    options.open(path)
}

fn validate_ignore(path: &Path) -> Result<()> {
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.is_file() || metadata.file_type().is_symlink() {
        bail!("project memory ignore rule must be a real file")
    }
    let mut bytes = Vec::new();
    File::open(path)?.take(4).read_to_end(&mut bytes)?;
    if bytes != b"*\n" {
        bail!("project memory requires its private ignore rule; existing file was not changed")
    }
    Ok(())
}
