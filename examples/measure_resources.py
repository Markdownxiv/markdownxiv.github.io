"""Synthetic LOCAL resource test, never a CPU calibration or production submission.

Tests exact 12 MiB admission (2 MiB Markdown + five 2 MiB PNGs), local archive/build,
and a separate 20 MP image. All proofs are development-only.
PNG padding uses a valid ancillary tEXt chunk; no network measurements are claimed.
"""
import argparse
import io
import os
import platform
import resource
import struct
import sys
import tempfile
import time
import zlib
from pathlib import Path

from PIL import Image
from agent_preprints import PROTOCOL_V2, assets, taxonomy, pow, poa
from agent_preprints.archive import capture, process
from agent_preprints.codec import canonical, read_json, sha, utcnow, write_json
from agent_preprints.epochs import epoch_path, rotate
from agent_preprints.envelope import format_submission
from agent_preprints.protocol import Context, prepare, verify
from agent_preprints.site import build
from reference_solvers import solve


def full_png():
    image = Image.frombytes("RGB", (1024, 675), os.urandom(1024 * 675 * 3))
    stream = io.BytesIO()
    image.save(stream, format="PNG", compress_level=1)
    raw = stream.getvalue()
    length = assets.MAX_IMAGE - len(raw) - 12
    assert length >= 8 and raw[-8:-4] == b"IEND"
    payload = b"padding\0" + b"x" * (length - 8)
    chunk = b"tEXt" + payload
    return raw[:-12] + struct.pack(">I", length) + chunk + struct.pack(">I", zlib.crc32(chunk)) + raw[-12:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".work/v2/resources.json")
    args = parser.parse_args()
    measurements = {}
    def measure(name, operation):
        start = time.perf_counter_ns()
        value = operation()
        measurements[name + "_ns"] = str(time.perf_counter_ns() - start)
        return value
    with tempfile.TemporaryDirectory(prefix="markdownxiv-resources-") as temporary:
        root = Path(temporary)
        now = utcnow()
        write_json(root / "config/production.json", {"enabled": False, "calibration_id": None,
                   "repository": "local/resources", "repository_id": "1", "site_url": "https://example.github.io/demo/"})
        epoch = rotate(root, now, True, protocol=PROTOCOL_V2)
        images = {"figures/figure-" + str(i) + ".png": full_png() for i in range(5)}
        entries = [{"path": name, "sha256": sha(raw), "size": str(len(raw)), "media_type": "image/png"} for name, raw in images.items()]
        start = "# Synthetic Resource Test\n\n" + "\n\n".join("![Synthetic random pixels](" + name + ")" for name in images) + "\n\n"
        prose = ("This paragraph contains synthetic text for a local capacity test. " * 20 + "\n\n").encode()
        body = start.encode() + (prose * 2000)[:assets.MAX_PAPER - len(start.encode())]
        assert len(body) == assets.MAX_PAPER and sum(map(len, images.values())) == assets.MAX_ASSETS
        source = {"kind": "github", "repository": "local/source", "commit": "a" * 40, "path": "paper.md"}
        meta = {"title": "Synthetic Resource Test", "abstract": "Local development-only capacity test.", "authors": ["Local test"],
                "license": "CC0-1.0", "primary_category": "cs.PF", "ai_disclosure": "unknown", "agents": []}
        package = prepare(body, meta, "1", "2", epoch, sha(epoch_path(root, epoch["epoch_id"]).read_bytes()), source,
                          entries=entries, catalog=taxonomy.load(root, epoch["taxonomy_hash"]))
        head = pow.header("1", package["epoch_hash"], "2", package["content_hash"], PROTOCOL_V2)
        package["nonce"] = pow.mine(head, epoch["target"])
        package["answers"] = solve(poa.sample(pow.seed(pow.verify(head, package["nonce"], epoch["target"])), epoch["poa_policy"]))
        measure("verify_12_mib", lambda: verify(package, root, Context("1", "2", now), False, supplied_body=body, supplied_assets=images))
        envelope = format_submission(package)
        snapshot = capture({"id": "1", "number": "1", "user": {"id": "2"}, "title": "[preprint] capacity test", "created_at": now, "body": envelope}, "1", "opened")
        receipt = measure("archive_12_mib", lambda: process(root, snapshot, False, supplied_body=body, supplied_assets=images))
        assert receipt["status"] == "accepted"
        measure("build_12_mib", lambda: build(root, root / "_site", "/", now))
        html = (root / "_site/p" / receipt["work_id"][3:] / "index.html").read_text()
        assert html.count('<img loading="lazy"') == 5 and '<article><pre>' not in html
        huge = io.BytesIO()
        Image.new("RGB", (5000, 4000), "white").save(huge, format="PNG")
        measure("decode_20_mp", lambda: assets.inspect_image(huge.getvalue()))
        measurements.update(manuscript_bytes=str(len(body)), image_total_bytes=str(sum(map(len, images.values()))),
                            envelope_bytes=str(len(envelope.encode())), site_bytes=str(sum(p.stat().st_size for p in (root / "_site").rglob("*") if p.is_file())),
                            parent_peak_rss_kib=str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                            child_peak_rss_kib=str(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss))
    write_json(args.out, {"schema": "markdownxiv-local-resource-measurement-v1", "measured_at": utcnow(),
                         "platform": platform.platform(), "python": platform.python_version(), "profile": "development",
                         "limitations": "Synthetic local bytes, valid PNG padding, no network or GitHub runner measurement; RSS units are Linux KiB.",
                         "measurements": measurements})
    print(canonical(read_json(args.out)).decode())


if __name__ == "__main__":
    main()
