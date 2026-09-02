# Security policy

## Supported versions

Security fixes are developed against the latest released version. Please reproduce and report issues against the latest release or a current commit when possible. If you use an older release, upgrade before concluding that a fix is unavailable, and include the exact version or commit in the report.

## Reporting a vulnerability

Please use a **private GitHub security advisory** rather than a public issue:

- [Open a private security advisory](https://github.com/1jehuang/jcode/security/advisories/new)
- [Security policy and advisories](https://github.com/1jehuang/jcode/security)

Do not put credentials, tokens, private repository contents, exploit code, sensitive logs, or other actionable vulnerability details in a public issue, pull request, discussion, or chat. If private advisory access is unavailable, report only a high-level, non-sensitive summary publicly and ask for a private contact path.

Useful evidence includes:

- affected version or commit, operating system, host, and installation mode;
- the smallest safe reproduction or a redacted description of the trigger;
- expected and observed behavior, including whether native host behavior remained available;
- relevant redacted logs, exit status, and stack trace; and
- the security impact and any practical mitigation or workaround.

Please redact secrets and personal or repository-sensitive data. Do not test against systems or data you do not own or have permission to assess.

## Scope and limitations

A hook or workflow check in this project is cooperative behavior, not an OS sandbox or a guarantee against a malicious same-user process, a compromised host, or ambient permissions retained by native tools. Reports should not assume that workflow activation, routing, or release verification provides stronger isolation than the implementation documents.

The separately tracked broker-hardening items are intentionally out of scope for this bounded activation remediation: configuration-descriptor no-follow/inode/mode/hash binding, ledger symlink safety, strict-usage exact key-set validation, and stale integration hashes remain follow-up work. This disposition does not claim those risks are fixed.
