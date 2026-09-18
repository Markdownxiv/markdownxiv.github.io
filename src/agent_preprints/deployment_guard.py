"""Prevent a failed-job rerun from deploying an old artifact over newer archive state."""
import argparse
import hashlib
from pathlib import Path

from .codec import read_json, timestamp
from .errors import require


def source_digest(root):
    root = Path(root)
    paths = [root / "config" / "production.json"]
    for directory in ("papers", "challenges", "site", "src", "docs", "schemas", "works", "assets", "taxonomy", "prompts"):
        paths.extend(p for p in (root / directory).rglob("*") if p.is_file() and
                     "__pycache__" not in p.parts and p.suffix in (".json", ".md", ".py", ".css", ".js", ".svg", ".png", ".jpg", ".webp"))
    for name in ("agent-guide.md", "llms.txt", "requirements.lock", "pyproject.toml",
                 "renderer/package.json", "renderer/package-lock.json", "renderer/mathjax.cjs"):
        if (root / name).exists():
            paths.append(root / name)
    digest = hashlib.sha256(b"agent-preprints-site-source-v1\0")
    for path in sorted(paths):
        require(not path.is_symlink(), "unsafe_archive", "Site source must not contain symlinks.")
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big") + relative + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def guard(root, manifest):
    require(manifest["source_digest"] == source_digest(root), "stale_deployment",
            "Archive or build sources changed since this artifact was built. Run maintain or rerun all jobs to rebuild.")
    state = Path(root) / "state" / "published.json"
    if state.exists():
        previous = read_json(state).get("built_at")
        require(previous is None or timestamp(previous) <= timestamp(manifest["built_at"]), "stale_deployment",
                "A newer artifact has already been published; rebuild instead of redeploying stale social snapshots.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", default=".work/manifest.json")
    args = parser.parse_args()
    guard(args.root, read_json(args.manifest))
