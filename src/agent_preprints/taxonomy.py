"""Immutable trusted taxonomy snapshots; no network in admission."""
import shutil
from pathlib import Path

from .codec import hexhash, read_json, sha
from .errors import require


def load(root, digest):
    path = Path(root) / "taxonomy" / (hexhash(digest) + ".json")
    require(path.is_file() and not path.is_symlink(), "unknown_taxonomy", "Taxonomy snapshot is unavailable.")
    require(sha(path.read_bytes()) == digest, "taxonomy_mismatch", "Taxonomy bytes differ from their hash.")
    return read_json(path)


def ensure(root):
    """Copy the repository's trusted catalog into a newly initialized local root."""
    target = Path(root) / "taxonomy"
    if not (target / "latest.json").exists():
        bundled = Path(__file__).resolve().parents[2] / "taxonomy"
        require(bundled.is_dir(), "unknown_taxonomy", "Run from the project checkout or download a challenge first.")
        shutil.copytree(bundled, target, dirs_exist_ok=True)
    digest = read_json(target / "latest.json")["taxonomy_hash"]
    load(root, digest)
    return digest


def normalize(value, catalog):
    aliases = {a["code"]: a["target"] for a in catalog["aliases"]}
    value = aliases.get(value, value)
    require(value in {c["code"] for c in catalog["categories"]}, "invalid_category", "Unknown category in this taxonomy snapshot.")
    return value


def validate_categories(meta, catalog):
    primary, secondary = meta["primary_category"], meta["secondary_categories"]
    require(isinstance(primary, str) and isinstance(secondary, list) and len(secondary) <= 2
            and all(isinstance(c, str) for c in secondary), "invalid_category", "Choose one primary and at most two secondary categories.")
    chosen = [primary, *secondary]
    require(len(set(chosen)) == len(chosen), "invalid_category", "Categories must be distinct.")
    for code in chosen:
        require(normalize(code, catalog) == code, "category_alias", "Normalize aliases before mining.")
