# Azdaja 50 MiB current-source acceptance capsule

Source commit: `fe91f98d4c49d5aca59c4911c12869c9a05d22ea`

This provider-free acceptance run exercised the release `azdaja solo` path over three deterministic, exactly 50 MiB inputs. The scripted transport returned programs rather than answer constants, and Azdaja executed those programs against the full local input.

| Scenario | Exact answer | Input | Root prompt | Input / prompt | Reaped-child RSS high-water |
|---|---|---:|---:|---:|---:|
| build | `Answer: 13` | 50 MiB | 12,737 B | 4,116x | 213.1 MiB |
| repo | `src/module_07777.rs\|AZD-7777` | 50 MiB | 12,451 B | 4,211x | 213.2 MiB |
| transcript | `ship-v0.1-after-doctor` | 50 MiB | 12,743 B | 4,114x | 213.2 MiB |

All three runs reported one root transport call, one Monty execution, zero recursive subcalls, no exact 100-byte source span in the model-facing prompt, and no surviving session after cleanup.

## What this does not prove

- live-model program synthesis
- semantic quality on natural data
- arbitrary-input support
- comparison superiority
- official benchmark status
- operating-system sandbox guarantees

Machine-readable receipt: `bench/results/product-50mb-current-source.json`
Captured command log: `bench/results/product-50mb-current-source.txt`
