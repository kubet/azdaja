//! Structural CI wiring checks. These do not execute the installer or claim artifact acceptance.
const WORKFLOW: &str = include_str!("../.github/workflows/source-install-integrity.yml");
const LIST_COMMAND: &str = "          cargo +1.95.0 test --release --locked --test installed_project_memory \\\n            -- --ignored --list > \"$scratch/installed-artifact-tests\"";
const RUN_COMMAND: &str = "          AZDAJA_INSTALLED_TEST_BINARY=\"$installed\" PATH=\"$guard:$PATH\" \\\n            cargo +1.95.0 test --release --locked --test installed_project_memory \\\n            -- --ignored --test-threads=1\n          test ! -e \"$marker\"";
const HISTORICAL_NOTICE_CHECK: &str = "          cmp release/historical/THIRD-PARTY-NOTICES-pre-v0.1.17.md \"$install_home/.local/share/azdaja/THIRD-PARTY-NOTICES.md\"";

#[test]
fn source_install_ci_runs_registered_artifact_tests_against_verified_installed_bytes() {
    assert_eq!(
        WORKFLOW.matches(LIST_COMMAND).count(),
        1,
        "missing unique ignored-test registry check"
    );
    assert_eq!(
        WORKFLOW.matches(RUN_COMMAND).count(),
        1,
        "missing unique actual installed-binary test invocation"
    );
    let byte_check = WORKFLOW
        .find("          cmp \"$source_binary\" \"$installed\"")
        .unwrap();
    let legal_check = WORKFLOW
        .find(HISTORICAL_NOTICE_CHECK)
        .expect("the frozen installer must preserve the exact historical notice");
    let list = WORKFLOW.find(LIST_COMMAND).unwrap();
    let run = WORKFLOW.find(RUN_COMMAND).unwrap();
    assert!(byte_check < legal_check && legal_check < list && list < run);
    for name in [
        "installed_artifact_preserves_cross_home_handoff_and_relocation",
        "installed_artifact_refuses_disabled_writes_and_corrupt_reads_without_fallback",
    ] {
        let guard =
            format!("          grep -Fx '{name}: test' \"$scratch/installed-artifact-tests\"");
        assert_eq!(WORKFLOW.matches(&guard).count(), 1);
        let position = WORKFLOW.find(&guard).unwrap();
        assert!(list < position && position < run);
    }
    let count =
        "          test \"$(grep -c ': test$' \"$scratch/installed-artifact-tests\")\" -eq 2";
    let position = WORKFLOW
        .find(count)
        .expect("must refuse zero or unexpected registered tests");
    assert!(list < position && position < run);
    assert!(WORKFLOW.contains("          set -euo pipefail"));
    assert!(!WORKFLOW.contains("continue-on-error:"));
}

#[test]
fn source_install_ci_separates_current_notice_audit_from_frozen_installer_compatibility() {
    let stages = [
        "        run: python3 release/verify-third-party-notices.py",
        "          frozen_installer_rejects_current_unpublished_notice_even_with_matching_download_checksum",
        "          cp release/historical/THIRD-PARTY-NOTICES-pre-v0.1.17.md \"$fixture/THIRD-PARTY-NOTICES.md\"",
        "          assert hashlib.sha256((fixture / \"THIRD-PARTY-NOTICES.md\").read_bytes()).hexdigest() == \"393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d2\"",
        "            sh site/install jcode,claude --bin-dir \"$install_bin\"",
        HISTORICAL_NOTICE_CHECK,
    ];
    let mut previous = None;
    for stage in stages {
        assert_eq!(
            WORKFLOW.matches(stage).count(),
            1,
            "missing unique stage: {stage}"
        );
        let position = WORKFLOW.find(stage).unwrap();
        if let Some(previous) = previous {
            assert!(
                previous < position,
                "notice boundary stage out of order: {stage}"
            );
        }
        previous = Some(position);
    }
    assert!(WORKFLOW.contains("          -- --exact --test-threads=1"));
    assert!(!WORKFLOW.contains("cp LICENSE THIRD-PARTY-NOTICES.md"));
    assert!(!WORKFLOW.contains("cmp THIRD-PARTY-NOTICES.md \"$install_home/"));
}

#[test]
fn source_install_handoff_explicitly_activates_its_shared_session() {
    let activation = "          export AZDAJA_JCODE_ACTIVATION=session";
    let session = "          export JCODE_HOOK_SESSION_ID=source-install-ci";
    assert_eq!(WORKFLOW.matches(activation).count(), 1);
    assert_eq!(WORKFLOW.matches(session).count(), 1);
    let first_hook = WORKFLOW
        .find("              JCODE_HOOK_EVENT=pre_tool JCODE_HOOK_SESSION_ID=source-install-ci")
        .unwrap();
    assert!(WORKFLOW.find(activation).unwrap() < first_hook);
    assert!(WORKFLOW.find(session).unwrap() < first_hook);
    assert!(WORKFLOW[first_hook..].contains("          test \"$blocked_status\" -eq 2"));
}
