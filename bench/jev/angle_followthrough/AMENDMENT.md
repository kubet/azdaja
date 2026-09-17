# Local setup failure continuation, before further inference

The original frozen campaign at `7950c24` stopped after one successful typed
calibration request (20 questions, 3,261 input and 404 output tokens). Its first
generative request failed during local `session_setup/connect`: one setup event,
zero entered model turns. The receipt remains stopped, immutable, and reportable.
No May evaluation judgments or other lane outputs were obtained.

Inspection without reading credential contents found the existing default-state
Jcode bridge's OAuth file is a regular file, while Azdaja requires its managed
symlink. Both local sockets were unavailable. We will not modify or kill that
shared bridge. The user-requested durable TypeSafe attachment remains in the
normal private host state. A separate owner-only experimental state receives a
temporary attachment through stdin and permits the existing native transport to
create its own bridge. Remove that temporary attachment after this continuation.

This is an explicitly disclosed local-setup correction, not a silent retry or a
new quality sample. The original source, requests, detached gold, thresholds,
order, concrete model, binary and failed receipt remain unchanged. The one
completed calibration observation is verified by frozen hashes, reloaded into
the actual evaluator and reused without a provider request. Its fitted threshold
is unchanged. No favorable-output selection or threshold repair is permitted.

The original global caps still apply across both receipts: 24 typed attempts,
12 logical generative calls including the failed setup, 1.5M reported typed
input tokens, and 30 minutes from the first campaign start, including this
repair interval. This continuation therefore has at most 23 typed and 11
logical generative admissions. Known usage is carried, not reset. Any further
transport/schema/resource failure stops without another automatic admission.

The continuation runner and predecessor artifacts receive a separate manifest
and exclusive started marker before inference. It does not edit the original
manifest or reinterpret a stopped receipt as complete. Report both attempts.
