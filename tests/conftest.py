"""
pytest fixtures for browser management.
Centralises browser setup/teardown so test files stay clean and focused.

WHY conftest.py?
- pytest automatically loads this file
- Fixtures here are available to ALL tests
- Keeps test files clean and focused

ASYNCIO NOTE:
On Windows / Python 3.14, calling sync_playwright() inside a fixture fails
because the ProactorEventLoop is already marked as "running" by the time
fixtures execute. playwright_state.initialize() is therefore called once in
pytest_sessionstart (before any asyncio activity) and ALL fixtures obtain the
browser via _pw_state.get_browser() — never via sync_playwright().
"""

import sys
import os
import base64
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

os.makedirs("reports/html", exist_ok=True)
os.makedirs("reports/allure-results", exist_ok=True)
os.makedirs("artifacts/screenshots", exist_ok=True)
os.makedirs("artifacts/videos", exist_ok=True)
os.makedirs("artifacts/traces", exist_ok=True)

# ---------------------------------------------------------------------------
# Shared playwright state — see playwright_state.py for details.
# Only this conftest calls initialize()/teardown(); sub-conftests use
# get_browser() / get_playwright() to obtain the already-running instances.
# ---------------------------------------------------------------------------
import playwright_state as _pw_state
from utils.custom_reporter import CustomReporter

_reporter = None


def pytest_sessionstart(session) -> None:
    _pw_state.initialize()
    global _reporter
    _reporter = CustomReporter(
        report_dir="reports/custom",
        title="Playwright Test Report",
    )


def pytest_sessionfinish(session, exitstatus) -> None:
    _pw_state.teardown()
    if _reporter:
        report = _reporter.generate_report()
        json_path = _reporter.save_json(report)
        html_path = _reporter.save_html(report)
        _reporter.print_summary(report)
        print(f"\n JSON Report: {json_path}")
        print(f" HTML Report: {html_path}")


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from typing import Generator
from collections.abc import Iterator

import pytest
from playwright.sync_api import Page

from utils.screenshot_manager import ScreenshotManager
from utils.video_manager import VideoManager
from utils.trace_manager import TraceManager
from utils.wait_helpers import WaitHelper

from pages import (
    LoginPage,
    InventoryPage,
    CartPage,
    CheckoutPage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
)
from pages.components import Header, SidebarMenu

try:
    import pytest_html
except ImportError:
    pytest_html = None


# ============================================================
# UTILITY FIXTURES
# ============================================================

@pytest.fixture
def wait_helper(page):
    """Provides utility methods for waiting on dynamic elements."""
    return WaitHelper(page)


# ============================================================
# SESSION SCOPE — created once for the entire test run
# ============================================================

@pytest.fixture(scope="session")
def playwright_instance():
    """
    SESSION SCOPE: Single Playwright instance for all tests.

    Lifecycle: created once at session start, destroyed at session end.
    Cleanup is handled by pytest_sessionfinish / playwright_state.teardown().
    """
    print("\n[SESSION] Playwright ready...")
    yield _pw_state.get_playwright()
    print("\n[SESSION] Playwright cleanup handled by session hooks...")


@pytest.fixture(scope="session")
def browser_type_name():
    """
    SESSION SCOPE: Browser type — override via BROWSER env var.
    Defaults to 'chromium'.
    """
    return os.environ.get("BROWSER", "chromium")


@pytest.fixture(scope="session")
def browser_instance(browser_type_name):
    """
    SESSION SCOPE: Single browser instance reused across all tests.

    Faster than launching per-test; cookies are cleared per context so tests
    remain isolated.
    """
    print(f"\n[SESSION] Browser ready ({browser_type_name})...")
    yield _pw_state.get_browser()
    print("\n[SESSION] Browser cleanup handled by session hooks...")


@pytest.fixture(scope="session")
def browser():
    """
    SESSION SCOPE: Alias for the shared browser instance.

    Convenience name used by fixtures that don't need browser_type_name.
    """
    yield _pw_state.get_browser()


@pytest.fixture(scope="session")
def test_data():
    """
    SESSION SCOPE: Shared test data loaded once per run.

    In a real project this might come from a JSON/YAML file or a database.
    """
    print("\n[SESSION] Loading test data...")
    return {
        "users": {
            "standard": {
                "username": "standard_user",
                "password": "secret_sauce",
            },
            "locked": {
                "username": "locked_out_user",
                "password": "secret_sauce",
            },
            "problem": {
                "username": "problem_user",
                "password": "secret_sauce",
            },
            "performance": {
                "username": "performance_glitch_user",
                "password": "secret_sauce",
            },
        },
        "products": {
            "backpack": {
                "name": "Sauce Labs Backpack",
                "price": "$29.99",
                "id": "sauce-labs-backpack",
            },
            "bike_light": {
                "name": "Sauce Labs Bike Light",
                "price": "$9.99",
                "id": "sauce-labs-bike-light",
            },
            "onesie": {
                "name": "Sauce Labs Onesie",
                "price": "$7.99",
                "id": "sauce-labs-onesie",
            },
        },
        "urls": {
            "base": "https://www.saucedemo.com",
            "inventory": "https://www.saucedemo.com/inventory.html",
            "cart": "https://www.saucedemo.com/cart.html",
        },
    }


# ============================================================
# MODULE SCOPE — created once per test file
# ============================================================

@pytest.fixture(scope="module")
def module_browser_context(browser_instance):
    """
    MODULE SCOPE: Browser context shared within a test file.

    Lifecycle: created before the first test in the file, destroyed after the
    last. Use when tests in the same file legitimately share cookies/storage.
    """
    print("\n[MODULE] Creating browser context...")
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
    )
    yield context
    print("\n[MODULE] Closing browser context...")
    context.close()


# ============================================================
# CLASS SCOPE — created once per test class
# ============================================================

@pytest.fixture(scope="class")
def class_authenticated_context(browser_instance, test_data):
    """
    CLASS SCOPE: Authenticated session shared across all tests in a class.

    Use when an expensive login (OAuth, 2FA) should be performed once for a
    class rather than for each individual test.
    """
    print("\n[CLASS] Creating authenticated context...")
    context = browser_instance.new_context()
    page = context.new_page()

    base_url = test_data["urls"]["base"]
    user = test_data["users"]["standard"]

    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")

    yield {"context": context, "page": page}

    print("\n[CLASS] Closing authenticated context...")
    context.close()


# ============================================================
# FUNCTION SCOPE — created for each test (DEFAULT)
# ============================================================

@pytest.fixture(scope="function")
def browser_context(browser_instance):
    """
    FUNCTION SCOPE: Fresh isolated context for each test.

    Provides clean cookies/storage on every test. This is the recommended
    default for most tests.
    """
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context) -> Iterator[Page]:
    """
    FUNCTION SCOPE: Fresh page for each test.

    Primary page fixture — used by the vast majority of tests.
    """
    pg = browser_context.new_page()
    pg.set_default_timeout(30000)
    pg.set_default_navigation_timeout(30000)
    yield pg
    # Page is closed automatically when browser_context closes.


@pytest.fixture(scope="function")
def context(browser, request):
    """
    FUNCTION SCOPE: Context with video recording enabled.

    An opt-in alternative to the plain browser_context fixture for tests that
    need video output.
    """
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir=VIDEOS_DIR,
        record_video_size={"width": 1280, "height": 720},
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def slow_page(browser):
    """
    FUNCTION SCOPE: Page with extended timeouts for slow pages.

    Use when the AUT has known latency (e.g. staging environment).
    """
    ctx = browser.new_context()
    pg = ctx.new_page()
    pg.set_default_timeout(60000)
    yield pg
    ctx.close()


@pytest.fixture(scope="function")
def page_with_downloads(browser, tmp_path):
    """
    FUNCTION SCOPE: Page configured to accept and save downloads.

    The download directory is available via page.download_dir.
    """
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    ctx = browser.new_context(accept_downloads=True)
    pg = ctx.new_page()
    pg.download_dir = str(download_dir)
    yield pg
    ctx.close()


# ============================================================
# PAGE STATE FIXTURES
# ============================================================

@pytest.fixture
def logged_in_page(page, test_data):
    """
    FUNCTION SCOPE: Page with a completed standard-user login.

    Each test gets a fresh login — use class_authenticated_context when you
    need to share an expensive login across multiple tests.
    """
    base_url = test_data["urls"]["base"]
    user = test_data["users"]["standard"]

    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")

    return page


@pytest.fixture
def page_with_cart(logged_in_page, test_data):
    """
    FUNCTION SCOPE: Logged-in page with the backpack added to the cart.

    Demonstrates fixture chaining / composition.
    """
    product = test_data["products"]["backpack"]
    logged_in_page.locator(
        f"[data-test='add-to-cart-{product['id']}']"
    ).click()
    return logged_in_page


# ============================================================
# FACTORY FIXTURES
# ============================================================

@pytest.fixture
def create_user_session(browser):
    """Factory for creating multiple independent user sessions within a test."""
    contexts = []

    def _create(user_type="standard"):
        users = {
            "standard": ("standard_user", "secret_sauce"),
            "problem": ("problem_user", "secret_sauce"),
        }
        username, password = users[user_type]
        ctx = browser.new_context()
        pg = ctx.new_page()
        contexts.append(ctx)
        pg.goto("https://www.saucedemo.com/")
        pg.get_by_placeholder("Username").fill(username)
        pg.get_by_placeholder("Password").fill(password)
        pg.get_by_role("button", name="Login").click()
        pg.wait_for_url("**/inventory.html")
        return pg

    yield _create

    for ctx in contexts:
        ctx.close()


@pytest.fixture(params=[
    pytest.param("sauce-labs-backpack", id="backpack"),
    pytest.param("sauce-labs-bike-light", id="bike_light"),
])
def product_id(request):
    """Parametrized fixture — runs the test once per product."""
    return request.param


# ============================================================
# PAGE OBJECT FIXTURES
# ============================================================

@pytest.fixture
def login_page(page) -> LoginPage:
    """Login Page Object."""
    return LoginPage(page)


@pytest.fixture
def inventory_page(page) -> InventoryPage:
    """Inventory Page Object."""
    return InventoryPage(page)


@pytest.fixture
def cart_page(page) -> CartPage:
    """Cart Page Object."""
    return CartPage(page)


@pytest.fixture
def checkout_page(page) -> CheckoutPage:
    """Checkout Step One Page Object."""
    return CheckoutPage(page)


@pytest.fixture
def checkout_step_two_page(page) -> CheckoutStepTwoPage:
    """Checkout Step Two Page Object."""
    return CheckoutStepTwoPage(page)


@pytest.fixture
def checkout_complete_page(page) -> CheckoutCompletePage:
    """Checkout Complete Page Object."""
    return CheckoutCompletePage(page)


# ============================================================
# COMPONENT FIXTURES
# ============================================================

@pytest.fixture
def header(page) -> Header:
    """Header component fixture."""
    return Header(page)


@pytest.fixture
def sidebar_menu(page) -> SidebarMenu:
    """Sidebar menu component fixture."""
    return SidebarMenu(page)


# ============================================================
# CONVENIENCE FIXTURES (chained page state)
# ============================================================

@pytest.fixture
def logged_in_user(login_page, inventory_page) -> InventoryPage:
    """
    Returns an InventoryPage for a logged-in standard user.

    Usage:
        def test_add_to_cart(logged_in_user):
            logged_in_user.add_to_cart_by_name("Sauce Labs Backpack")
    """
    login_page.navigate()
    login_page.login_as_standard_user()
    assert inventory_page.is_loaded()
    return inventory_page


@pytest.fixture
def user_with_cart(logged_in_user, cart_page) -> CartPage:
    """Returns a CartPage with one item already added."""
    logged_in_user.add_to_cart_by_name("Sauce Labs Backpack")
    logged_in_user.go_to_cart()
    assert cart_page.is_loaded()
    return cart_page


@pytest.fixture
def user_at_checkout(user_with_cart, checkout_page) -> CheckoutPage:
    """Returns a CheckoutPage ready for information entry."""
    user_with_cart.proceed_to_checkout()
    assert checkout_page.is_loaded()
    return checkout_page


# ============================================================
# ARTIFACT DIRECTORIES
# ============================================================

SCREENSHOTS_DIR = "screenshots"
VIDEOS_DIR = "videos"
TRACES_DIR = "traces"

for _dir in [SCREENSHOTS_DIR, VIDEOS_DIR, TRACES_DIR]:
    os.makedirs(_dir, exist_ok=True)


# ============================================================
# TRACING FIXTURES
# ============================================================

@pytest.fixture(scope="function")
def context_with_tracing(browser, request):
    """
    FUNCTION SCOPE: Context with tracing enabled; trace saved only on failure.
    """
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
    )
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield ctx

    test_name = request.node.name
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    if test_failed:
        trace_path = (
            f"{TRACES_DIR}/{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        ctx.tracing.stop(path=trace_path)
        print(f"\n Trace saved: {trace_path}")
    else:
        ctx.tracing.stop()

    ctx.close()


@pytest.fixture(scope="function")
def page_with_tracing(context_with_tracing):
    """Page backed by a tracing-enabled context."""
    return context_with_tracing.new_page()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _capture_screenshot(page: Page, test_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
    path = f"{SCREENSHOTS_DIR}/{safe_name}_{timestamp}.png"
    try:
        page.screenshot(path=path, full_page=True)
        print(f"\n Screenshot saved: {path}")
        return path
    except Exception as exc:
        print(f"\n Failed to capture screenshot: {exc}")
        return ""


def _save_page_content(page: Page, test_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
    path = f"{SCREENSHOTS_DIR}/{safe_name}_{timestamp}.html"
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page.content())
        print(f" HTML saved: {path}")
        return path
    except Exception as exc:
        print(f"\n Failed to save HTML: {exc}")
        return ""


# ============================================================
# PYTEST HOOKS
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Unified report hook — runs first so rep_call is available to all fixtures.

    Responsibilities:
    1. Attach rep_{when} to the item node (fixtures use request.node.rep_call).
    2. Record result in the custom reporter.
    3. Embed a failure screenshot into the pytest-html report (when available).
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call":
        return

    # Custom reporter
    global _reporter
    if _reporter:
        if report.passed:
            status = "passed"
        elif report.failed:
            status = "failed"
        elif report.skipped:
            status = "skipped"
        else:
            status = "unknown"

        error_message = (
            str(report.longrepr)
            if report.failed and hasattr(report, "longrepr")
            else ""
        )
        _reporter.create_result(
            name=item.name,
            status=status,
            duration=report.duration,
            error_message=error_message,
        )

    # pytest-html screenshot embedding
    if report.failed and pytest_html:
        page = None
        for fixture_name in ["page", "page_with_video", "traced_page", "auto_screenshot"]:
            if fixture_name in item.fixturenames:
                page = item.funcargs.get(fixture_name)
                if page:
                    break
        if page:
            try:
                screenshot_bytes = page.screenshot(full_page=True)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                extra = getattr(report, "extra", [])
                extra.append(pytest_html.extras.png(screenshot_b64))
                report.extra = extra
            except Exception as exc:
                print(f"Failed to capture screenshot for report: {exc}")


# ============================================================
# PYTEST CONFIGURATION HOOKS
# ============================================================

def pytest_configure(config):
    """Register custom markers and inject metadata into pytest-html."""
    if hasattr(config, "_metadata"):
        config._metadata["Project"] = "Playwright Learning"
        config._metadata["Tester"] = os.environ.get("USER", "Unknown")
        config._metadata["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    config.addinivalue_line("markers", "smoke: Quick sanity tests")
    config.addinivalue_line("markers", "regression: Full regression tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "flaky: Known flaky tests")
    config.addinivalue_line("markers", "wip: Work in progress")
    config.addinivalue_line("markers", "debug: Mark test for debugging")


def pytest_html_report_title(report):
    """Customise the pytest-html report title."""
    report.title = "Playwright Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """Add a custom summary section to the pytest-html report."""
    prefix.extend([
        "<p>Test execution completed.</p>",
        "<p>View traces with: <code>playwright show-trace artifacts/traces/trace.zip</code></p>",
    ])


def pytest_collection_modifyitems(config, items):
    """Auto-apply markers based on the test file's directory path."""
    for item in items:
        path = str(item.fspath)
        if "smoke" in path:
            item.add_marker(pytest.mark.smoke)
        elif "regression" in path:
            item.add_marker(pytest.mark.regression)


# ============================================================
# DEBUG FIXTURES
# ============================================================

@pytest.fixture
def debug_page(browser, request):
    """
    Page fixture with all debugging features enabled:
    tracing, video recording, screenshots, and HTML capture on failure.
    """
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir=VIDEOS_DIR,
    )
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    pg = ctx.new_page()
    pg.set_default_timeout(30000)

    yield pg

    test_name = request.node.name
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    if test_failed:
        _capture_screenshot(pg, test_name)
        _save_page_content(pg, test_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
        trace_path = f"{TRACES_DIR}/{safe_name}_{timestamp}.zip"
        ctx.tracing.stop(path=trace_path)
        print(f" Trace saved: {trace_path}")
    else:
        ctx.tracing.stop()

    ctx.close()

    if pg.video:
        print(f" Video saved: {pg.video.path()}")


# ============================================================
# SCREENSHOT FIXTURES
# ============================================================

@pytest.fixture
def screenshot_manager(request):
    """
    Provides a ScreenshotManager for manual screenshot capture within a test.

    Usage:
        def test_something(page, screenshot_manager):
            screenshot_manager.capture(page, "step_1", "Description")
    """
    manager = ScreenshotManager(
        base_dir="artifacts/screenshots",
        test_name=request.node.name,
    )
    yield manager
    manager.save_metadata()


@pytest.fixture
def auto_screenshot(page, request):
    """
    Wraps the page fixture and captures a full-page screenshot on failure.
    """
    manager = ScreenshotManager(
        base_dir="artifacts/screenshots",
        test_name=request.node.name,
    )
    page._screenshot_manager = manager

    yield page

    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if test_failed:
        manager.capture(page, "failure_final_state", "Page state at failure", full_page=True)
    manager.save_metadata()
    manager.cleanup(keep_on_failure=True, test_passed=not test_failed)


# ============================================================
# VIDEO FIXTURES
# ============================================================

_video_manager = VideoManager()


@pytest.fixture
def page_with_video(browser, request):
    """
    Page fixture with video recording; video is kept only if the test fails.
    """
    ctx = _video_manager.create_recording_context(
        browser,
        request.node.name,
        viewport={"width": 1280, "height": 720},
    )
    pg = ctx.new_page()

    yield pg

    ctx.close()

    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if test_failed:
        print(f" Video saved for failed test: {request.node.name}")
    else:
        if hasattr(ctx, "_video_dir"):
            import shutil
            if ctx._video_dir.exists():
                shutil.rmtree(ctx._video_dir)


@pytest.fixture
def always_record_video(browser, request):
    """Page fixture that always keeps the video recording."""
    ctx = _video_manager.create_recording_context(
        browser,
        request.node.name,
    )
    pg = ctx.new_page()

    yield pg

    ctx.close()

    if hasattr(ctx, "_video_dir"):
        print(f" Video saved: {ctx._video_dir}")


# ============================================================
# TRACE FIXTURES
# ============================================================

_trace_manager = TraceManager()


@pytest.fixture
def traced_context(browser, request):
    """
    Browser context with tracing; trace is saved only if the test fails.
    """
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    _trace_manager.start_tracing(ctx, request.node.name)

    yield ctx

    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    _trace_manager.stop_and_save(ctx, request.node.name, save=test_failed)
    ctx.close()


@pytest.fixture
def traced_page(traced_context):
    """Page backed by a traced_context (trace saved on failure)."""
    return traced_context.new_page()


@pytest.fixture
def always_trace(browser, request):
    """Context that always saves a trace — useful for CI or critical tests."""
    ctx = browser.new_context()
    _trace_manager.start_tracing(ctx, request.node.name)

    yield ctx

    _trace_manager.stop_and_save(ctx, request.node.name, save=True)
    ctx.close()
