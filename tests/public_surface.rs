use std::{fs, path::Path};

fn read_public_surface(root: &Path, relative: &str) -> String {
    fs::read_to_string(root.join(relative))
        .unwrap_or_else(|error| panic!("failed to read {relative}: {error}"))
}

#[test]
fn public_surface_leads_with_the_product_contract_not_capacity_marketing() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let active_surfaces = [
        "README.md",
        "site/index.html",
        "site/saga.html",
        "docs/launch-package.md",
        "docs/launch-saga.md",
        "release/show-hn-v0.1.13.md",
        "release/v0.1.14.md",
    ];
    let rejected = [
        "analyze 50 mib",
        "analyse 50 mib",
        "50 mib",
        "52,428,800",
        "fifty-megabyte",
    ];

    for relative in active_surfaces {
        let text = read_public_surface(root, relative);
        let lowercase = text.to_lowercase();
        for phrase in rejected {
            assert!(
                !lowercase.contains(phrase),
                "{relative} still contains rejected capacity-led marketing: {phrase}"
            );
        }
    }

    let site = read_public_surface(root, "site/index.html");
    assert!(site.contains("<h1>Azdaja</h1>"));
    assert!(site.contains("A local evaluator for language-model context."));
    assert!(site.contains("Keep complete source material outside the root prompt."));
    assert!(site.contains("macOS 11+ on Apple Silicon and Intel"));
    assert!(site.contains("THIRD-PARTY-NOTICES.md\">third-party notices</a>"));

    let styles = read_public_surface(root, "site/styles.css");
    assert!(styles.contains("font-size:clamp(1.65rem,3.5vw,2.1rem)"));
    assert!(styles.contains("font-size:clamp(1rem,1.5vw,1.08rem)"));
    assert!(styles.contains("overflow-wrap:anywhere"));

    let readme = read_public_surface(root, "README.md");
    assert!(readme.contains(
        "Azdaja keeps complete source material in a local evaluator and gives language models a bounded working surface"
    ));
    assert!(!readme.contains("site/demo-50mb.gif"));

    let launch = read_public_surface(root, "docs/launch-package.md");
    assert!(launch.contains("Show HN: Azdaja – A local evaluator for language-model context"));
}
