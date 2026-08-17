use std::{fs, path::Path};

const PRIVACY_CONFIRMATION: &str = "I removed raw input, traces, config, host paths, OAuth material, tokens, and secrets from this report.";
const PRIVATE_ADVISORY_URL: &str = "https://github.com/kubet/azdaja/security/advisories/new";

fn canonical_body_items<'a>(text: &'a str, path: &Path) -> Vec<Vec<&'a str>> {
    let lines: Vec<_> = text.lines().collect();
    let body_positions: Vec<_> = lines
        .iter()
        .enumerate()
        .filter_map(|(index, line)| (*line == "body:").then_some(index))
        .collect();
    assert_eq!(
        body_positions.len(),
        1,
        "issue form must have one canonical top-level body: {}",
        path.display()
    );
    let body = body_positions[0];
    assert!(
        !lines[body + 1..]
            .iter()
            .any(|line| !line.is_empty() && !line.starts_with(' ')),
        "unexpected top-level content after issue-form body: {}",
        path.display()
    );

    let starts: Vec<_> = lines[body + 1..]
        .iter()
        .enumerate()
        .filter_map(|(offset, line)| line.starts_with("  - type: ").then_some(body + 1 + offset))
        .collect();
    assert!(
        !starts.is_empty(),
        "issue form has no body items: {}",
        path.display()
    );

    starts
        .iter()
        .enumerate()
        .map(|(index, start)| {
            let end = starts.get(index + 1).copied().unwrap_or(lines.len());
            lines[*start..end].to_vec()
        })
        .collect()
}

#[test]
fn public_feedback_paths_enforce_the_privacy_boundary() {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join(".github/ISSUE_TEMPLATE");
    let config = fs::read_to_string(dir.join("config.yml")).expect("read issue chooser config");
    let blank_settings: Vec<_> = config
        .lines()
        .filter(|line| line.starts_with("blank_issues_enabled:"))
        .collect();
    assert_eq!(
        blank_settings,
        ["blank_issues_enabled: false"],
        "blank public issues must stay canonically disabled at top level"
    );
    assert_eq!(
        config
            .lines()
            .filter(|line| *line == "contact_links:")
            .count(),
        1,
        "chooser must have one canonical top-level contact_links list"
    );
    let contact_lines: Vec<_> = config.lines().collect();
    let private_contact = contact_lines
        .iter()
        .position(|line| *line == "  - name: Privately report a security vulnerability")
        .expect("chooser must retain private vulnerability contact");
    let next_contact = contact_lines[private_contact + 1..]
        .iter()
        .position(|line| line.starts_with("  - name: "))
        .map(|offset| private_contact + 1 + offset)
        .unwrap_or(contact_lines.len());
    assert!(
        contact_lines[private_contact..next_contact]
            .iter()
            .any(|line| *line == format!("    url: {PRIVATE_ADVISORY_URL}")),
        "private vulnerability contact must own the advisory URL"
    );

    let mut forms = Vec::new();
    for entry in fs::read_dir(&dir).expect("read issue template directory") {
        let path = entry.expect("read issue template entry").path();
        let extension = path
            .extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or_default();
        if extension.eq_ignore_ascii_case("md") {
            panic!(
                "legacy Markdown issue template bypasses required privacy confirmation: {}",
                path.display()
            );
        }
        if !(extension.eq_ignore_ascii_case("yml") || extension.eq_ignore_ascii_case("yaml"))
            || path.file_name().and_then(|name| name.to_str()) == Some("config.yml")
        {
            continue;
        }

        let name = path
            .file_name()
            .and_then(|name| name.to_str())
            .expect("UTF-8 issue form name");
        let expected_label = match name {
            "first-use-feedback.yml" => r#"labels: ["first-use"]"#,
            "product-defect.yml" => r#"labels: ["product-defect"]"#,
            _ => panic!("unreviewed public issue form: {}", path.display()),
        };
        let text = fs::read_to_string(&path).expect("read issue form");
        let label_settings: Vec<_> = text
            .lines()
            .filter(|line| line.starts_with("labels:"))
            .collect();
        assert_eq!(
            label_settings,
            [expected_label],
            "issue form must own its exact top-level routing label: {}",
            path.display()
        );
        let items = canonical_body_items(&text, &path);
        let version_items: Vec<_> = items
            .iter()
            .filter(|item| item.contains(&"    id: version"))
            .collect();
        assert_eq!(
            version_items.len(),
            1,
            "issue form must have one version body item: {}",
            path.display()
        );
        let version = version_items[0];
        assert_eq!(
            version.first().copied(),
            Some("  - type: input"),
            "version must be an input body item: {}",
            path.display()
        );
        assert!(
            version.contains(&"      label: Azdaja version, if available"),
            "version must be optional for pre-binary install failures: {}",
            path.display()
        );
        assert!(
            version.contains(&"      description: Output of `azdaja --version` only. If installation failed before a binary existed, leave this blank."),
            "version guidance must admit a pre-binary install failure: {}",
            path.display()
        );
        assert!(
            !version.contains(&"      required: true"),
            "version cannot be required when installation produced no binary: {}",
            path.display()
        );

        if name == "first-use-feedback.yml" {
            let workload_items: Vec<_> = items
                .iter()
                .filter(|item| item.contains(&"    id: workload"))
                .collect();
            assert_eq!(
                workload_items.len(),
                1,
                "first-use form must have one workload item"
            );
            let workload = workload_items[0];
            assert_eq!(workload.first().copied(), Some("  - type: dropdown"));
            assert!(
                workload.contains(&"        - Not reached — installation or doctor failed"),
                "pre-workload failures need a truthful input-class option"
            );
            assert!(
                workload.contains(&"      required: true"),
                "workload or explicit not-reached status must remain required"
            );

            let size_items: Vec<_> = items
                .iter()
                .filter(|item| item.contains(&"    id: size"))
                .collect();
            assert_eq!(
                size_items.len(),
                1,
                "first-use form must have one input-size item"
            );
            let size = size_items[0];
            assert_eq!(size.first().copied(), Some("  - type: input"));
            assert!(size.contains(&"      label: Approximate input size, if reached"));
            assert!(size.contains(
                &"      description: Enter `not reached` if installation or doctor failed before processing."
            ));
            assert!(
                size.contains(&"      required: true"),
                "first-use size or explicit not-reached status must remain required"
            );
        }

        let privacy_items: Vec<_> = items
            .iter()
            .filter(|item| item.contains(&"    id: privacy"))
            .collect();
        assert_eq!(
            privacy_items.len(),
            1,
            "issue form must have one canonical privacy body item: {}",
            path.display()
        );
        let privacy = privacy_items[0];
        assert_eq!(
            privacy.first().copied(),
            Some("  - type: checkboxes"),
            "privacy body item must be checkboxes: {}",
            path.display()
        );
        let required_option = [
            format!("        - label: {PRIVACY_CONFIRMATION}"),
            "          required: true".to_owned(),
        ];
        assert!(
            privacy.windows(2).any(|lines| {
                lines[0] == required_option[0].as_str() && lines[1] == required_option[1].as_str()
            }),
            "exact privacy confirmation must itself be required: {}",
            path.display()
        );
        assert!(
            !privacy.contains(&"          required: false"),
            "privacy confirmation cannot be optional: {}",
            path.display()
        );

        let reproduction_items: Vec<_> = items
            .iter()
            .filter(|item| item.contains(&"    id: reproduction"))
            .collect();
        assert_eq!(
            reproduction_items.len(),
            1,
            "issue form must have one reproduction body item: {}",
            path.display()
        );
        let reproduction = reproduction_items[0];
        assert_eq!(
            reproduction.first().copied(),
            Some("  - type: textarea"),
            "reproduction must be a textarea body item: {}",
            path.display()
        );
        assert!(
            reproduction.contains(&"      label: Synthetic or sanitized reproduction"),
            "reproduction body item must request synthetic or sanitized input: {}",
            path.display()
        );

        forms.push(name.to_owned());
    }

    forms.sort();
    assert_eq!(
        forms,
        ["first-use-feedback.yml", "product-defect.yml"].map(str::to_owned),
        "every public issue form must be reviewed as a privacy-safe collection path"
    );
}
