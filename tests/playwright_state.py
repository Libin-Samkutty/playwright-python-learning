"""
Shared playwright state for the test suite.

On Windows / Python 3.14, calling sync_playwright() once causes the
ProactorEventLoop to appear "running" in the main thread.  Any subsequent
call to sync_playwright() therefore raises:
  "Playwright Sync API inside the asyncio loop."

To avoid this, playwright is initialised ONCE from the root conftest's
pytest_sessionstart hook (which fires before any asyncio loop activity),
and the single browser instance is shared across all conftest files via
this module.

Usage in conftest files:
    from playwright_state import get_browser, get_playwright
    # Then use get_browser() wherever a Browser object is needed.
"""

_state: dict = {}


def initialize() -> None:
    """Start playwright and launch a browser.  Safe to call multiple
    times; subsequent calls are no-ops once the state is populated.
    The browser type is determined by the BROWSER env var (default: chromium)."""
    if _state:
        return
    try:
        import os
        from playwright.sync_api import sync_playwright
        browser_name = os.environ.get("BROWSER", "chromium")
        cm = sync_playwright()
        pw = cm.__enter__()
        _state["cm"] = cm
        _state["pw"] = pw
        browser_type = getattr(pw, browser_name)
        _state["browser"] = browser_type.launch(headless=True, slow_mo=0)
    except Exception as exc:
        _state["error"] = str(exc)


def get_browser():
    """Return the shared Browser instance (raises RuntimeError if not ready)."""
    if "browser" not in _state:
        raise RuntimeError(
            "Shared browser not initialised. "
            f"Error: {_state.get('error', 'unknown')}"
        )
    return _state["browser"]


def get_playwright():
    """Return the shared Playwright instance (raises RuntimeError if not ready)."""
    if "pw" not in _state:
        raise RuntimeError(
            "Shared playwright not initialised. "
            f"Error: {_state.get('error', 'unknown')}"
        )
    return _state["pw"]


def teardown() -> None:
    """Close the browser and stop playwright.  Called from pytest_sessionfinish."""
    if "browser" in _state:
        try:
            _state["browser"].close()
        except Exception:
            pass
    if "cm" in _state:
        try:
            _state["cm"].__exit__(None, None, None)
        except Exception:
            pass
    _state.clear()
