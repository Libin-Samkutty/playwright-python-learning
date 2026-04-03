from playwright.sync_api import expect

def test_saucedemo_complete_flow(page):
    """Practice: Complete e-commerce flow"""
    
    # 1. Login
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    
    # 2. Sort by price (low to high)
    sort_dropdown = page.locator("[data-test='product-sort-container']")
    sort_dropdown.select_option(label="Price (low to high)")
    
    # Verify cheapest item is first
    first_price = page.locator(".inventory_item_price").first
    expect(first_price).to_have_text("$7.99")
    
    # 3. Add first item to cart
    first_item = page.locator(".inventory_item").first
    first_item.get_by_role("button", name="Add to cart").click()
    
    # Verify cart badge
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    
    # 4. Go to cart
    page.locator(".shopping_cart_link").click()
    expect(page).to_have_url("https://www.saucedemo.com/cart.html")
    
    # Verify item in cart
    cart_item = page.locator(".cart_item")
    expect(cart_item).to_have_count(1)
    expect(cart_item).to_contain_text("Sauce Labs Onesie")
    
    # 5. Checkout
    page.get_by_role("button", name="Checkout").click()
    
    # Fill checkout form
    page.get_by_placeholder("First Name").fill("John")
    page.get_by_placeholder("Last Name").fill("Doe")
    page.get_by_placeholder("Zip/Postal Code").fill("12345")
    
    page.get_by_role("button", name="Continue").click()
    
    # Complete order
    page.get_by_role("button", name="Finish").click()
    
    # 6. Verify success
    expect(page).to_have_url("https://www.saucedemo.com/checkout-complete.html")
    expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")
