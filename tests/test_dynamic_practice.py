from playwright.sync_api import expect

def test_dynamic_controls_complete(page):
    """Practice: Complete dynamic controls test"""
    
    page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    
    # === CHECKBOX SECTION ===
    
    # 1. Verify checkbox exists
    checkbox = page.locator("#checkbox-example input[type='checkbox']")
    expect(checkbox).to_be_visible()
    
    # 2. Remove checkbox
    page.get_by_role("button", name="Remove").click()
    
    # Wait for checkbox to disappear (loading appears then hides)
    page.wait_for_selector("#loading", state="visible", timeout=10000)
    page.wait_for_selector("#loading", state="hidden", timeout=10000)

    # 3. Verify "It's gone!" message
    message = page.locator("#message")
    expect(message).to_have_text("It's gone!")

    # 4. Add checkbox back
    page.get_by_role("button", name="Add").click()

    # Wait for loading to appear then disappear
    page.wait_for_selector("#loading", state="visible", timeout=10000)
    page.wait_for_selector("#loading", state="hidden", timeout=10000)
    checkbox = page.locator("#checkbox-example input[type='checkbox']")
    expect(checkbox).to_be_visible(timeout=10000)

    # 5. Verify "It's back!" message
    expect(message).to_have_text("It's back!")
    
    # === INPUT SECTION ===
    
    # 6. Verify input is disabled
    text_input = page.locator("#input-example input")
    expect(text_input).to_be_disabled()
    
    # 7. Enable input
    page.get_by_role("button", name="Enable").click()
    
    # Wait for input to be enabled
    expect(text_input).to_be_enabled(timeout=10000)
    
    # 8. Type text
    text_input.fill("Hello Playwright!")
    expect(text_input).to_have_value("Hello Playwright!")
    
    # 9. Verify "It's enabled!" message
    expect(message).to_have_text("It's enabled!")
