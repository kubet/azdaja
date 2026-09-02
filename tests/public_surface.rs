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
        ".github/ISSUE_TEMPLATE/first-use-feedback.yml",
        ".github/ISSUE_TEMPLATE/product-defect.yml",
        "site/index.html",
        "site/proof.html",
        "site/saga.html",
        "docs/launch-package.md",
        "docs/launch-saga.md",
        "release/show-hn-v0.1.13.md",
        "release/show-hn-v0.1.14.md",
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
    assert!(site.contains("The suite returned <strong>3/3 exact</strong>"));
    assert!(site.contains("three provider calls, three local Monty executions, and zero recursive or semantic subcalls"));
    assert!(site.contains("href=\"/proof.html\""));
    assert!(
        site.contains(
            "https://github.com/kubet/azdaja/blob/main/bench/results/live-fable-suite.json"
        )
    );
    assert!(site.contains("macOS 11+ on Apple Silicon and Intel"));
    assert!(site.contains("THIRD-PARTY-NOTICES.md\">third-party notices</a>"));

    let proof = read_public_surface(root, "site/proof.html");
    assert!(proof.contains("The suite returned <strong>3/3 exact</strong>"));
    assert!(
        proof.contains("contains neither its expected answer nor its answer-specific constant")
    );
    assert!(proof.contains("rejects altered totals"));
    assert!(proof.contains("not a benchmark, leaderboard result, or superiority claim"));
    assert!(
        proof.contains(
            "https://github.com/kubet/azdaja/blob/main/bench/results/live-fable-suite.json"
        )
    );
    assert!(
        proof
            .contains("https://github.com/kubet/azdaja/blob/main/bench/live_fable_suite/README.md")
    );

    let receipt: serde_json::Value = serde_json::from_str(&read_public_surface(
        root,
        "bench/results/live-fable-suite.json",
    ))
    .unwrap();
    let source_commit = receipt["source"]["commit"].as_str().unwrap();
    let benchmarks = read_public_surface(root, "BENCHMARKS.md");
    assert!(proof.contains(source_commit));
    assert!(benchmarks.contains(source_commit));
    for scenario in receipt["scenarios"].as_array().unwrap() {
        let provider_seconds = scenario["transport"]["elapsed_seconds"].as_f64().unwrap();
        let displayed = format!("{provider_seconds:.3} s");
        assert!(proof.contains(&displayed));
        assert!(benchmarks.contains(&displayed));
    }

    let styles = read_public_surface(root, "site/styles.css");
    assert!(styles.contains("font-size:clamp(1.65rem,3.5vw,2.1rem)"));
    assert!(styles.contains("font-size:clamp(1rem,1.5vw,1.08rem)"));
    assert!(styles.contains("overflow-wrap:anywhere"));

    let readme = read_public_surface(root, "README.md");
    assert!(readme.contains(
        "Azdaja keeps complete source material in a local evaluator and gives language models a bounded working surface"
    ));
    assert!(readme.contains("[Live proof](https://azdaja.dev/proof.html)"));
    assert!(!readme.contains("site/demo-50mb.gif"));

    let launch = read_public_surface(root, "docs/launch-package.md");
    assert!(launch.contains("- Repository: <https://github.com/kubet/azdaja>\n- Release: <https://github.com/kubet/azdaja/releases/tag/v0.1.14>\n- Receipts and reproduction material: <https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md>\n- Installer documentation: [install.md](install.md)\n- Historical launch record: [launch-saga.md](launch-saga.md)"));
    assert!(launch.contains("Hacker News wording must be independently written and proofread by a human. Agents may verify public URLs and external factual state only. No content in this receipt authorizes posting, replying, emailing, submitting forms, requesting votes, or running paid inference."));

    let show_hn = read_public_surface(root, "release/show-hn-v0.1.14.md");
    assert!(show_hn.contains("Status: prepared only."));
    assert!(show_hn.contains("v0.1.14"));
    assert!(show_hn.contains("## Human-only drafting boundary"));
    assert!(show_hn.contains("Never ask for votes, comments, reposts, or coordinated engagement."));
    assert!(show_hn.contains("https://azdaja.dev/op-4.html"));
    assert!(show_hn.contains("https://github.com/kubet/azdaja/releases/tag/v0.1.14"));
}

#[test]
fn public_site_exposes_machine_readable_search_metadata() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));

    let site = read_public_surface(root, "site/index.html");
    assert_eq!(site.matches("application/ld+json").count(), 1);
    for field in [
        "\"@type\": \"SoftwareApplication\"",
        "\"url\": \"https://azdaja.dev/\"",
        "\"softwareVersion\": \"0.1.14\"",
        "\"downloadUrl\": \"https://github.com/kubet/azdaja/releases/tag/v0.1.14\"",
        "\"codeRepository\": \"https://github.com/kubet/azdaja\"",
    ] {
        assert!(site.contains(field), "site metadata is missing {field}");
    }

    for (relative, headline, url) in [
        (
            "site/proof.html",
            "Three exact results, one bounded interface",
            "https://azdaja.dev/proof.html",
        ),
        (
            "site/saga.html",
            "The zero that changed Azdaja",
            "https://azdaja.dev/saga.html",
        ),
        (
            "site/op-4.html",
            "Five ways our own scorer tried to lie to us",
            "https://azdaja.dev/op-4.html",
        ),
    ] {
        let article = read_public_surface(root, relative);
        assert_eq!(article.matches("application/ld+json").count(), 1);
        assert!(article.contains("\"@type\": \"TechArticle\""));
        assert!(article.contains(&format!("\"headline\": \"{headline}\"")));
        assert!(article.contains(&format!("\"url\": \"{url}\"")));
        assert!(article.contains("\"isPartOf\": {"));
    }

    let sitemap = read_public_surface(root, "site/sitemap.xml");
    assert!(sitemap.starts_with("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"));
    assert!(sitemap.contains("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"));
    assert_eq!(sitemap.matches("<url>").count(), 4);
    assert_eq!(sitemap.matches("<loc>").count(), 4);
    for url in [
        "https://azdaja.dev/",
        "https://azdaja.dev/proof.html",
        "https://azdaja.dev/saga.html",
        "https://azdaja.dev/op-4.html",
    ] {
        assert_eq!(sitemap.matches(&format!("<loc>{url}</loc>")).count(), 1);
    }
    assert!(sitemap.trim_end().ends_with("</urlset>"));

    let robots = read_public_surface(root, "site/robots.txt");
    assert!(robots.contains("Sitemap: https://azdaja.dev/sitemap.xml"));

    let vercel = read_public_surface(root, "site/vercel.json");
    assert!(vercel.contains(r#""cleanUrls": true"#));
    assert!(
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("site/proof.html")
            .is_file()
    );
}
