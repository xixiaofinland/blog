(() => {
  const darkThemes = ["ayu", "navy", "coal"];
  const lightThemes = ["light", "rust"];

  const classList = document.getElementsByTagName("html")[0].classList;

  let lastThemeWasLight = true;
  for (const cssClass of classList) {
    if (darkThemes.includes(cssClass)) {
      lastThemeWasLight = false;
      break;
    }
  }

  // mdBook renders ```mermaid as <pre><code class="language-mermaid">.
  // Mermaid needs <div class="mermaid"> — transform before initializing.
  document.querySelectorAll("code.language-mermaid").forEach((code) => {
    const pre = code.parentElement;
    const div = document.createElement("div");
    div.className = "mermaid";
    div.textContent = code.textContent;
    pre.replaceWith(div);
  });

  const theme = lastThemeWasLight ? "default" : "dark";
  mermaid.initialize({ startOnLoad: true, theme });

  // Simplest way to make mermaid re-render the diagrams in the new theme is via refreshing the page

  for (const darkTheme of darkThemes) {
    document.getElementById(darkTheme).addEventListener("click", () => {
      if (lastThemeWasLight) {
        window.location.reload();
      }
    });
  }

  for (const lightTheme of lightThemes) {
    document.getElementById(lightTheme).addEventListener("click", () => {
      if (!lastThemeWasLight) {
        window.location.reload();
      }
    });
  }
})();
