"use strict";

const contents = document.querySelector(".reader-toc");
if (contents) {
  const mobile = matchMedia("(max-width: 850px)");
  const arrange = () => { contents.open = !mobile.matches; };
  arrange();
  mobile.addEventListener("change", arrange);
  const links = [...contents.querySelectorAll("nav a")];
  const headings = links.map(link => document.getElementById(decodeURIComponent(link.hash.slice(1)))).filter(Boolean);
  let waiting = false;
  const update = () => {
    waiting = false;
    const current = headings.filter(heading => heading.getBoundingClientRect().top <= 100).at(-1) || headings[0];
    for (const link of links) {
      if (current && decodeURIComponent(link.hash.slice(1)) === current.id) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
  };
  addEventListener("scroll", () => {
    if (!waiting) { waiting = true; requestAnimationFrame(update); }
  }, {passive: true});
  contents.addEventListener("click", event => {
    if (mobile.matches && event.target.closest("nav a")) contents.open = false;
  });
  update();
}

const printButton = document.querySelector(".reader-print");
if (printButton) {
  printButton.hidden = false;
  printButton.addEventListener("click", () => window.print());
}
