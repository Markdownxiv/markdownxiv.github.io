"""The AP-JSON subset: no JSON numbers; bounded, exact UTF-8, ASCII object keys."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .errors import Rejection, require

MAX_PACKAGE = 60_000
MAX_PAPER = 262_144
HEX = re.compile(r"[0-9a-f]{64}\Z")
DEC = re.compile(r"0|[1-9][0-9]*\Z")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _bad_number(_):
    raise Rejection("invalid_json", "JSON numbers are forbidden; use canonical decimal strings.")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "invalid_json", "Duplicate JSON key.")
        result[key] = value
    return result


def _check(value, depth=0, budget=None):
    if budget is None:
        budget = [40_000]
    budget[0] -= 1
    require(depth <= 24 and budget[0] >= 0, "input_limit", "JSON nesting or node limit exceeded.")
    if isinstance(value, str):
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), "invalid_json", "Invalid Unicode scalar.")
    elif value is None or type(value) is bool:
        return
    elif isinstance(value, list):
        for item in value:
            _check(item, depth + 1, budget)
    elif isinstance(value, dict):
        for key, item in value.items():
            require(isinstance(key, str) and re.fullmatch(r"[a-z][a-z0-9_]*", key) is not None,
                    "invalid_json", "Object keys must be lowercase ASCII identifiers.")
            _check(item, depth + 1, budget)
    else:
        raise Rejection("invalid_json", "Unsupported JSON type.")


def loads(data, limit=MAX_PACKAGE):
    if isinstance(data, str):
        try:
            data = data.encode("utf-8")
        except UnicodeError as exc:
            raise Rejection("invalid_json", "Invalid UTF-8.") from exc
    require(isinstance(data, bytes) and len(data) <= limit, "input_limit", "JSON byte limit exceeded.")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=_bad_number, parse_float=_bad_number,
                           parse_constant=_bad_number)
        _check(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Rejection("invalid_json", "Malformed AP-JSON.") from exc


def canonical(value):
    _check(value)
    # This exact encoding is part of v1, not a reliance on default JSON formatting.
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def read_json(path, limit=2_000_000):
    with Path(path).open("rb") as stream:
        return loads(stream.read(limit + 1), limit)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def fields(obj, required, optional=()):
    require(isinstance(obj, dict) and set(required) <= obj.keys()
            and obj.keys() <= set(required) | set(optional), "invalid_fields", "Missing or unknown fields.")


def decimal(value, low=0, high=(1 << 64) - 1, signed=False):
    pattern = r"(?:0|[1-9][0-9]*)" if not signed else r"(?:0|-?[1-9][0-9]*)"
    require(isinstance(value, str) and len(value) <= 80
            and re.fullmatch(pattern, value) is not None, "invalid_integer", "Noncanonical integer.")
    number = int(value)
    require(low <= number <= high, "input_limit", "Integer outside permitted range.")
    return number


def hexhash(value):
    require(isinstance(value, str) and HEX.fullmatch(value) is not None,
            "invalid_hash", "Expected 32-byte lowercase hexadecimal hash.")
    return value


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value),
            "invalid_time", "Expected UTC time YYYY-MM-DDTHH:MM:SSZ.")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise Rejection("invalid_time", "Invalid calendar time.") from exc


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def text(value, low, high):
    require(isinstance(value, str) and low <= len(value) <= high
            and not any(ord(c) < 32 or ord(c) == 127 for c in value),
            "invalid_metadata", "Invalid metadata text or length.")


def metadata(value):
    fields(value, ["title", "abstract", "authors", "license"], ["tags"])
    text(value["title"], 1, 240)
    text(value["abstract"], 1, 6000)
    require(isinstance(value["authors"], list) and 1 <= len(value["authors"]) <= 32,
            "invalid_metadata", "Expected 1–32 authors.")
    for author in value["authors"]:
        text(author, 1, 120)
    text(value["license"], 1, 80)
    require(re.fullmatch(r"[A-Za-z0-9.+-]+", value["license"]) is not None,
            "invalid_metadata", "Declare a license identifier explicitly.")
    tags = value.get("tags", [])
    require(isinstance(tags, list) and len(tags) <= 8, "invalid_metadata", "At most eight tags.")
    for tag in tags:
        text(tag, 1, 32)
    require(len(set(tags)) == len(tags), "invalid_metadata", "Duplicate tag.")


def paper_bytes(data):
    require(isinstance(data, bytes) and 1 <= len(data) <= MAX_PAPER,
            "paper_limit", "Paper must contain 1–262144 UTF-8 bytes.")
    try:
        decoded = data.decode("utf-8")
    except UnicodeError as exc:
        raise Rejection("invalid_utf8", "Paper is not UTF-8.") from exc
    require(not decoded.startswith("\ufeff") and "\x00" not in decoded,
            "invalid_utf8", "BOM and NUL are forbidden. No normalization is performed.")
    return data


def content_hash(meta, paper_hash):
    metadata(meta)
    hexhash(paper_hash)
    return sha(canonical({"metadata": meta, "paper_sha256": paper_hash}))
