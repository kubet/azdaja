use std::{fs, path::Path};

#[test]
fn v011_release_plan_is_exact_and_v010_receipts_remain_immutable() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    assert_eq!(env!("CARGO_PKG_VERSION"), "0.1.2");
    let normalizer = fs::read_to_string(root.join("release/v0.1.1/normalize-darwin.py")).unwrap();
    assert!(normalizer.contains("dev.kubet.azdaja"));
    assert!(normalizer.contains("hashlib.sha256(ASSET_NAME.encode()).digest()[:16]"));
    assert!(normalizer.contains("--timestamp=none"));
    assert!(normalizer.contains("--verify"));

    let sums = fs::read_to_string(root.join("release/v0.1.1/SHA256SUMS")).unwrap();
    assert_eq!(
        sums,
        "b58975de462e823adcf901e331acfd4e70c9e72b5db014de265c04e371d31883  azdaja-v0.1.1-darwin-arm64\n\
         b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247  azdaja-v0.1.1-linux-x86_64\n"
    );
    let entries: Vec<_> = sums.lines().collect();
    assert_eq!(entries.len(), 2);

    let old_sums = fs::read_to_string(root.join("release/v0.1.0/SHA256SUMS")).unwrap();
    assert_eq!(
        old_sums,
        "6b50716382ac35e4f2bc9fc3c1cc3db9ee059edde783b78dba21273bf626762a  azdaja-v0.1.0-darwin-arm64\n"
    );
    let old_integrity =
        fs::read_to_string(root.join("release/v0.1.0/public-release-integrity-receipt.json"))
            .unwrap();
    assert!(old_integrity.contains("021b79e76e5951dd6142b4c76e564ae41adb9504"));
    assert!(
        old_integrity.contains("6b50716382ac35e4f2bc9fc3c1cc3db9ee059edde783b78dba21273bf626762a")
    );

    let receipt: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(root.join("release/v0.1.1/prepublication-receipt.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(
        receipt["status"],
        "LOCAL_PREPUBLICATION_GATES_PASS_PUBLICATION_PENDING"
    );
    assert_eq!(
        receipt["authorization"]["internal_reviewed_go_received"],
        false
    );
    assert_eq!(
        receipt["authorization"]["push_tag_release_performed"],
        false
    );
    assert_eq!(
        receipt["binary_inputs"]["manifest_sha256"],
        "9a3984e89b773a06d2d4ba2c979ada67f4a2c628001fd7c09ab103d1a337a9b5"
    );
    assert_eq!(receipt["binary_inputs"]["files"], 10);
    let manifest = fs::read_to_string(root.join("release/v0.1.1/binary-inputs.json")).unwrap();
    assert!(manifest.contains("369f23c05288e24745a61296564e6b8d95836441ac41d1c96a4b08c521ada629"));
    let names = receipt["release_plan"]["exact_asset_name_set"]
        .as_array()
        .unwrap();
    assert_eq!(names.len(), 3);
    assert!(names.contains(&serde_json::json!("SHA256SUMS")));
    assert!(names.contains(&serde_json::json!("azdaja-v0.1.1-darwin-arm64")));
    assert!(names.contains(&serde_json::json!("azdaja-v0.1.1-linux-x86_64")));

    let site = fs::read_to_string(root.join("site/index.html")).unwrap();
    assert_eq!(site.matches("/main/site/install").count(), 1);
}

#[test]
fn workflows_are_read_only_and_have_no_release_mutation_automation() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join(".github/workflows");
    for entry in fs::read_dir(root).unwrap() {
        let path = entry.unwrap().path();
        if !matches!(
            path.extension().and_then(|s| s.to_str()),
            Some("yml" | "yaml")
        ) {
            continue;
        }
        let text = fs::read_to_string(&path).unwrap();
        assert!(
            text.contains("permissions:\n  contents: read"),
            "workflow must be contents-read-only: {}",
            path.display()
        );
        for forbidden in [
            "gh release create",
            "gh release upload",
            "softprops/action-gh-release",
            "actions/create-release",
        ] {
            assert!(
                !text.contains(forbidden),
                "release mutation automation in {}: {forbidden}",
                path.display()
            );
        }
    }
}
