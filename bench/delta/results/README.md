# Frozen diagnostic results

`r5-result.json` is the exact sanitized stdout from the single r5 paired GPT-5.6 Luna campaign. It records hashes and aggregate usage, not raw model text or credentials. The gate failed because neither candidate arm invoked Azdaja, and OpenCode-native was not exact. No efficiency claim was made.

`r9-result.json` is the exact sanitized stdout from the direct candidate-only r9 follow-up against the hash-bound correct r8 native baseline. Both managed Luna calls succeeded with complete usage and lower observed tokens and wall time, but strict 64-label response finalization failed before either candidate produced an answer. Quality therefore blocks any delta claim.
