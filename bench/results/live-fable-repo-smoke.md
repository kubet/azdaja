# Live Claude Fable repository smoke

Source commit: `30f27f5a9ec916c72b66ea58d879df6cfe634a11`

Claude Fable returned `src/module_07777.rs|AZD-7777` exactly from a 52,428,800-byte synthetic repository dump. Azdaja sent a 12,460-byte root prompt, then executed the model-authored generic program locally against the complete input.

- Provider calls: 1
- Provider wall time: 25.789 seconds
- End-to-end wall time: 26.990 seconds
- Input-to-root-prompt ratio: 4,208x by bytes
- Local Monty executions: 1
- Recursive or semantic subcalls: 0
- Exact 100-byte source spans in the provider prompt: 0
- Host input or scratch paths in the provider prompt: 0
- The published model response contains neither the ticket nor the final answer constant.

## Limits

- single synthetic live smoke
- one model and one provider route
- no baseline arm
- no repeated trials
- subscription token usage unavailable in text mode
- not a benchmark or superiority result
