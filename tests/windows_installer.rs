use std::{fs, path::Path};

#[test]
fn windows_installer_is_versioned_hashed_atomic_and_fail_closed() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let installer = fs::read_to_string(root.join("site/install.ps1")).unwrap();

    for required in [
        "azdaja-v$Version-windows-x86_64.exe",
        "SHA256SUMS must contain exactly one checksum",
        "Get-FileHash -LiteralPath $binaryPath -Algorithm SHA256",
        "checksum mismatch for $asset",
        "downloaded payload is not a PE executable",
        "downloaded payload is not Windows x86-64",
        "refusing reparse-point install path",
        "[System.IO.File]::Replace($stage, $destination, $backup, $true)",
        "remote releases require HTTPS unless the host is loopback",
        "installed binary failed the exact version probe",
    ] {
        assert!(
            installer.contains(required),
            "missing installer guard: {required}"
        );
    }

    for forbidden in [
        "Invoke-Expression",
        "Start-Process powershell",
        "ExecutionPolicy Bypass",
    ] {
        assert!(
            !installer.contains(forbidden),
            "unsafe installer primitive present: {forbidden}"
        );
    }
}

#[test]
fn windows_ci_runs_the_real_installer_and_rejects_tampering() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let ci = fs::read_to_string(root.join(".github/workflows/ci.yml")).unwrap();
    let job = ci
        .split_once("\n  windows-safety:\n")
        .expect("Windows safety job must exist")
        .1;

    for required in [
        "Validate Windows installer and tamper refusal",
        "& .\\site\\install.ps1 -ReleaseRoot $scratch -InstallDir $install -NoPathUpdate",
        "tampered Windows payload was accepted",
        "tampered Windows install published an artifact",
    ] {
        assert!(
            job.contains(required),
            "missing Windows CI acceptance: {required}"
        );
    }
}

#[test]
fn windows_installer_is_served_uncached_as_plain_text() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let headers = fs::read_to_string(root.join("site/_headers")).unwrap();
    let vercel = fs::read_to_string(root.join("site/vercel.json")).unwrap();

    assert!(headers.contains(
        "/install.ps1\n  Cache-Control: no-store\n  Content-Type: text/plain; charset=utf-8"
    ));
    assert!(vercel.contains(r#""source": "/install.ps1""#));
    assert!(vercel.contains(r#""value": "text/plain; charset=utf-8""#));
}
