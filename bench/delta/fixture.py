#!/usr/bin/env python3
"""Deterministic public fixture for the GPT-5.6 Luna Azdaja delta gate."""
from __future__ import annotations

import hashlib

SELECTED_RECORDS = 64
HAM_RECORDS = 42
SPAM_RECORDS = SELECTED_RECORDS - HAM_RECORDS
DISTRACTOR_RECORDS = 242
TOTAL_RECORDS = SELECTED_RECORDS + DISTRACTOR_RECORDS
USER_NOISE_BYTES = 4096

HAM_TEMPLATES = (
    "Hi {name}, our project planning meeting is confirmed for Tuesday at {hour}:30 in room {room}. Please bring the latest notes. Ref {ref}.",
    "Your dental appointment at Riverside Clinic is booked for {month} {day} at {hour}:00. Call the clinic desk if you need to reschedule. Ref {ref}.",
    "Dad, I arrived safely at the station. I will take the local bus home and should be there around {hour}:15. Ref {ref}.",
    "The school office confirms that {name} can be collected from the main entrance after practice at {hour}:45. Ref {ref}.",
    "Your reserved library book is ready for pickup at the central branch and will be held until {month} {day}. Ref {ref}.",
    "Team, the code review for change {ref} is complete. Please join the normal standup at {hour}:00 tomorrow to discuss it.",
    "Your grocery delivery is scheduled for {month} {day} between {hour}:00 and {hour}:45. The driver will use the front entrance. Ref {ref}.",
    "Can you bring the blue folder to family dinner at {hour}:30 tonight? I left it beside the kitchen calendar. Ref {ref}.",
    "Your flight itinerary for booking {ref} is confirmed. Check-in opens at {hour}:00 on {month} {day} at the airline counter.",
    "The mechanic says your car is ready for collection after {hour}:00. The completed service order number is {ref}.",
    "The landlord scheduled the requested kitchen repair for {month} {day} at {hour}:30. The building manager will accompany the technician. Ref {ref}.",
    "Football practice moved to field {room} at {hour}:15 because of maintenance. Please tell the rest of the team. Ref {ref}.",
    "Your hotel booking {ref} is confirmed for {month} {day}. Reception will hold the room until {hour}:00 on arrival day.",
    "Hi {name}, would you like to meet for coffee near the office at {hour}:30 on {month} {day}? Ref {ref}.",
    "The community center confirms your language class in room {room} at {hour}:00 this Thursday. Registration ref {ref}.",
)

SPAM_TEMPLATES = (
    "CONGRATULATIONS! Your mobile number won a cash prize. Pay the processing fee now at prize-{ref}.invalid to claim immediately.",
    "URGENT account suspension notice: verify your password and card details today at secure-check-{ref}.invalid or lose access.",
    "Earn guaranteed income from home with no experience. Send an enrollment payment using offer code {ref} to start today.",
    "Exclusive casino bonus: deposit now and receive 500 free spins. Claim at jackpot-{ref}.invalid before midnight.",
    "You were selected for a free smartphone. Pay only the shipping charge at gift-{ref}.invalid to release your reward.",
    "Pre-approved instant loan with no credit check. Transfer the advance fee for application {ref} to receive cash in one hour.",
    "Guaranteed crypto profits of 300 percent this week. Join private wallet group {ref} and send funds now.",
    "Miracle weight-loss capsules remove 20 pounds in seven days. Order trial {ref} now with your card details.",
    "Call premium number 0900-{ref} now to hear your secret admirer message. Charges apply every minute.",
    "Tax refund waiting: submit bank login details at refund-{ref}.invalid today or the payment will be cancelled.",
    "Final warning: an unpaid parcel fee blocks delivery. Enter your card at parcel-fee-{ref}.invalid to release it.",
    "Limited investment alert: double your money by tomorrow with broker code {ref}. Deposit before this offer expires.",
)

NAMES = ("Mira", "Noah", "Lina", "Owen", "Sara", "Theo", "Ava", "Milan", "Lea", "Iris")
MONTHS = ("June", "July", "August", "September", "October")


def is_ham(index: int) -> bool:
    """A full-cycle permutation makes exactly HAM_RECORDS selected rows ham."""
    return ((index * 73 + 19) % SELECTED_RECORDS) < HAM_RECORDS


def message(index: int, ham: bool) -> str:
    templates = HAM_TEMPLATES if ham else SPAM_TEMPLATES
    template = templates[(index * 17 + 5) % len(templates)]
    return template.format(
        name=NAMES[(index * 7 + 3) % len(NAMES)],
        hour=8 + ((index * 5 + 2) % 11),
        room=1 + ((index * 11 + 4) % 24),
        month=MONTHS[(index * 3 + 1) % len(MONTHS)],
        day=1 + ((index * 13 + 6) % 27),
        ref=410000 + index * 37,
    )


def user_noise(index: int) -> str:
    chunks: list[str] = []
    counter = 0
    while sum(map(len, chunks)) < USER_NOISE_BYTES:
        chunks.append(hashlib.sha256(f"azdaja-delta-user:{index}:{counter}".encode()).hexdigest())
        counter += 1
    return "".join(chunks)[:USER_NOISE_BYTES]


def records() -> list[tuple[str, bool | None]]:
    rows: list[tuple[int, str, bool | None]] = []
    for index in range(SELECTED_RECORDS):
        ham = is_ham(index)
        date = f"2026-May-{1 + ((index * 7 + 2) % 28):02d} {8 + index % 11:02d}:{(index * 13) % 60:02d}"
        line = f"Date: {date} || User: user-{index:03d}-{user_noise(index)} || Instance: {message(index, ham)}"
        rows.append((index, line, ham))
    for offset in range(DISTRACTOR_RECORDS):
        index = SELECTED_RECORDS + offset
        date = f"2026-June-{1 + ((offset * 5 + 1) % 28):02d} {9 + offset % 10:02d}:{(offset * 17) % 60:02d}"
        line = f"Date: {date} || User: user-{index:03d}-{user_noise(index)} || Instance: {message(index, offset % 2 == 0)}"
        rows.append((index, line, None))
    rows.sort(key=lambda row: (row[0] * 137 + 29) % TOTAL_RECORDS)
    return [(line, label) for _, line, label in rows]


def generate() -> str:
    return "\n".join(line for line, _ in records()) + "\n"


def expected_answer() -> int:
    return sum(label is True for _, label in records())


def selected_instances() -> list[str]:
    selected: list[str] = []
    for line, label in records():
        if label is not None:
            selected.append(line.split(" || Instance: ", 1)[1])
    return selected


def validate() -> dict[str, int | str]:
    text = generate()
    selected = selected_instances()
    assert len(records()) == TOTAL_RECORDS
    assert len(selected) == SELECTED_RECORDS
    assert len(set(selected)) == SELECTED_RECORDS
    assert expected_answer() == HAM_RECORDS
    assert text.isascii()
    assert len(text.encode()) > 1_000_000
    compact = "\n".join(f"{index}\t{value}" for index, value in enumerate(selected))
    assert len(compact.encode()) < 65536
    return {
        "context_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "context_bytes": len(text.encode()),
        "total_records": TOTAL_RECORDS,
        "selected_records": SELECTED_RECORDS,
        "unique_decision_evidence": len(set(selected)),
        "expected_answer": expected_answer(),
        "compact_evidence_bytes": len(compact.encode()),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(validate(), sort_keys=True))
