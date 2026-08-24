//! Deterministic, bounded repository-to-JSON bundling for future `az solo --repo` wiring.
//!
//! The builder deliberately uses only crate dependencies plus the standard library so this
//! module can be compiled and tested in isolation. Git worktrees are enumerated through Git so
//! ignored untracked files are never candidates; other directories use a bounded filesystem walk.
//! Directory exclusions are pruned without inspecting their contents. `skipped_files` counts
//! individual non-directory entries that were encountered but not included, including symlinks,
//! special files, credential-shaped files, non-UTF-8 paths, and non-UTF-8 contents.

use anyhow::{Context, Result, anyhow, bail};
use serde::Serialize;
use std::{
    ffi::OsString,
    fs::{self, File, OpenOptions},
    io::Read,
    path::{Component, Path, PathBuf},
    process::Command,
};

/// Bundle schema version emitted in the top-level `version` field.
pub const REPO_BUNDLE_VERSION: u32 = 1;
/// Maximum number of UTF-8 files included in one bundle.
pub const MAX_INCLUDED_FILES: usize = 4_096;
/// Maximum raw byte length of one candidate file.
pub const MAX_FILE_BYTES: usize = 8 * 1024 * 1024;
/// Maximum sum of raw UTF-8 source bytes included in one bundle.
pub const MAX_TOTAL_SOURCE_BYTES: usize = 32 * 1024 * 1024;

/// Prompt guidance for a model receiving the encoded bundle as `ctx`.
pub const REPO_BUNDLE_PROMPT_NOTE: &str = "`ctx` is JSON: parse it, require version 1, then read `files` in order; each item has a slash-normalized relative `path` and UTF-8 `text`.";

/// A ready-to-load repository bundle and its source accounting.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RepoBundle {
    /// Compact, deterministic JSON with schema `{ "version": 1, "files": [...] }`.
    pub text: String,
    /// Number of entries in the encoded `files` array.
    pub included_files: usize,
    /// Number of encountered non-directory entries omitted from the bundle.
    pub skipped_files: usize,
    /// Sum of the original UTF-8 byte lengths, before JSON escaping or framing.
    pub raw_source_bytes: usize,
    /// Concise instructions for parsing this bundle when it is loaded as `ctx`.
    pub prompt_note: &'static str,
}

#[derive(Debug, Clone, Copy)]
struct Limits {
    max_files: usize,
    max_file_bytes: usize,
    max_total_bytes: usize,
}

const PRODUCTION_LIMITS: Limits = Limits {
    max_files: MAX_INCLUDED_FILES,
    max_file_bytes: MAX_FILE_BYTES,
    max_total_bytes: MAX_TOTAL_SOURCE_BYTES,
};

#[derive(Debug)]
struct Candidate {
    absolute_path: PathBuf,
    relative_path: String,
}

#[derive(Debug, Serialize)]
struct BundleFile {
    path: String,
    text: String,
}

#[derive(Serialize)]
struct EncodedBundle<'a> {
    version: u32,
    files: &'a [BundleFile],
}

/// Build a deterministic, bounded JSON bundle from `root`.
///
/// `root` must be an actual directory rather than a symlink to one. Symlinks below the root are
/// skipped and never opened. Excluded directories are not traversed. Candidate files must remain
/// regular files when opened, must contain valid UTF-8, and must fit all configured safety caps.
/// Limit violations return actionable errors instead of returning a partial bundle.
pub fn build_repo_bundle(root: impl AsRef<Path>) -> Result<RepoBundle> {
    build_repo_bundle_with_limits(root.as_ref(), PRODUCTION_LIMITS)
}

fn build_repo_bundle_with_limits(root: &Path, limits: Limits) -> Result<RepoBundle> {
    validate_limits(limits)?;
    validate_root(root)?;

    let (mut candidates, mut skipped_files) = collect_candidates(root)?;
    candidates.sort_unstable_by(|left, right| left.relative_path.cmp(&right.relative_path));

    let mut files = Vec::new();
    let mut raw_source_bytes = 0usize;

    for candidate in candidates {
        let Some(mut file) = open_regular_file_without_following(&candidate.absolute_path)
            .with_context(|| {
                format!(
                    "cannot safely open repository file {}",
                    candidate.relative_path
                )
            })?
        else {
            increment_skipped(&mut skipped_files)?;
            continue;
        };

        let metadata = file.metadata().with_context(|| {
            format!(
                "cannot inspect open repository file {}",
                candidate.relative_path
            )
        })?;
        let declared_len = usize::try_from(metadata.len()).unwrap_or(usize::MAX);
        if declared_len > limits.max_file_bytes {
            bail!(
                "repository file exceeds the {} byte per-file limit: {} ({} bytes); remove, exclude, or reduce this file",
                limits.max_file_bytes,
                candidate.relative_path,
                metadata.len()
            );
        }

        let read_limit = limits
            .max_file_bytes
            .checked_add(1)
            .ok_or_else(|| anyhow!("repository per-file limit is too large"))?;
        let mut bytes = Vec::with_capacity(declared_len.min(limits.max_file_bytes));
        file.by_ref()
            .take(read_limit as u64)
            .read_to_end(&mut bytes)
            .with_context(|| format!("cannot read repository file {}", candidate.relative_path))?;
        if bytes.len() > limits.max_file_bytes {
            bail!(
                "repository file exceeds the {} byte per-file limit while being read: {}; remove, exclude, or reduce this file",
                limits.max_file_bytes,
                candidate.relative_path
            );
        }

        let after = file.metadata().with_context(|| {
            format!(
                "cannot re-check repository file {}",
                candidate.relative_path
            )
        })?;
        if !after.file_type().is_file()
            || after.len() != metadata.len()
            || bytes.len() as u64 != after.len()
        {
            bail!(
                "repository file changed while bundling: {}; retry when the repository is stable",
                candidate.relative_path
            );
        }

        let Ok(text) = String::from_utf8(bytes) else {
            increment_skipped(&mut skipped_files)?;
            continue;
        };

        if files.len() == limits.max_files {
            bail!(
                "repository bundle exceeds the {} included-file limit at {}; exclude files or choose a narrower repository",
                limits.max_files,
                candidate.relative_path
            );
        }

        let next_total = raw_source_bytes
            .checked_add(text.len())
            .ok_or_else(|| anyhow!("repository source byte count overflow"))?;
        if next_total > limits.max_total_bytes {
            bail!(
                "repository bundle exceeds the {} byte total UTF-8 source limit at {} (would total {} bytes); exclude files or choose a narrower repository",
                limits.max_total_bytes,
                candidate.relative_path,
                next_total
            );
        }

        raw_source_bytes = next_total;
        files.push(BundleFile {
            path: candidate.relative_path,
            text,
        });
    }

    let included_files = files.len();
    let text = serde_json::to_string(&EncodedBundle {
        version: REPO_BUNDLE_VERSION,
        files: &files,
    })
    .context("cannot encode repository bundle as JSON")?;

    Ok(RepoBundle {
        text,
        included_files,
        skipped_files,
        raw_source_bytes,
        prompt_note: REPO_BUNDLE_PROMPT_NOTE,
    })
}

fn validate_limits(limits: Limits) -> Result<()> {
    if limits.max_files == 0 {
        bail!("repository included-file limit must be positive");
    }
    if limits.max_file_bytes == 0 {
        bail!("repository per-file byte limit must be positive");
    }
    if limits.max_total_bytes == 0 {
        bail!("repository total source byte limit must be positive");
    }
    Ok(())
}

fn validate_root(root: &Path) -> Result<()> {
    let metadata = fs::symlink_metadata(root)
        .with_context(|| format!("cannot inspect repository root {}", root.display()))?;
    if metadata.file_type().is_symlink() {
        bail!("repository root must not be a symlink: {}", root.display());
    }
    if !metadata.file_type().is_dir() {
        bail!("repository root must be a directory: {}", root.display());
    }
    Ok(())
}

fn collect_candidates(root: &Path) -> Result<(Vec<Candidate>, usize)> {
    let git_metadata_present = git_metadata_present(root)?;
    let git_probe = Command::new("git")
        .args(["rev-parse", "--is-inside-work-tree"])
        .current_dir(root)
        .output();

    match git_probe {
        Ok(output)
            if output.status.success()
                && String::from_utf8_lossy(&output.stdout).trim() == "true" =>
        {
            collect_git_candidates(root)
        }
        Ok(output) if git_metadata_present => {
            let detail = command_failure_detail(&output.stderr);
            bail!(
                "Git metadata is present but the repository worktree could not be verified{detail}; refusing filesystem fallback"
            );
        }
        Err(error) if git_metadata_present => bail!(
            "Git metadata is present but Git could not be started to verify the repository worktree: {error}; refusing filesystem fallback"
        ),
        Ok(_) | Err(_) => collect_filesystem_candidates(root),
    }
}

fn git_metadata_present(root: &Path) -> Result<bool> {
    let absolute_root = if root.is_absolute() {
        root.to_path_buf()
    } else {
        std::env::current_dir()
            .context("cannot determine the current directory while checking Git metadata")?
            .join(root)
    };

    for ancestor in absolute_root.ancestors() {
        match fs::symlink_metadata(ancestor.join(".git")) {
            Ok(_) => return Ok(true),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => {
                return Err(error).with_context(|| {
                    format!(
                        "cannot inspect Git metadata boundary at {}",
                        ancestor.join(".git").display()
                    )
                });
            }
        }
    }
    Ok(false)
}

fn collect_git_candidates(root: &Path) -> Result<(Vec<Candidate>, usize)> {
    let output = Command::new("git")
        .args([
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            ".",
        ])
        .current_dir(root)
        .output()
        .context("cannot start Git to enumerate repository files")?;
    if !output.status.success() {
        let detail = command_failure_detail(&output.stderr);
        bail!(
            "cannot enumerate Git worktree files with git ls-files{detail}; refusing filesystem fallback"
        );
    }
    if !output.stdout.is_empty() && !output.stdout.ends_with(&[0]) {
        bail!("git ls-files returned malformed non-NUL-terminated output");
    }

    let mut candidates = Vec::new();
    let mut skipped_files = 0usize;
    if output.stdout.is_empty() {
        return Ok((candidates, skipped_files));
    }
    let path_bytes = output
        .stdout
        .strip_suffix(&[0])
        .expect("non-empty git ls-files output was checked for NUL termination");
    for raw_path in path_bytes.split(|byte| *byte == 0) {
        if raw_path.is_empty() {
            bail!("git ls-files returned an empty repository path");
        }
        let Ok(path_text) = std::str::from_utf8(raw_path) else {
            increment_skipped(&mut skipped_files)?;
            continue;
        };
        let Some(relative_path) = normalize_relative_path(Path::new(path_text))? else {
            increment_skipped(&mut skipped_files)?;
            continue;
        };
        let relative_path_buf = PathBuf::from(&relative_path);
        if has_excluded_parent_directory(&relative_path_buf) {
            continue;
        }
        let Some(name) = relative_path_buf.file_name().and_then(|name| name.to_str()) else {
            increment_skipped(&mut skipped_files)?;
            continue;
        };
        if is_credential_shaped_file(name)
            || !is_safe_regular_candidate(root, &relative_path_buf).with_context(|| {
                format!("cannot safely inspect Git repository entry {relative_path}")
            })?
        {
            increment_skipped(&mut skipped_files)?;
            continue;
        }
        candidates.push(Candidate {
            absolute_path: root.join(&relative_path_buf),
            relative_path,
        });
    }

    candidates.sort_unstable_by(|left, right| left.relative_path.cmp(&right.relative_path));
    if candidates
        .windows(2)
        .any(|pair| pair[0].relative_path == pair[1].relative_path)
    {
        bail!("git ls-files returned a duplicate repository path");
    }
    Ok((candidates, skipped_files))
}

fn command_failure_detail(stderr: &[u8]) -> String {
    let stderr = String::from_utf8_lossy(stderr);
    let stderr = stderr.trim();
    if stderr.is_empty() {
        String::new()
    } else {
        format!(": {stderr}")
    }
}

fn has_excluded_parent_directory(path: &Path) -> bool {
    path.parent().is_some_and(|parent| {
        parent.components().any(|component| {
            let Component::Normal(name) = component else {
                return false;
            };
            name.to_str().is_some_and(is_excluded_directory)
        })
    })
}

fn is_safe_regular_candidate(root: &Path, relative_path: &Path) -> Result<bool> {
    let components = relative_path.components().collect::<Vec<_>>();
    let mut current = root.to_path_buf();
    for (index, component) in components.iter().enumerate() {
        let Component::Normal(component) = component else {
            bail!("Git repository enumeration produced a non-relative path");
        };
        current.push(component);
        let metadata = match fs::symlink_metadata(&current) {
            Ok(metadata) => metadata,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
            Err(error) => return Err(error.into()),
        };
        if metadata.file_type().is_symlink() {
            return Ok(false);
        }
        let is_last = index + 1 == components.len();
        if (is_last && !metadata.file_type().is_file())
            || (!is_last && !metadata.file_type().is_dir())
        {
            return Ok(false);
        }
    }
    Ok(!components.is_empty())
}

fn collect_filesystem_candidates(root: &Path) -> Result<(Vec<Candidate>, usize)> {
    let mut candidates = Vec::new();
    let mut skipped_files = 0usize;
    let mut pending_directories = vec![PathBuf::new()];

    while let Some(relative_directory) = pending_directories.pop() {
        let absolute_directory = root.join(&relative_directory);
        let directory_metadata = fs::symlink_metadata(&absolute_directory).with_context(|| {
            format!(
                "cannot inspect repository directory {}",
                display_relative(&relative_directory)
            )
        })?;
        if directory_metadata.file_type().is_symlink() || !directory_metadata.file_type().is_dir() {
            increment_skipped(&mut skipped_files)?;
            continue;
        }

        let mut entries = fs::read_dir(&absolute_directory)
            .with_context(|| {
                format!(
                    "cannot read repository directory {}",
                    display_relative(&relative_directory)
                )
            })?
            .collect::<std::io::Result<Vec<_>>>()
            .with_context(|| {
                format!(
                    "cannot enumerate repository directory {}",
                    display_relative(&relative_directory)
                )
            })?;
        entries.sort_unstable_by_key(|entry| entry.file_name());

        let mut child_directories = Vec::new();
        for entry in entries {
            let name: OsString = entry.file_name();
            let relative_path = relative_directory.join(&name);
            let absolute_path = entry.path();
            let metadata = fs::symlink_metadata(&absolute_path).with_context(|| {
                format!(
                    "cannot inspect repository entry {}",
                    display_relative(&relative_path)
                )
            })?;

            if metadata.file_type().is_symlink() {
                increment_skipped(&mut skipped_files)?;
                continue;
            }

            if metadata.file_type().is_dir() {
                let Some(name_utf8) = name.to_str() else {
                    // The directory cannot contribute representable relative paths. Prune it
                    // without pretending its uninspected contents are individual skipped files.
                    continue;
                };
                if !is_excluded_directory(name_utf8) {
                    child_directories.push(relative_path);
                }
                continue;
            }

            let Some(name_utf8) = name.to_str() else {
                increment_skipped(&mut skipped_files)?;
                continue;
            };

            if !metadata.file_type().is_file() || is_credential_shaped_file(name_utf8) {
                increment_skipped(&mut skipped_files)?;
                continue;
            }

            let Some(relative_path) = normalize_relative_path(&relative_path)? else {
                increment_skipped(&mut skipped_files)?;
                continue;
            };
            candidates.push(Candidate {
                absolute_path,
                relative_path,
            });
        }

        // Reverse the sorted children because this is a LIFO worklist. Candidate output receives
        // a final full-path sort, while deterministic traversal keeps error selection stable too.
        for child in child_directories.into_iter().rev() {
            pending_directories.push(child);
        }
    }

    Ok((candidates, skipped_files))
}

fn display_relative(path: &Path) -> String {
    if path.as_os_str().is_empty() {
        ".".to_owned()
    } else {
        path.to_string_lossy().into_owned()
    }
}

fn normalize_relative_path(path: &Path) -> Result<Option<String>> {
    let mut normalized = String::new();
    for component in path.components() {
        let Component::Normal(component) = component else {
            bail!("repository traversal produced a non-relative path");
        };
        let Some(component) = component.to_str() else {
            return Ok(None);
        };
        if !normalized.is_empty() {
            normalized.push('/');
        }
        normalized.push_str(component);
    }
    if normalized.is_empty() {
        bail!("repository traversal produced an empty file path");
    }
    Ok(Some(normalized))
}

fn is_excluded_directory(name: &str) -> bool {
    let lower = name.to_ascii_lowercase();
    matches!(
        lower.as_str(),
        ".git"
            | ".hg"
            | ".svn"
            | "target"
            | "node_modules"
            | "build"
            | "dist"
            | "out"
            | "coverage"
            | ".cache"
            | "cache"
            | "__pycache__"
            | ".pytest_cache"
            | ".mypy_cache"
            | ".ruff_cache"
            | ".tox"
            | ".nox"
            | ".venv"
            | "venv"
            | "virtualenv"
            | "env"
            | ".direnv"
            | ".next"
            | ".nuxt"
            | ".turbo"
            | ".parcel-cache"
            | ".gradle"
            | "cmakefiles"
            | "deriveddata"
    ) || lower.starts_with("bazel-")
}

fn is_credential_shaped_file(name: &str) -> bool {
    let lower = name.to_ascii_lowercase();
    if lower.starts_with(".env") {
        return true;
    }

    let extension_is_secret = Path::new(&lower)
        .extension()
        .and_then(|extension| extension.to_str())
        .is_some_and(|extension| matches!(extension, "pem" | "key" | "p12" | "pfx"));
    extension_is_secret
        || matches!(
            lower.as_str(),
            "id_rsa"
                | "id_ed25519"
                | "id_dsa"
                | "id_ecdsa"
                | ".netrc"
                | ".npmrc"
                | ".pypirc"
                | "credentials.json"
                | "secrets.json"
                | "service-account.json"
        )
}

fn increment_skipped(skipped: &mut usize) -> Result<()> {
    *skipped = skipped
        .checked_add(1)
        .ok_or_else(|| anyhow!("repository skipped-file count overflow"))?;
    Ok(())
}

fn open_regular_file_without_following(path: &Path) -> Result<Option<File>> {
    let path_metadata = fs::symlink_metadata(path)
        .with_context(|| format!("cannot inspect repository file {}", path.display()))?;
    if path_metadata.file_type().is_symlink() || !path_metadata.file_type().is_file() {
        return Ok(None);
    }

    let mut options = OpenOptions::new();
    options.read(true);
    configure_no_follow(&mut options);
    let file = options.open(path).with_context(|| {
        format!(
            "cannot open repository file {} without following links",
            path.display()
        )
    })?;
    let open_metadata = file
        .metadata()
        .with_context(|| format!("cannot inspect open repository file {}", path.display()))?;
    if !open_metadata.file_type().is_file() {
        return Ok(None);
    }
    if !metadata_matches(&path_metadata, &open_metadata) {
        bail!(
            "repository file identity changed before it could be read: {}; retry when the repository is stable",
            path.display()
        );
    }
    Ok(Some(file))
}

#[cfg(unix)]
fn configure_no_follow(options: &mut OpenOptions) {
    use std::os::unix::fs::OpenOptionsExt;
    options.custom_flags(libc::O_CLOEXEC | libc::O_NOFOLLOW);
}

#[cfg(windows)]
fn configure_no_follow(options: &mut OpenOptions) {
    use std::os::windows::fs::OpenOptionsExt;
    const FILE_FLAG_OPEN_REPARSE_POINT: u32 = 0x0020_0000;
    options.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT);
}

#[cfg(not(any(unix, windows)))]
fn configure_no_follow(_: &mut OpenOptions) {}

#[cfg(unix)]
fn metadata_matches(path: &fs::Metadata, open: &fs::Metadata) -> bool {
    use std::os::unix::fs::MetadataExt;
    path.dev() == open.dev() && path.ino() == open.ino()
}

#[cfg(windows)]
fn metadata_matches(path: &fs::Metadata, open: &fs::Metadata) -> bool {
    use std::os::windows::fs::MetadataExt;
    path.volume_serial_number() == open.volume_serial_number()
        && path.file_index() == open.file_index()
}

#[cfg(not(any(unix, windows)))]
fn metadata_matches(_: &fs::Metadata, _: &fs::Metadata) -> bool {
    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::Value;
    use std::{
        fs,
        sync::atomic::{AtomicU64, Ordering},
        time::{SystemTime, UNIX_EPOCH},
    };

    static NEXT_TEST_DIR: AtomicU64 = AtomicU64::new(0);

    struct TestDir(PathBuf);

    impl TestDir {
        fn new(label: &str) -> Self {
            let nonce = NEXT_TEST_DIR.fetch_add(1, Ordering::Relaxed);
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock after epoch")
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "azdaja-repo-source-{label}-{}-{timestamp}-{nonce}",
                std::process::id()
            ));
            fs::create_dir(&path).expect("create test directory");
            Self(path)
        }

        fn path(&self) -> &Path {
            &self.0
        }

        fn write(&self, relative: &str, contents: impl AsRef<[u8]>) {
            let path = self.0.join(relative);
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent).expect("create file parent");
            }
            fs::write(path, contents).expect("write fixture");
        }
    }

    impl Drop for TestDir {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn parsed_files(bundle: &RepoBundle) -> Vec<(String, String)> {
        let value: Value = serde_json::from_str(&bundle.text).expect("valid bundle JSON");
        assert_eq!(value["version"], REPO_BUNDLE_VERSION);
        value["files"]
            .as_array()
            .expect("files array")
            .iter()
            .map(|file| {
                (
                    file["path"].as_str().expect("string path").to_owned(),
                    file["text"].as_str().expect("string text").to_owned(),
                )
            })
            .collect()
    }

    fn git(root: &TestDir, args: &[&str]) {
        let output = Command::new("git")
            .args(args)
            .current_dir(root.path())
            .output()
            .expect("run git fixture command");
        assert!(
            output.status.success(),
            "git {args:?} failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }

    #[test]
    fn output_is_deterministic_and_sorted_by_normalized_relative_path() {
        let root = TestDir::new("order");
        root.write("z-last.txt", "z");
        root.write("a-dir/z.txt", "az");
        root.write("a-dir/a.txt", "aa");
        root.write("a-file.txt", "a");

        let first = build_repo_bundle(root.path()).expect("first bundle");
        let second = build_repo_bundle(root.path()).expect("second bundle");
        assert_eq!(first, second);
        assert_eq!(
            parsed_files(&first),
            [
                ("a-dir/a.txt".to_owned(), "aa".to_owned()),
                ("a-dir/z.txt".to_owned(), "az".to_owned()),
                ("a-file.txt".to_owned(), "a".to_owned()),
                ("z-last.txt".to_owned(), "z".to_owned()),
            ]
        );
        assert_eq!(first.included_files, 4);
        assert_eq!(first.raw_source_bytes, 6);
        assert_eq!(first.prompt_note, REPO_BUNDLE_PROMPT_NOTE);
    }

    #[test]
    fn excludes_build_cache_venv_and_credential_shapes() {
        let root = TestDir::new("exclusions");
        root.write("src/main.rs", "safe");
        for path in [
            ".hg/config",
            "target/debug/app",
            "node_modules/pkg/index.js",
            "build/generated.c",
            ".cache/item",
            ".venv/bin/python",
            "__pycache__/mod.pyc",
        ] {
            root.write(path, "excluded directory content");
        }
        for path in [
            ".env",
            ".env.production",
            "server.PEM",
            "signing.key",
            "id_rsa",
            "id_ed25519",
            "credentials.json",
        ] {
            root.write(path, "secret");
        }

        let bundle = build_repo_bundle(root.path()).expect("bundle");
        assert_eq!(
            parsed_files(&bundle),
            [("src/main.rs".to_owned(), "safe".to_owned())]
        );
        assert_eq!(bundle.included_files, 1);
        assert_eq!(bundle.skipped_files, 7);
        assert!(!bundle.text.contains("secret"));
        assert!(!bundle.text.contains("excluded directory content"));
    }

    #[test]
    fn git_worktree_excludes_ignored_secrets_and_includes_tracked_and_nonignored_files() {
        let root = TestDir::new("git-ignore-boundary");
        git(&root, &["init", "--quiet"]);
        root.write(".gitignore", "secrets.yaml\ncredentials.toml\n*.tfvars\n");
        root.write("tracked.txt", "tracked");
        root.write("src/nonignored.rs", "nonignored");
        root.write("z-untracked.txt", "untracked");
        root.write("secrets.yaml", "ignored-secret-yaml");
        root.write("credentials.toml", "ignored-credentials-toml");
        root.write("infra/production.tfvars", "ignored-terraform-secret");
        root.write("credentials.json", "common-credential-exclusion");
        git(&root, &["add", ".gitignore", "tracked.txt"]);

        let first = build_repo_bundle(root.path()).expect("first Git-aware bundle");
        let second = build_repo_bundle(root.path()).expect("second Git-aware bundle");
        assert_eq!(first, second);
        assert_eq!(
            parsed_files(&first),
            [
                (
                    ".gitignore".to_owned(),
                    "secrets.yaml\ncredentials.toml\n*.tfvars\n".to_owned()
                ),
                ("src/nonignored.rs".to_owned(), "nonignored".to_owned()),
                ("tracked.txt".to_owned(), "tracked".to_owned()),
                ("z-untracked.txt".to_owned(), "untracked".to_owned()),
            ]
        );
        let included_paths = parsed_files(&first)
            .into_iter()
            .map(|(path, _)| path)
            .collect::<Vec<_>>();
        assert!(!included_paths.iter().any(|path| path == "secrets.yaml"));
        assert!(!included_paths.iter().any(|path| path == "credentials.toml"));
        assert!(!included_paths.iter().any(|path| path.ends_with(".tfvars")));
        assert!(!included_paths.iter().any(|path| path == "credentials.json"));
    }

    #[test]
    fn git_worktree_enumeration_failure_is_fail_closed() {
        let root = TestDir::new("git-enumeration-failure");
        git(&root, &["init", "--quiet"]);
        root.write("safe.txt", "must not be returned through fallback");
        root.write(".git/index", "not a valid Git index");

        let error = build_repo_bundle(root.path()).expect_err("broken Git index must fail closed");
        assert!(
            error
                .to_string()
                .contains("cannot enumerate Git worktree files with git ls-files")
        );
        assert!(error.to_string().contains("refusing filesystem fallback"));
    }

    #[cfg(unix)]
    #[test]
    fn rejects_symlink_root_and_skips_nested_symlinks_without_target_leakage() {
        use std::os::unix::fs::symlink;

        let actual = TestDir::new("actual-root");
        git(&actual, &["init", "--quiet"]);
        actual.write("safe.txt", "safe");
        let link_parent = TestDir::new("root-link-parent");
        let root_link = link_parent.path().join("repo-link");
        symlink(actual.path(), &root_link).expect("create root symlink");
        let error = build_repo_bundle(&root_link).expect_err("symlink root rejected");
        assert!(error.to_string().contains("must not be a symlink"));

        let outside = TestDir::new("outside");
        outside.write("secret.txt", "outside-secret-marker");
        symlink(
            outside.path().join("secret.txt"),
            actual.path().join("linked-file"),
        )
        .expect("create file symlink");
        symlink(outside.path(), actual.path().join("linked-directory"))
            .expect("create directory symlink");

        let bundle = build_repo_bundle(actual.path()).expect("bundle with nested symlinks");
        assert_eq!(
            parsed_files(&bundle),
            [("safe.txt".to_owned(), "safe".to_owned())]
        );
        assert_eq!(bundle.skipped_files, 2);
        assert!(!bundle.text.contains("outside-secret-marker"));
        assert!(
            !bundle
                .text
                .contains(outside.path().to_string_lossy().as_ref())
        );
    }

    #[test]
    fn skips_non_utf8_contents_and_counts_only_raw_included_utf8_bytes() {
        let root = TestDir::new("non-utf8");
        root.write("binary.bin", [0xff, 0xfe, 0xfd]);
        root.write("unicode.txt", "é🙂");

        let bundle = build_repo_bundle(root.path()).expect("bundle");
        assert_eq!(
            parsed_files(&bundle),
            [("unicode.txt".to_owned(), "é🙂".to_owned())]
        );
        assert_eq!(bundle.skipped_files, 1);
        assert_eq!(bundle.raw_source_bytes, "é🙂".len());
    }

    #[cfg(unix)]
    #[test]
    fn skips_non_regular_entries() {
        use std::os::unix::net::UnixListener;

        let root = TestDir::new("special");
        root.write("safe", "ok");
        let socket_path = root.path().join("service.sock");
        let _listener = UnixListener::bind(&socket_path).expect("bind Unix socket");

        let bundle = build_repo_bundle(root.path()).expect("bundle");
        assert_eq!(
            parsed_files(&bundle),
            [("safe".to_owned(), "ok".to_owned())]
        );
        assert_eq!(bundle.skipped_files, 1);
    }

    // macOS filesystems reject non-UTF-8 path components with EILSEQ before the builder can see
    // them. Other Unix filesystems generally permit arbitrary non-NUL bytes in a component.
    #[cfg(all(unix, not(any(target_os = "macos", target_os = "ios"))))]
    #[test]
    fn skips_non_utf8_paths() {
        use std::{ffi::OsStr, os::unix::ffi::OsStrExt};

        let root = TestDir::new("non-utf8-path");
        root.write("safe", "ok");
        fs::write(
            root.path().join(OsStr::from_bytes(b"bad-\xff-name")),
            b"hidden",
        )
        .expect("write non-UTF-8 path");

        let bundle = build_repo_bundle(root.path()).expect("bundle");
        assert_eq!(
            parsed_files(&bundle),
            [("safe".to_owned(), "ok".to_owned())]
        );
        assert_eq!(bundle.skipped_files, 1);
    }

    #[test]
    fn enforces_file_count_per_file_and_total_limits_without_truncation() {
        let count_root = TestDir::new("count-limit");
        count_root.write("a", "1");
        count_root.write("b", "2");
        let count_error = build_repo_bundle_with_limits(
            count_root.path(),
            Limits {
                max_files: 1,
                max_file_bytes: 8,
                max_total_bytes: 8,
            },
        )
        .expect_err("file count limit");
        assert!(
            count_error
                .to_string()
                .contains("1 included-file limit at b")
        );
        assert!(count_error.to_string().contains("exclude files"));

        let file_root = TestDir::new("file-limit");
        file_root.write("large.txt", "12345");
        let file_error = build_repo_bundle_with_limits(
            file_root.path(),
            Limits {
                max_files: 2,
                max_file_bytes: 4,
                max_total_bytes: 8,
            },
        )
        .expect_err("per-file limit");
        assert!(file_error.to_string().contains("4 byte per-file limit"));
        assert!(file_error.to_string().contains("large.txt"));
        assert!(
            file_error
                .to_string()
                .contains("remove, exclude, or reduce")
        );

        let total_root = TestDir::new("total-limit");
        total_root.write("a", "123");
        total_root.write("b", "456");
        let total_error = build_repo_bundle_with_limits(
            total_root.path(),
            Limits {
                max_files: 2,
                max_file_bytes: 8,
                max_total_bytes: 5,
            },
        )
        .expect_err("total limit");
        assert!(
            total_error
                .to_string()
                .contains("5 byte total UTF-8 source limit at b")
        );
        assert!(total_error.to_string().contains("would total 6 bytes"));
    }

    #[test]
    fn preserves_unicode_paths_uses_forward_slashes_and_leaks_no_root_path() {
        let root = TestDir::new("unicode-path");
        root.write("資料/naïve🙂.txt", "line 1\nline 2");

        let bundle = build_repo_bundle(root.path()).expect("bundle");
        assert_eq!(
            parsed_files(&bundle),
            [("資料/naïve🙂.txt".to_owned(), "line 1\nline 2".to_owned())]
        );
        assert!(!bundle.text.contains(root.path().to_string_lossy().as_ref()));
        let path = parsed_files(&bundle).remove(0).0;
        assert!(!path.starts_with('/'));
        assert!(!path.contains('\\'));
    }

    #[test]
    fn rejects_non_directory_roots_and_schema_is_compact_and_versioned() {
        let root = TestDir::new("root-kind");
        root.write("file.txt", "x");
        let error = build_repo_bundle(root.path().join("file.txt"))
            .expect_err("regular-file root rejected");
        assert!(error.to_string().contains("must be a directory"));

        let bundle = build_repo_bundle(root.path()).expect("bundle");
        assert_eq!(
            bundle.text,
            r#"{"version":1,"files":[{"path":"file.txt","text":"x"}]}"#
        );
        assert!(!bundle.text.contains("included_files"));
        assert_eq!(MAX_INCLUDED_FILES, 4_096);
        assert_eq!(MAX_FILE_BYTES, 8 * 1024 * 1024);
        assert_eq!(MAX_TOTAL_SOURCE_BYTES, 32 * 1024 * 1024);
    }
}
