# Response-driven Choice descent

`python3 -B -m bench.jev.angle_lab.descent.run` prepares16 exact fixed-commit excerpts in4 document-heading branches. Gold is separate. Flat Choice sees all excerpts. Root Choice sees only headings and paths. Each child pack is created from actual returned branch probabilities, not from gold.

Greedy preserves only the returned winner. Beam preserves at most2 branches with probability at least.1, unless no_match wins. Flat and beam return at most2 excerpts under the same .1 rule. This cutoff is an experimental selection policy, not runtime enforcement or calibrated confidence. The two-evidence query can falsify greedy sufficiency. No-match is explicit. All source/index bytes, questions, rounds and observed timings count.

This is a small retrieval diagnostic. Choice trees already appear in TypeSafe's cookbook. It is neither a new algorithm nor proof of logarithmic total work or search over a million-source corpus. Multi-path costs and irreversible discarded branches are part of the result.
