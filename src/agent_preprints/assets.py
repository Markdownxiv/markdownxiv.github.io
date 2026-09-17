"""Bounded, exact-byte image manifests. Submission bytes never become code."""
import io
import multiprocessing
import os
import re
from pathlib import Path

from .codec import decimal, fields, hexhash, sha
from .errors import Rejection, require

MIB = 1024 * 1024
MAX_PAPER = 2 * MIB
MAX_IMAGE = 2 * MIB
MAX_IMAGES = 20
MAX_ASSETS = 10 * MIB
MAX_PIXELS = 20_000_000
POLICY = {"paper_bytes": str(MAX_PAPER), "image_bytes": str(MAX_IMAGE), "image_count": str(MAX_IMAGES),
          "image_total_bytes": str(MAX_ASSETS), "image_pixels": str(MAX_PIXELS), "version_bytes": str(12 * MIB),
          "media_types": ["image/png", "image/jpeg", "image/webp"]}
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}


def logical_path(path):
    require(isinstance(path, str) and 1 <= len(path) <= 200 and re.fullmatch(r"[A-Za-z0-9_./-]+", path)
            and len(path.split("/")) <= 10 and all(p not in ("", ".", "..") for p in path.split("/"))
            and path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")),
            "unsafe_asset_path", "Images must use bounded relative PNG/JPEG/WebP paths without traversal.")
    return path


def filename(entry):
    return hexhash(entry["sha256"]) + "." + EXT[entry["media_type"]]


def validate_manifest(entries, max_image=MAX_IMAGE, max_total=MAX_ASSETS):
    require(isinstance(entries, list) and len(entries) <= MAX_IMAGES, "asset_limit", "At most 20 images.")
    total, paths = 0, []
    for item in entries:
        fields(item, ["path", "sha256", "size", "media_type"])
        paths.append(logical_path(item["path"]))
        hexhash(item["sha256"])
        total += decimal(item["size"], 1, max_image)
        require(isinstance(item["media_type"], str) and item["media_type"] in EXT,
                "invalid_image", "Unsupported image media type.")
        require(item["path"].lower().endswith({"image/png": (".png",), "image/jpeg": (".jpg", ".jpeg"),
                                               "image/webp": (".webp",)}[item["media_type"]]),
                "invalid_image", "Image path extension does not match declared media type.")
    require(paths == sorted(set(paths)) and total <= max_total, "asset_limit", "Manifest must be sorted, unique and within the image byte budget.")


def _inspect_worker(conn, body):
    try:
        # No credentials or source paths reach the native decoder subprocess.
        os.environ.clear()
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
        resource.setrlimit(resource.RLIMIT_AS, (512 * MIB, 512 * MIB))
        from PIL import Image
        import warnings
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        Image.MAX_IMAGE_PIXELS = MAX_PIXELS
        with Image.open(io.BytesIO(body), formats=["PNG", "JPEG", "WEBP"]) as image:
            if image.width * image.height > MAX_PIXELS or getattr(image, "n_frames", 1) != 1:
                raise ValueError("pixel/frame limit")
            fmt = image.format
            image.verify()
        with Image.open(io.BytesIO(body), formats=[fmt]) as image:
            image.load()  # Reject truncated or malformed compressed data, not just bad headers.
        conn.send({"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[fmt])
    except BaseException:
        conn.send(None)
    finally:
        conn.close()


def inspect_image(body, max_image=MAX_IMAGE):
    require(isinstance(body, bytes) and 0 < len(body) <= max_image, "asset_limit", "Image exceeds its byte limit.")
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_inspect_worker, args=(child, body))
    proc.start()
    child.close()
    media = None
    try:
        if parent.poll(6):
            try:
                media = parent.recv()
            except EOFError:
                pass
    finally:
        if proc.is_alive():
            proc.terminate()
        proc.join(timeout=1)
        parent.close()
    require(media in EXT, "invalid_image", "Image failed bounded static PNG/JPEG/WebP decoding (20 MP maximum).")
    return media


def _references_worker(conn, text):
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (4, 4))
        resource.setrlimit(resource.RLIMIT_AS, (512 * MIB, 512 * MIB))
        from markdown_it import MarkdownIt
        md = MarkdownIt("commonmark", {"html": False, "maxNesting": 24}).enable("table")
        found = set()
        def walk(tokens):
            for token in tokens:
                if token.type == "image":
                    found.add(logical_path(token.attrGet("src")))
                    require(len(found) <= MAX_IMAGES, "asset_limit", "At most 20 images.")
                if token.children:
                    walk(token.children)
        walk(md.parse(text))
        conn.send(sorted(found))
    except BaseException:
        conn.send(None)
    finally:
        conn.close()


def references(body):
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_references_worker, args=(child, body.decode("utf-8")))
    proc.start()
    child.close()
    result = None
    try:
        if parent.poll(7):
            try:
                result = parent.recv()
            except EOFError:
                pass
    finally:
        if proc.is_alive():
            proc.terminate()
        proc.join(timeout=1)
        parent.close()
    require(result is not None, "invalid_asset_references", "Unsupported image references or Markdown parsing limit exceeded.")
    return result


def read_local(directory, relative, max_image=MAX_IMAGE):
    root = Path(directory).resolve()
    path = root
    for part in logical_path(relative).split("/"):
        path = path / part
        require(not path.is_symlink(), "unsafe_asset_path", "Local asset paths cannot traverse symlinks.")
    require(path.is_file() and path.stat().st_size <= max_image, "asset_limit", "Local image missing or too large.")
    return path.read_bytes()


def collect_local(body, directory, max_image=MAX_IMAGE, max_total=MAX_ASSETS):
    entries, data = [], {}
    for name in references(body):
        raw = read_local(directory, name, max_image)
        entries.append({"path": name, "sha256": sha(raw), "size": str(len(raw)), "media_type": inspect_image(raw, max_image)})
        data[name] = raw
    validate_manifest(entries, max_image, max_total)
    return entries, data


def verify(body, entries, obtain, max_image=MAX_IMAGE, max_total=MAX_ASSETS):
    validate_manifest(entries, max_image, max_total)
    require(references(body) == [e["path"] for e in entries], "asset_manifest_mismatch", "Every image reference must match the manifest; unused assets are forbidden.")
    data = {}
    for entry in entries:
        raw = obtain(entry)
        require(isinstance(raw, bytes) and len(raw) == int(entry["size"]) and sha(raw) == entry["sha256"],
                "asset_hash_mismatch", "Image bytes differ from the PoW-bound manifest.")
        require(inspect_image(raw, max_image) == entry["media_type"], "invalid_image", "Decoded image type differs from manifest.")
        data[entry["path"]] = raw
    return data
