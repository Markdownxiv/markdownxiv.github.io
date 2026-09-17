import hashlib
import os
import platform
import struct
import sys
import time
from pathlib import Path

from .codec import canonical, decimal, hexhash, read_json, sha, utcnow, write_json
from .errors import Rejection, require

IMPLEMENTATION = "python-hashlib-copy-sha256-u64be-v1"


def header(repository_id, epoch_hash, submitter_id, content_hash, protocol="agent-preprints-v1"):
    decimal(repository_id, 1)
    decimal(submitter_id, 1)
    require(protocol in ("agent-preprints-v1", "agent-preprints-v2"), "protocol_version", "Unsupported PoW protocol.")
    domain = b"agent-preprints-pow-v2" if protocol == "agent-preprints-v2" else b"agent-preprints-pow-v1"
    parts = [domain, repository_id.encode("ascii"),
             bytes.fromhex(hexhash(epoch_hash)), submitter_id.encode("ascii"),
             bytes.fromhex(hexhash(content_hash))]
    return b"".join(struct.pack(">I", len(part)) + part for part in parts)


def nonce_bytes(nonce):
    import re
    require(isinstance(nonce, str) and re.fullmatch(r"[0-9a-f]{16}", nonce) is not None,
            "invalid_nonce", "Nonce must be exactly eight bytes in lowercase hex, big endian.")
    return bytes.fromhex(nonce)


def digest(head, nonce):
    return hashlib.sha256(head + nonce_bytes(nonce)).digest()


def target_int(target):
    hexhash(target)
    number = int(target, 16)
    require(number > 0, "invalid_target", "Target must be positive.")
    return number


def verify(head, nonce, target):
    result = digest(head, nonce)
    require(int.from_bytes(result, "big") < target_int(target), "invalid_pow", "PoW hash is not below the published target.")
    return result


def seed(pow_hash):
    return hashlib.sha256(b"agent-preprints-poa-v1\0" + pow_hash).digest()


def _search_chunk(base, bound, start, stop):
    """The identical hot loop is used by measurement and actual mining."""
    for current in range(start, stop):
        trial = base.copy()
        trial.update(current.to_bytes(8, "big"))
        if trial.digest() < bound:
            return current
    return None


def mine(head, target, checkpoint=None, max_seconds=None, progress=None):
    """One thread, one fixed-header hashlib.copy per attempt; resumable, never a server call."""
    binding = sha(head + bytes.fromhex(target))
    start = 0
    if checkpoint and Path(checkpoint).exists():
        state = read_json(checkpoint)
        require(state.get("binding") == binding, "checkpoint_mismatch", "Checkpoint belongs to another proof.")
        if state.get("nonce") is not None:
            verify(head, state["nonce"], target)
            return state["nonce"]
        start = decimal(state["next_nonce"], 0, 1 << 64)
    base = hashlib.sha256(head)
    bound = target_int(target).to_bytes(32, "big")
    began = time.monotonic()
    last = began
    current = start
    try:
        while current < 1 << 64:
            stop = min(current + 8192, 1 << 64)
            found = _search_chunk(base, bound, current, stop)
            if found is not None:
                nonce = found.to_bytes(8, "big").hex()
                if checkpoint:
                    _checkpoint(checkpoint, {"binding": binding, "nonce": nonce})
                return nonce
            current = stop
            now = time.monotonic()
            if now - last >= 1:
                if checkpoint:
                    _checkpoint(checkpoint, {"binding": binding, "next_nonce": str(current)})
                if progress:
                    progress(current - start, now - began)
                last = now
            if max_seconds is not None and now - began >= max_seconds:
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        if checkpoint:
            _checkpoint(checkpoint, {"binding": binding, "next_nonce": str(current)})
        raise Rejection("mining_paused", "Mining stopped; checkpoint saved when a path was supplied.")
    raise Rejection("nonce_exhausted", "64-bit nonce space exhausted.")


def _checkpoint(path, value):
    temporary = Path(str(path) + ".tmp")
    write_json(temporary, value)
    os.replace(temporary, path)


def cpu_name():
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown (operator must identify reference CPU)"


def calibrate(seconds=10, cpu=None, conditions="unspecified load; operator must record conditions"):
    require(1 <= seconds <= 600, "input_limit", "Benchmark duration must be 1–600 seconds.")
    # Same header length and hot loop as mine. No nonce search happens in verification.
    head = header("123456789", "00" * 32, "12345678", "11" * 32)
    base = hashlib.sha256(head)
    bound = bytes(32)  # impossible target: counts every completed attempt
    started = time.perf_counter_ns()
    count = 0
    elapsed = 0
    while elapsed < seconds * 1_000_000_000:
        if _search_chunk(base, bound, count, count + 8192) is not None:
            raise RuntimeError("Impossible zero-target result")
        count += 8192
        elapsed = time.perf_counter_ns() - started
    target = min((1 << 256) - 1, ((1 << 256) * elapsed) // (count * 300 * 1_000_000_000))
    return {"profile": "production", "implementation": IMPLEMENTATION, "cpu": cpu or cpu_name(),
            "threads": "1", "python": sys.version.split()[0], "platform": platform.platform(),
            "conditions": conditions, "measured_at": utcnow(), "attempts": str(count),
            "elapsed_ns": str(elapsed), "expected_seconds": "300", "target": f"{target:064x}"}


def validate_calibration(value):
    from .codec import fields, timestamp
    fields(value, ["profile", "implementation", "cpu", "threads", "python", "platform", "conditions",
                   "measured_at", "attempts", "elapsed_ns", "expected_seconds", "target"])
    require(value["profile"] == "production" and value["implementation"] == IMPLEMENTATION
            and value["threads"] == "1" and value["expected_seconds"] == "300",
            "calibration_required", "Unsupported production calibration.")
    count = decimal(value["attempts"], 8192)
    elapsed = decimal(value["elapsed_ns"], 1_000_000_000, 610_000_000_000)
    timestamp(value["measured_at"])
    for key in ("cpu", "conditions", "platform", "python"):
        require(isinstance(value[key], str) and 1 <= len(value[key]) <= 1024,
                "calibration_required", "Calibration conditions are incomplete.")
    expected = min((1 << 256) - 1, ((1 << 256) * elapsed) // (count * 300 * 1_000_000_000))
    require(target_int(value["target"]) == expected, "calibration_required", "Target does not match measured attempts and duration.")
