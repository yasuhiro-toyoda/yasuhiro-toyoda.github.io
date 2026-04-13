(() => {
  const header = document.querySelector("[data-site-header]");

  if (!header) {
    return;
  }

  const mobileQuery = window.matchMedia("(max-width: 800px)");
  const root = document.documentElement;
  let lastScrollY = Math.max(window.scrollY, 0);
  let isHidden = false;
  let frameId = null;

  const setHeaderHeight = () => {
    root.style.setProperty("--site-header-height", `${header.offsetHeight}px`);
  };

  const showHeader = () => {
    if (!isHidden) {
      return;
    }

    header.classList.remove("site-header--hidden");
    isHidden = false;
  };

  const hideHeader = () => {
    if (isHidden) {
      return;
    }

    header.classList.add("site-header--hidden");
    isHidden = true;
  };

  const syncHeader = () => {
    frameId = null;
    setHeaderHeight();

    const currentScrollY = Math.max(window.scrollY, 0);

    if (!mobileQuery.matches) {
      showHeader();
      lastScrollY = currentScrollY;
      return;
    }

    const threshold = header.offsetHeight;
    const delta = currentScrollY - lastScrollY;

    if (currentScrollY <= threshold || delta < -6) {
      showHeader();
    } else if (delta > 6) {
      hideHeader();
    }

    lastScrollY = currentScrollY;
  };

  const requestSync = () => {
    if (frameId !== null) {
      return;
    }

    frameId = window.requestAnimationFrame(syncHeader);
  };

  if ("ResizeObserver" in window) {
    const resizeObserver = new ResizeObserver(() => {
      setHeaderHeight();
      requestSync();
    });

    resizeObserver.observe(header);
  }

  if ("addEventListener" in mobileQuery) {
    mobileQuery.addEventListener("change", requestSync);
  } else if ("addListener" in mobileQuery) {
    mobileQuery.addListener(requestSync);
  }

  setHeaderHeight();
  syncHeader();

  window.addEventListener("scroll", requestSync, { passive: true });
  window.addEventListener("resize", requestSync, { passive: true });
})();
