"""
tests/functional/conftest.py
Fixtures for functional tests demonstrating advanced pytest patterns.

WHY pytest_sessionstart?
========================
On Python 3.14 / Windows, pytest-xdist workers always have an asyncio event
loop running by the time function-scoped fixtures execute.
sync_playwright() raises "Playwright Sync API inside the asyncio loop" in that
environment.  The only reliable window to call sync_playwright() is during
pytest_sessionstart(), which runs at worker startup BEFORE any asyncio
infrastructure is set up.  Fixtures then reuse the pre-created browser.

NOTE: multi_browser / responsive_page etc. all use the pre-created Chromium
browser.  The parametrized fixture names (firefox, webkit) still run 3 times
to demonstrate the fixture pattern, but the actual browser is Chromium.
For true cross-browser runs remove xdist (-n0) so sync_playwright() can
be called freely.
"""

import pytest
import playwright_state as _pw_state


# ---------------------------------------------------------------------------
# Browser helper — delegates to the single shared playwright instance that
# root conftest initialises in pytest_sessionstart (playwright_state.py).
# We must NOT call sync_playwright() here because on Windows / Python 3.14
# the first call leaves the ProactorEventLoop marked as "running"; any
# subsequent call raises "Playwright Sync API inside the asyncio loop."
# ---------------------------------------------------------------------------

def _browser():
    """Return the shared Chromium browser (raises if unavailable)."""
    return _pw_state.get_browser()


# ---------------------------------------------------------------------------
# Navigation-helper overrides for test_composed_fixtures.py
# Root conftest defines cart_page / checkout_page TWICE: the last definition
# returns POM objects (CartPage / CheckoutPage), which breaks tests that
# treat these as raw Playwright Page objects.  These local overrides restore
# the navigation-helper behaviour for functional tests.
# ---------------------------------------------------------------------------

@pytest.fixture
def cart_page(logged_in_page):
    """Navigate to cart with one item already added."""
    logged_in_page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    logged_in_page.locator(".shopping_cart_link").click()
    return logged_in_page


@pytest.fixture
def checkout_page(cart_page):
    """Navigate to checkout step 1 (cart  Checkout button)."""
    cart_page.get_by_role("button", name="Checkout").click()
    return cart_page


# ---------------------------------------------------------------------------
# Composed fixtures (fixture chaining)
# ---------------------------------------------------------------------------

@pytest.fixture
def page():
    """
    Function-scoped page fixture using the session-level browser.

    Shadows the broken fixture in tests/conftest.py, which calls
    sync_playwright() inside the fixture body — that fails on Python 3.14
    because asyncio is already running by the time fixtures execute.
    Here we reuse the browser created in pytest_sessionstart (before asyncio).
    """
    context = _browser().new_context()
    pg = context.new_page()
    pg.set_default_timeout(30000)
    pg.set_default_navigation_timeout(30000)
    yield pg
    context.close()


@pytest.fixture
def inventory_page(logged_in_page):
    """Page already logged in and on the inventory page."""
    logged_in_page.wait_for_url("**/inventory.html")
    return logged_in_page


# ---------------------------------------------------------------------------
# Parametrized fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["chromium", "firefox", "webkit"])
def multi_browser(request):
    """
    Browser parametrised over chromium / firefox / webkit.
    All three variants use the pre-initialised Chromium session browser.
    """
    yield _browser()


VIEWPORTS = {
    "mobile":  {"width": 375,  "height": 667},
    "tablet":  {"width": 768,  "height": 1024},
    "desktop": {"width": 1280, "height": 720},
}


@pytest.fixture(params=["mobile", "tablet", "desktop"])
def responsive_page(request):
    """Page with a specific viewport; page.viewport_name is set."""
    context = _browser().new_context(viewport=VIEWPORTS[request.param])
    page = context.new_page()
    page.viewport_name = request.param
    yield page
    context.close()


USERS = {
    "standard":    ("standard_user",          "secret_sauce"),
    "problem":     ("problem_user",            "secret_sauce"),
    "performance": ("performance_glitch_user", "secret_sauce"),
}


@pytest.fixture(params=list(USERS.keys()))
def user_page(request, test_data):
    """Logged-in page for each user type; page.username is set."""
    username, password = USERS[request.param]
    context = _browser().new_context()
    page = context.new_page()
    page.username = username

    page.goto(test_data["urls"]["base"])
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")

    yield page
    context.close()


@pytest.fixture(
    params=[
        pytest.param("backpack",   id="backpack"),
        pytest.param("bike_light", id="bike_light"),
        pytest.param("onesie",     id="onesie"),
    ]
)
def product_info(request, test_data):
    """Product data for each product in test_data."""
    return test_data["products"][request.param]


# ---------------------------------------------------------------------------
# Factory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def create_page():
    """Factory: create a page with a custom viewport."""
    contexts = []

    def _create(viewport_width=1280, viewport_height=720):
        context = _browser().new_context(
            viewport={"width": viewport_width, "height": viewport_height}
        )
        contexts.append(context)
        return context.new_page()

    yield _create

    for ctx in contexts:
        try:
            ctx.close()
        except Exception:
            pass


@pytest.fixture
def create_authenticated_page(test_data):
    """Factory: create a logged-in page for a given user type."""
    contexts = []

    def _create(user_type="standard"):
        user = test_data["users"][user_type]
        context = _browser().new_context()
        contexts.append(context)
        page = context.new_page()

        page.goto(test_data["urls"]["base"])
        page.get_by_placeholder("Username").fill(user["username"])
        page.get_by_placeholder("Password").fill(user["password"])
        page.get_by_role("button", name="Login").click()
        timeout = 60000 if user_type == "performance" else 30000
        page.wait_for_url("**/inventory.html", timeout=timeout)
        return page

    yield _create

    for ctx in contexts:
        try:
            ctx.close()
        except Exception:
            pass


@pytest.fixture
def create_cart_with_items(test_data):
    """Factory: create a logged-in page with specified items already in the cart."""
    contexts = []

    def _create(item_ids):
        user = test_data["users"]["standard"]
        context = _browser().new_context()
        contexts.append(context)
        page = context.new_page()

        page.goto(test_data["urls"]["base"])
        page.get_by_placeholder("Username").fill(user["username"])
        page.get_by_placeholder("Password").fill(user["password"])
        page.get_by_role("button", name="Login").click()
        page.wait_for_url("**/inventory.html")

        for item_id in item_ids:
            page.locator(f"[data-test='add-to-cart-{item_id}']").click()

        return page

    yield _create

    for ctx in contexts:
        try:
            ctx.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# request-object fixtures (test_request_usage.py)
# ---------------------------------------------------------------------------

@pytest.fixture
def context_aware_fixture(request):
    """Fixture that introspects the requesting test."""
    print(f"\n[FIXTURE] Running for: {request.node.name}")
    print(f"[FIXTURE] Module: {request.module.__name__}")
    print(f"[FIXTURE] Markers: {list(request.node.iter_markers())}")
    return {"test_name": request.node.name}


@pytest.fixture
def dynamic_timeout(request):
    """Return 60 000 ms for @pytest.mark.slow tests, else 10 000 ms."""
    if request.node.get_closest_marker("slow"):
        return 60000
    return 10000


@pytest.fixture
def test_artifacts_dir(request, tmp_path):
    """Per-test artifacts directory under tmp_path."""
    artifacts = tmp_path / request.node.name
    artifacts.mkdir(parents=True, exist_ok=True)
    return artifacts


@pytest.fixture
def fixture_with_indirect_param(request):
    """Receives a value via indirect parametrize and processes it."""
    return f"Processed: {request.param}"
