"""Import factual taxonomy labels/aliases from arXiv; review and commit the snapshot.

Usage: python scripts/update_taxonomy.py --html downloaded.html --date YYYY-MM-DD
No submission or CI job runs this importer or trusts a live arXiv response.
"""
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

from agent_preprints.codec import canonical, sha, write_json


class TaxonomyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.heading = None
        self.buffer = []
        self.group = self.archive = None
        self.groups, self.categories, self.aliases = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id") == "category_taxonomy_list":
            self.active = True
        if self.active and tag in ("h2", "h3", "h4"):
            self.heading, self.buffer = tag, []
            if tag == "h2":
                self.group = attrs["id"].removeprefix("accordion-head-grp_")

    def handle_data(self, text):
        if self.heading:
            self.buffer.append(text)
        if self.active:
            for source, target in re.findall(r"([a-z-]+(?:\.[A-Z]+)?) is an alias for ([a-z-]+(?:\.[A-Z]+)?)", text):
                self.aliases.append({"code": source, "target": target})

    def handle_endtag(self, tag):
        if tag != self.heading:
            return
        value = " ".join("".join(self.buffer).split())
        if tag == "h2":
            self.groups.append({"code": self.group, "name": value})
            self.archive = {"code": self.group, "name": value}
        elif tag == "h3":
            match = re.fullmatch(r"(.+?)\s*\(([^()]+)\)", value)
            if not match:
                raise ValueError("Unrecognized archive heading: " + value)
            self.archive = {"code": match[2], "name": match[1]}
        else:
            match = re.fullmatch(r"([^ ]+) \((.+)\)", value)
            if not match:
                raise ValueError("Unrecognized category heading: " + value)
            self.categories.append({"code": match[1], "name": match[2], "group": self.group,
                                    "archive": self.archive["code"], "archive_name": self.archive["name"]})
        self.heading = None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--root", default=".")
    args = p.parse_args()
    parser = TaxonomyParser()
    raw = Path(args.html).read_bytes()
    parser.feed(raw.decode())
    assert len(parser.groups) == 8 and len(parser.categories) > 140
    codes = {c["code"] for c in parser.categories}
    assert len(codes) == len(parser.categories)
    assert all(a["code"] in codes and a["target"] in codes for a in parser.aliases)
    aliases = {a["code"] for a in parser.aliases}
    result = {"schema": "markdownxiv-taxonomy-v1", "source": "https://arxiv.org/category_taxonomy",
              "retrieved_on": args.date, "source_sha256": sha(raw), "groups": parser.groups,
              "categories": [c for c in parser.categories if c["code"] not in aliases],
              "aliases": parser.aliases}
    payload = canonical(result) + b"\n"
    digest = sha(payload)
    path = Path(args.root) / "taxonomy" / (digest + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == payload
    else:
        path.write_bytes(payload)
    write_json(path.parent / "latest.json", {"taxonomy_hash": digest})
    print(digest, len(result["categories"]), "categories;", len(parser.aliases), "aliases")


if __name__ == "__main__":
    main()
