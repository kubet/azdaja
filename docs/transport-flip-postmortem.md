# Transport flip: retained-evidence post-mortem

## Decision

The fixed transport scout's **+0.00-point** result is a **pre-inference setup
failure, non-diagnostic for discoverability or selection—not genuine disuse**.
The treatment was configured as available, but no live root turn was reached. No
root could discover, select, or decline the agent-class route. The evidence
therefore rules out a "presented and declined" reading, while also stopping
short of claiming an observed discoverability failure.

This is a private diagnostic, not an official Oolong or leaderboard result, not
a product comparison, and not a superiority or inferiority claim.

## What the retained evidence proves

The sealed schedule contained ten fixed pairs: control first, then treatment,
with no retries or replacements. All 20 rows reached terminal accounting. All
20 failed with the same sanitized controller fact: private OAuth/session setup
failed before inference. Consequently:

- successful provider turns were **0**;
- agent-class calls were **0**;
- control and treatment execution were **0/10** each;
- fail-closed scores were **0.00 vs 0.00**, a **+0.00-point** delta;
- observed costs were zero on both arms, so no treatment/control cost ratio
  existed and the cost gate did not pass; and
- cleanup found no owned campaign processes or agent-call directories.

Treatment rows recorded `agent_transport_available=true` and
`agent_transport_forced=false`; control rows recorded it unavailable. That
metadata proves configuration assignment, not presentation to a model. The
candidate code did include a root-prompt capability disclosure and a separately
gated route. The retained offline fake-provider proof exercised that route once,
but it was explicitly outside the disease denominator and is not live-provider
or model-choice evidence. The one forced live proof also failed before it could
establish the required live path.

The exact sanitized terminal aggregate is retained in
[`endgame-agent-transport-v2-disease10-terminal.json`](../bench/results/endgame-agent-transport-v2-disease10-terminal.json).
Its receipt hash remains bound by the Day-7 launch receipt.

## Evidence versus inference

A genuine-disuse finding would require at least one successful root turn that
received the capability disclosure, retained evidence that the route was
selectable, and an observed decision not to select it. None exists here.

A discoverability finding would require the selection stage to be reached and
then show that the surface was not noticed or selected. That stage was never
reached either. The narrower supported statement is that setup prevented the
surface from becoming discoverable to a live root. Whether a reachable root
would notice, decline, or benefit from it is unknown.

The numeric tie therefore measures fail-closed setup zeros, not equal task
quality, equal cost, equal usefulness, or a model preference for the bare arm.
It cannot support promotion, adoption, or a new fixed-199 run. The sealed
schedule remains terminal and is never resumed, retried, replaced, or rescored.

## Post-launch disposition

One repaired **v0.2 roadmap** study may be designed to separate provider reach,
capability presentation, selection, and agent execution with distinct retained
receipts. It would need a fresh schedule, explicit post-launch owner
authorization, a passing live-path precondition before denominator rows, and a
preregistered interpretation for presented-but-unselected treatment rows.

That is roadmap material only. This post-mortem does **not** authorize an extra
flip, benchmark call, ARC call, provider inference, API call, rerun, or release
change before launch.
