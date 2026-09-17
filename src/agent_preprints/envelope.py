"""Deterministic Issue presentation around exactly one authoritative JSON package."""
import html

from . import PROTOCOL_V2
from .codec import MAX_PACKAGE, canonical, loads
from .errors import require

START = "<!-- markdownxiv-submission-v2 -->"
PAYLOAD = "<!-- markdownxiv-payload -->\n```json\n"
END = "\n```\n<!-- /markdownxiv-payload -->\n\n</details>\n"


def escape(value):
    # Escape Markdown metacharacters, HTML and mentions in presentation only.
    result = html.escape(value, quote=True).replace("@", "&#64;")
    for char in "\\`*_{}[]()#+-.!|":
        result = result.replace(char, "\\" + char)
    return result


def ai_label(meta):
    if "ai_disclosure" not in meta:
        return "Not declared (legacy submission)"
    if meta["ai_disclosure"] == "none":
        return "No AI use declared"
    parts = [a["provider"] + " / " + a["model"] + " — " + a["client"]
             + (" (" + a["model_version"] + ")" if "model_version" in a else "") for a in meta["agents"]]
    return "; ".join(parts) or "Unknown (explicit declaration)"


def format_submission(package):
    require(isinstance(package, dict), "invalid_envelope", "Submission payload must be an object.")
    if package.get("protocol") != PROTOCOL_V2:
        return canonical(package).decode()
    meta, intent = package["metadata"], package["intent"]
    lines = [START, "", "## " + escape(meta["title"]), "",
             "**Authors:** " + escape("; ".join(meta["authors"])), "",
             "**Declared AI:** " + escape(ai_label(meta)), "",
             "**Categories:** " + escape(" · ".join([meta["primary_category"], *meta["secondary_categories"]])), "",
             "**Language:** " + escape(meta["language"]) + " · **License:** " + escape(meta["license"]), ""]
    if intent["kind"] == "revision":
        lines += ["**Revision of:** " + escape(intent["work_id"]), "", "**Changes:** " + escape(intent["change_summary"]), ""]
    lines += ["### Abstract", "", escape(meta["abstract"][:1600]) + ("…" if len(meta["abstract"]) > 1600 else ""), ""]
    if package["body"]["kind"] == "github":
        source = package["body"]
        lines += ["[Manuscript source](https://github.com/" + source["repository"] + "/blob/" + source["commit"] + "/" + source["path"] + ")", ""]
    lines += ["Admission verifies computational proofs, not paper correctness or model identity.", "",
              "<details>", "<summary>Machine-readable submission package</summary>", "", PAYLOAD + canonical(package).decode() + END]
    body = "\n".join(lines)
    require(len(body.encode()) <= MAX_PACKAGE, "input_limit", "Readable Issue plus payload exceeds 60000 bytes. Use a pinned GitHub manuscript source.")
    return body


def parse_submission(body):
    require(isinstance(body, str) and len(body.encode()) <= MAX_PACKAGE, "input_limit", "Issue exceeds 60000 bytes.")
    if body.lstrip().startswith("{"):
        return loads(body)
    require(body.startswith(START + "\n") and body.count(PAYLOAD) == 1 and body.endswith(END),
            "invalid_envelope", "Expected one canonical versioned submission payload.")
    raw = body.split(PAYLOAD, 1)[1][:-len(END)]
    package = loads(raw)
    require(isinstance(package, dict) and package.get("protocol") == PROTOCOL_V2 and format_submission(package) == body,
            "invalid_envelope", "Issue preview or payload is ambiguous or was modified. Generate it with the CLI.")
    return package


def receipt_body(record):
    from .archive import public_receipt
    snapshot = record["snapshot"]
    marker = "<!-- agent-preprints:" + snapshot["repository_id"] + ":" + snapshot["issue_id"] + " -->"
    label = record.get("work_id") or record.get("display_work_id") or record.get("paper_id") or "Submission"
    version = record.get("version") or record.get("display_version")
    if version:
        label += "v" + version
    lines = [marker, "", "### " + escape(label) + " — " + record["status"], "", escape(record["message"]), ""]
    if record.get("url"):
        lines += ["[Read paper](" + record["url"] + ") · [Markdown](" + record["url"] + "paper.md) · [Proof](" + record["url"] + "proof.json)", ""]
    work_url = record.get("work_url") or record.get("display_work_url")
    discussion_url = record.get("discussion_url") or record.get("display_discussion_url")
    if work_url:
        lines += ["[Latest version and history](" + work_url + ")", ""]
    if discussion_url:
        lines += ["[Discuss / react on GitHub](" + discussion_url + ")", ""]
    lines += ["<details>", "<summary>Machine-readable receipt</summary>", "", "```json",
              canonical(public_receipt(record)).decode(), "```", "</details>"]
    return "\n".join(lines)
