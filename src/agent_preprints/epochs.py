import re
import secrets
from datetime import timedelta
from pathlib import Path

from . import PROTOCOL, VERIFIER, PROTOCOL_V2, VERIFIER_V2, PROTOCOL_V3, VERIFIER_V3
from .codec import (canonical, decimal, fields, hexhash, read_json, sha,
                    timestamp, utcnow, write_json)
from .errors import Rejection, require
from .poa import DEV_POLICY, PRODUCTION_POLICY, validate_policy
from .pow import target_int, validate_calibration


def epoch_path(root, epoch_id):
    require(isinstance(epoch_id, str) and re.fullmatch(r"(?:dev-)?(?:v[23]-)?\d{4}-\d{2}-\d{2}", epoch_id),
            "unknown_epoch", "Invalid epoch identifier.")
    return Path(root) / "challenges" / "epochs" / (epoch_id + ".json")


def validate_epoch(epoch, production=True):
    v2 = isinstance(epoch, dict) and epoch.get("protocol") in (PROTOCOL_V2, PROTOCOL_V3)
    v3 = isinstance(epoch, dict) and epoch.get("protocol") == PROTOCOL_V3
    fields(epoch, ["protocol", "verifier", "epoch_id", "profile", "repository_id", "not_before",
                   "expires_at", "salt", "target", "calibration_id", "question_count", "poa_policy"]
           + (["taxonomy_hash", "resource_policy"] if v2 else []))
    require((epoch["protocol"], epoch["verifier"]) in ((PROTOCOL, VERIFIER), (PROTOCOL_V2, VERIFIER_V2), (PROTOCOL_V3, VERIFIER_V3)),
            "protocol_version", "Unsupported protocol or verifier version.")
    epoch_path(".", epoch["epoch_id"])
    require(("v3-" in epoch["epoch_id"]) == v3 and ("v2-" in epoch["epoch_id"]) == (v2 and not v3), "invalid_epoch", "Epoch identifier/protocol mismatch.")
    if v2:
        from .assets import POLICY
        if v3:
            from .protocol_v3 import POLICY
        hexhash(epoch["taxonomy_hash"])
        require(epoch["resource_policy"] == POLICY, "invalid_policy", "Unsupported resource policy.")
    require(epoch["profile"] in ("production", "development") and
            (not production or epoch["profile"] == "production"),
            "production_required", "Production admission rejects development epochs.")
    decimal(epoch["repository_id"], 1)
    epoch_path(".", epoch["epoch_id"])
    require(epoch["epoch_id"].startswith("dev-") == (epoch["profile"] == "development"),
            "invalid_epoch", "Epoch identifier/profile mismatch.")
    require(timestamp(epoch["expires_at"]) - timestamp(epoch["not_before"]) == timedelta(hours=48),
            "invalid_epoch", "Epoch validity must be exactly 48 hours.")
    hexhash(epoch["salt"])
    target_int(epoch["target"])
    if epoch["profile"] == "production":
        hexhash(epoch["calibration_id"])
    else:
        require(epoch["calibration_id"] == "development-only", "invalid_epoch", "Invalid development calibration.")
    require(epoch["question_count"] == "2", "invalid_policy", "v1 requires exactly two questions.")
    validate_policy(epoch["poa_policy"], production=epoch["profile"] == "production")


def initialize(root, calibration, repository, repository_id, site_url):
    from .github import repository_name
    from .site import site_address
    repository_name(repository)
    decimal(repository_id, 1)
    site_address(site_url)
    validate_calibration(calibration)
    root = Path(root)
    raw = canonical(calibration) + b"\n"
    cid = sha(raw)
    path = root / "challenges" / "calibrations" / (cid + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == raw, "immutable_conflict", "Calibration hash collision or modified file.")
    else:
        path.write_bytes(raw)
    write_json(root / "config" / "production.json", {"repository": repository, "repository_id": repository_id,
               "site_url": site_url.rstrip("/") + "/", "calibration_id": cid, "enabled": True})
    return cid


def rotate(root, now=None, development=False, repository_id="1", protocol=None):
    root, now = Path(root), now or utcnow()
    moment = timestamp(now)
    config_path = root / "config" / "production.json"
    if development:
        protocol = protocol or PROTOCOL
        profile, cid, target, policy = "development", "development-only", "0" + "f" * 63, DEV_POLICY
    else:
        config = read_json(config_path)
        protocol = protocol or config.get("protocol", PROTOCOL)
        cid = config.get("calibration_id")
        if not config.get("enabled") or cid is None:
            write_json(root / "challenges" / "latest.json", {"status": "calibration_required", "protocol": PROTOCOL})
            return None
        hexhash(cid)
        cal_path = root / "challenges" / "calibrations" / (cid + ".json")
        require(cal_path.exists(), "calibration_required", "Published calibration file is missing.")
        require(sha(cal_path.read_bytes()) == cid, "calibration_required", "Calibration hash mismatch.")
        calibration = read_json(cal_path)
        validate_calibration(calibration)
        profile, target, policy = "production", calibration["target"], PRODUCTION_POLICY
        repository_id = config["repository_id"]
    require(protocol in (PROTOCOL, PROTOCOL_V2, PROTOCOL_V3), "protocol_version", "Unsupported epoch protocol.")
    eid = ("dev-" if development else "") + (protocol.rsplit("-", 1)[1] + "-" if protocol != PROTOCOL else "") + moment.strftime("%Y-%m-%d")
    path = epoch_path(root, eid)
    registry_path = root / "challenges" / "registry.json"
    registry = read_json(registry_path) if registry_path.exists() else {"epochs": []}
    if path.exists():
        epoch = read_json(path)
        validate_epoch(epoch, not development)
        entries = [e for e in registry["epochs"] if e["epoch_id"] == eid]
        require(len(entries) == 1 and entries[0]["epoch_hash"] == sha(path.read_bytes()),
                "immutable_conflict", "Existing epoch is absent from registry or was modified.")
    else:
        # Never backdate publication, even when a scheduled run starts late.
        epoch = {"protocol": protocol, "verifier": {PROTOCOL: VERIFIER, PROTOCOL_V2: VERIFIER_V2, PROTOCOL_V3: VERIFIER_V3}[protocol], "epoch_id": eid, "profile": profile,
                 "repository_id": repository_id, "not_before": now,
                 "expires_at": (moment + timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "salt": secrets.token_hex(32), "target": target, "calibration_id": cid, "question_count": "2", "poa_policy": policy}
        if protocol in (PROTOCOL_V2, PROTOCOL_V3):
            from . import assets, taxonomy
            epoch.update({"taxonomy_hash": taxonomy.ensure(root), "resource_policy": assets.POLICY})
            if protocol == PROTOCOL_V3:
                from .protocol_v3 import POLICY
                epoch["resource_policy"] = POLICY
        validate_epoch(epoch, not development)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(canonical(epoch) + b"\n")
        registry["epochs"].append({"epoch_id": eid, "epoch_hash": sha(path.read_bytes()),
                                   "published_at": now if development else None})
        write_json(registry_path, registry)
    latest = {"status": "active", "protocol": protocol, "epoch_id": eid,
              "epoch_hash": sha(path.read_bytes()), "path": "epochs/" + eid + ".json"}
    write_json(root / "challenges" / "latest.json", latest)
    return epoch


def load_epoch(root, eid, expected_hash, received_at, repository_id, production=True):
    root = Path(root)
    if production:
        config = read_json(root / "config" / "production.json")
        require(config.get("enabled") is True and config.get("calibration_id") is not None,
                "calibration_required", "Production submissions are paused until a measured calibration is published.")
        require(config["repository_id"] == repository_id, "repository_mismatch", "Platform repository configuration mismatch.")
    path = epoch_path(root, eid)
    require(path.is_file(), "unknown_epoch", "Epoch is not in the trusted repository.")
    raw = path.read_bytes()
    hexhash(expected_hash)
    require(sha(raw) == expected_hash, "epoch_hash_mismatch", "Epoch hash differs from the trusted immutable file.")
    epoch = read_json(path)
    validate_epoch(epoch, production)
    require(epoch["epoch_id"] == eid, "invalid_epoch", "Epoch filename/identifier mismatch.")
    require(epoch["repository_id"] == repository_id, "repository_mismatch", "Epoch targets another repository.")
    registry = read_json(root / "challenges" / "registry.json")
    entries = [e for e in registry["epochs"] if e["epoch_id"] == eid and e["epoch_hash"] == expected_hash]
    require(len(entries) == 1, "unknown_epoch", "Epoch is not registered.")
    if entries[0]["published_at"] is None:
        raise Rejection("epoch_unpublished", "Epoch has not been confirmed deployed to Pages.", True)
    observed = timestamp(received_at)
    require(observed >= timestamp(entries[0]["published_at"]), "epoch_unpublished_at_submission", "Epoch was not published when this request was observed.")
    require(timestamp(epoch["not_before"]) <= observed, "epoch_not_yet_valid", "Epoch was not yet valid at receipt time.")
    require(observed < timestamp(epoch["expires_at"]), "epoch_expired", "Epoch expired before receipt of this complete request.")
    if production:
        cid = epoch["calibration_id"]
        cal_path = root / "challenges" / "calibrations" / (cid + ".json")
        require(cal_path.is_file() and sha(cal_path.read_bytes()) == cid,
                "calibration_required", "Epoch calibration is missing or corrupted.")
        cal = read_json(cal_path)
        validate_calibration(cal)
        require(cal["target"] == epoch["target"], "calibration_required", "Epoch target differs from calibration.")
    return epoch
