"use strict";
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
