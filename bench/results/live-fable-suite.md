# Live Claude Fable three-scenario product suite

Source commit: `2514d26a245a5d1c9f6bb1f351391b69a616c3b1`

Claude Fable synthesized three generic programs from three bounded root prompts. Azdaja executed each program locally against its complete deterministic input and returned all three exact answers.

| Scenario | Exact result | Root prompt | Input / prompt | Provider time |
|---|---|---:|---:|---:|
| build | `Answer: 13` | 12,739 B | 4,116x | 17.570 s |
| repo | `src/module_07777.rs\|AZD-7777` | 12,460 B | 4,208x | 22.054 s |
| catalog | `Color: cerulean` | 12,770 B | 4,106x | 23.872 s |

Totals: 3/3 exact, 3 provider calls, 3 Monty executions, 0 recursive or semantic subcalls.

Every model response is published in the receipt and contains neither its expected answer nor its answer-specific constant. Exact scanners found zero 100-byte source spans in all provider prompts, and no prompt contained a repository, input, or scratch host path.

## Limits

- three deterministic synthetic live smokes
- one model and one provider route
- one provider call per scenario
- no baseline arm
- no repeated trials
- subscription token usage unavailable in text mode
- not a benchmark or superiority result
