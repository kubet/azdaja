#!/usr/bin/env python3
"""Normalize Darwin LC_UUID, then replace the linker signature deterministically."""

import hashlib
import os
import pathlib
import subprocess
import sys

ASSET_NAME = "azdaja-v0.1.1-darwin-arm64"
LC_UUID = 0x1B
MH_MAGIC_64_LE = 0xFEEDFACF


def expected_uuid() -> bytes:
    value = bytearray(hashlib.sha256(ASSET_NAME.encode()).digest()[:16])
    value[6] = (value[6] & 0x0F) | 0x40  # RFC 4122 version 4 layout.
    value[8] = (value[8] & 0x3F) | 0x80  # RFC 4122 variant.
    return bytes(value)


def uuid_offset(data: bytes) -> int:
    if len(data) < 32 or int.from_bytes(data[:4], "little") != MH_MAGIC_64_LE:
        raise SystemExit("normalize-darwin: expected thin 64-bit little-endian Mach-O")
    commands = int.from_bytes(data[16:20], "little")
    offset = 32
    found: list[int] = []
    for _ in range(commands):
        if offset + 8 > len(data):
            raise SystemExit("normalize-darwin: truncated Mach-O load commands")
        command = int.from_bytes(data[offset : offset + 4], "little")
        size = int.from_bytes(data[offset + 4 : offset + 8], "little")
        if size < 8 or offset + size > len(data):
            raise SystemExit("normalize-darwin: invalid Mach-O load command")
        if command == LC_UUID:
            if size != 24:
                raise SystemExit("normalize-darwin: invalid LC_UUID size")
            found.append(offset + 8)
        offset += size
    if len(found) != 1:
        raise SystemExit(f"normalize-darwin: expected one LC_UUID, found {len(found)}")
    return found[0]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: normalize-darwin.py /path/to/azdaja-v0.1.1-darwin-arm64")
    path = pathlib.Path(sys.argv[1])
    if path.name != ASSET_NAME or not path.is_file() or path.is_symlink():
        raise SystemExit("normalize-darwin: exact regular asset filename required")
    data = bytearray(path.read_bytes())
    offset = uuid_offset(data)
    data[offset : offset + 16] = expected_uuid()
    path.write_bytes(data)
    path.chmod(0o755)
    subprocess.run(
        [
            "/usr/bin/codesign",
            "--force",
            "--sign",
            "-",
            "--identifier",
            "dev.kubet.azdaja",
            "--timestamp=none",
            str(path),
        ],
        check=True,
        stdin=subprocess.DEVNULL,
    )
    normalized = path.read_bytes()
    offset = uuid_offset(normalized)
    if normalized[offset : offset + 16] != expected_uuid():
        raise SystemExit("normalize-darwin: LC_UUID verification failed")
    subprocess.run(
        ["/usr/bin/codesign", "--verify", "--strict", str(path)],
        check=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if os.access(path, os.X_OK) is False:
        raise SystemExit("normalize-darwin: output is not executable")


if __name__ == "__main__":
    main()
