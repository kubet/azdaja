use azdaja::Config;

#[test]
fn explicit_jcode_repair_model_deserializes_and_validates() {
    let config: Config = toml::from_str("jcode_repair_model = \"gpt-5.6-luna\"").unwrap();
    let config = config.validate().unwrap();
    assert_eq!(config.jcode_repair_model.as_deref(), Some("gpt-5.6-luna"));
    assert!(Config::default().jcode_repair_model.is_none());
}

#[test]
fn blank_jcode_repair_model_is_rejected_when_present() {
    for value in ["", "   "] {
        let mut config = Config::default();
        config.jcode_repair_model = Some(value.to_owned());
        let error = config.validate().err().unwrap().to_string();
        assert!(error.contains("jcode_repair_model cannot be empty when present"));
    }
}
