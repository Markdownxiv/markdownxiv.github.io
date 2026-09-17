"use strict";
const categorySearch = document.querySelector("#category-search");
if (categorySearch) {
  categorySearch.addEventListener("input", () => {
    const words = categorySearch.value.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const group of document.querySelectorAll("[data-subject-group]")) {
      let visible = 0;
      const groupName = group.querySelector("h2").textContent.toLocaleLowerCase();
      for (const row of group.querySelectorAll(".category-row")) {
        row.hidden = !words.every(word => (groupName + " " + row.textContent.toLocaleLowerCase()).includes(word));
        visible += Number(!row.hidden);
      }
      group.hidden = visible === 0;
      count += visible;
    }
    document.querySelector("#no-subjects").hidden = count !== 0;
  });
}

const results = document.querySelector("#search-results");
if (results) {
  const parameters = new URLSearchParams(location.search);
  const query = parameters.get("q") || "";
  document.querySelector("#global-search").value = query;
  const node = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  const localLink = (text, path) => {
    const element = node("a", text);
    const address = new URL(path, location.origin);
    if (address.origin === location.origin && address.pathname.startsWith(new URL(".", new URL(results.dataset.index, location.origin)).pathname)) {
      element.href = address.href;
    }
    return element;
  };
  const pageSize = 50;
  async function runSearch() {
    try {
      const response = await fetch(results.dataset.index, {credentials: "omit"});
      if (!response.ok) throw new Error("Unavailable index");
      const index = await response.json();
      if (!Array.isArray(index.papers)) throw new Error("Invalid index");
      const words = query.toLocaleLowerCase().split(/\s+/).filter(Boolean);
      const matching = index.papers.filter(paper => {
        const content = [paper.work_id, paper.title, paper.abstract, ...paper.authors, paper.primary_category,
          ...paper.secondary_categories, ...paper.tags, paper.declared_ai].join(" ").toLocaleLowerCase();
        return words.every(word => content.includes(word));
      });
      const pageCount = Math.max(1, Math.ceil(matching.length / pageSize));
      const requested = Number(parameters.get("page") || "1");
      const current = Number.isSafeInteger(requested) ? Math.min(pageCount, Math.max(1, requested)) : 1;
      const toolbar = () => {
        const bar = node("div", undefined, "list-tools");
        const first = matching.length ? (current - 1) * pageSize + 1 : 0;
        bar.append(node("span", `${first}-${Math.min(current * pageSize, matching.length)} of ${matching.length}`));
        if (pageCount > 1) {
          const navigation = node("nav", undefined, "pagination");
          navigation.setAttribute("aria-label", "Search pages");
          const link = (label, page) => {
            const target = new URLSearchParams({q: query, page: String(page)});
            return localLink(label, location.pathname + "?" + target);
          };
          if (current > 1) navigation.append(link("Previous", current - 1));
          const pages = [...new Set([1, pageCount, current - 2, current - 1, current, current + 1, current + 2])]
            .filter(page => page >= 1 && page <= pageCount).sort((a, b) => a - b);
          let previous = 0;
          for (const page of pages) {
            if (previous && page - previous > 1) navigation.append(node("span", "..."));
            if (page === current) {
              const selected = node("span", String(page));
              selected.setAttribute("aria-current", "page");
              navigation.append(selected);
            } else navigation.append(link(String(page), page));
            previous = page;
          }
          if (current < pageCount) navigation.append(link("Next", current + 1));
          bar.append(navigation);
        }
        return bar;
      };
      results.replaceChildren(toolbar());
      if (!matching.length) results.append(node("p", "No matching papers.", "empty"));
      const list = node("ol", undefined, "papers");
      for (const paper of matching.slice((current - 1) * pageSize, current * pageSize)) {
        const row = node("li", undefined, "paper-row");
        const identity = node("div", undefined, "paper-id");
        const formats = node("span", undefined, "paper-formats");
        formats.append(localLink("abs", paper.url), node("span", "|"), localLink("md", paper.markdown_url));
        identity.append(node("span", paper.work_id + "v" + paper.version), formats);
        const title = node("h2");
        title.append(localLink(paper.title, paper.url));
        const authors = node("p", undefined, "authors");
        paper.authors.forEach((name, i) => {
          if (i) authors.append(document.createTextNode(", "));
          let author = node("span", name);
          try {
            const address = new URL((paper.author_homepages || [])[i]);
            if (address.protocol === "https:" && !address.username && !address.password) {
              author = node("a", name);
              author.href = address.href;
              author.rel = "nofollow noopener noreferrer";
            }
          } catch (_) { /* Missing homepages remain plain names. */ }
          authors.append(author);
        });
        row.append(identity, title, authors, node("p", paper.received_at.slice(0, 10) + " / " +
          [paper.primary_category, ...paper.secondary_categories].filter(Boolean).join(", "), "paper-details"));
        list.append(row);
      }
      results.append(list, toolbar());
    } catch (_) {
      const retry = node("button", "Retry");
      retry.type = "button";
      retry.addEventListener("click", runSearch);
      results.replaceChildren(node("p", "Search is temporarily unavailable."), retry);
    }
  }
  runSearch();
}

const search = document.querySelector("#search");
if (search) {
  const papers = [...document.querySelectorAll("[data-paper]")];
  search.addEventListener("input", () => {
    const terms = search.value.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const paper of papers) {
      const match = terms.every(term => paper.textContent.toLocaleLowerCase().includes(term));
      paper.hidden = !match;
      count += Number(match);
    }
    const empty = document.querySelector("#no-results");
    if (empty) empty.hidden = count !== 0;
  });
}
const challenge = document.querySelector("#challenge-status");
if (challenge && challenge.dataset.expires) {
  const check = () => {
    if (Date.now() >= Date.parse(challenge.dataset.expires)) {
      challenge.textContent = "expired — waiting for a new published epoch";
    }
  };
  check();
  setInterval(check, 30000);
}
