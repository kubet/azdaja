#!/usr/bin/env python3
from pathlib import Path
reports=[
("INC-101","Authentication remained healthy until the signing material aged beyond its renewal window; every subsequent request was rejected although hosts and links were nominal."),
("INC-102","Interface queues stayed pinned, retransmissions climbed, and packet loss vanished only after traffic was shifted to the secondary link."),
("INC-103","Writes stalled as the volume reached its allocation ceiling; deleting old snapshots immediately restored service."),
("INC-104","The rotating access secret was no longer accepted after its validity interval elapsed; issuing fresh credentials fixed all callers."),
("INC-105","Disk free space fell to zero and compaction could not reserve blocks; expanding the volume cleared the incident."),
("INC-106","A saturated uplink accumulated deep queues and dropped frames under peak traffic; rerouting reduced latency at once."),
]
filler="Routine telemetry remained within nominal bounds. "*1800
out=[]
for i,text in reports: out.append(f"=== {i} ===\n{filler}\nFINDING: {text}\n{filler}\n")
Path(__file__).with_name("semantic-incidents.txt").write_text("".join(out))
