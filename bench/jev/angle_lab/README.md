# Six isolated Jev × Azdaja experiments

Read PLAN.md and AMENDMENT-01.md first. No lane is presumed beneficial. Rejected early drafts are outside the active experiment; active grading consumes external results only.

Offline checks:

```sh
AZDAJA_ANGLE_BINARY=/absolute/path/to/tested/azdaja python3 -B -m unittest bench.jev.angle_lab.test_native bench.jev.angle_lab.test_lanes -v
python3 -B -m bench.jev.angle_lab.campaign
```

Every prepared pack is also passed through the actual native validator with a synthetic credential-leakage guard. The expected refusal is precise and occurs before transport. This is separate from live efficacy.

Root alone may seal and run the campaign. `--seal --azdaja PATH` hashes code, raw JSONL, packs, detached gold, source context and binary. `--live --acknowledge-provider-calls --azdaja PATH --credential-state-root PRIVATE_HOST_ROOT --output NEW_DIRECTORY` is a separate, explicit action. An exclusive `.started` marker prevents automatic readmission of the same manifest. Default invocation performs zero inference. Do not rerun a failed holdout or remove that marker to seek better scores.

The driver uses actual `start/load/exec/final` and persistent re-entry, not a shadow API wrapper. This is an authored adaptive plan with semantic leaves, not automatically synthesized planning. Contract/deadline/usage failures are terminal. A stopped receipt retains known usage and marks unknown usage as unknown. Reports separate quality from timing/token/cost estimates and preserve every negative result. Source/model strings do not authenticate backend weights, and documented prices are not billing receipts.
