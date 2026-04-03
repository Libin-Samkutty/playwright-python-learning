"""
CONCEPT: Forms and User Interactions
GOAL: Master all types of user input and actions
REAL-WORLD USE: Testing any interactive web application
"""

from playwright.sync_api import expect
import pytest

# Tests will be added as we learn each interaction type

def test_text_input_fill(page):
    """
    METHOD: fill()
    ACTION: Clears field and types text
    REAL-WORLD USE: Login forms, search boxes, any text input
    
    HOW IT WORKS:
    1. Focuses the element
    2. Clears existing content
    3. Types the text instantly (not character by character)
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Find username input
    username = page.get_by_placeholder("Username")
    
    # Fill clears existing content and sets new value
    username.fill("standard_user")
    
    # Verify value was set
    expect(username).to_have_value("standard_user")
    
    # Fill again - replaces previous value
    username.fill("different_user")
    expect(username).to_have_value("different_user")


def test_text_input_type(page):
    """
    METHOD: type()
    ACTION: Types text character by character
    REAL-WORLD USE: When you need to simulate real typing (triggers JS events)
    
    DIFFERENCE FROM fill():
    - fill(): Instant, doesn't trigger keypress events per character
    - type(): Simulates real typing, triggers each keypress
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    username = page.get_by_label("Username")
    
    # Type simulates real keyboard input
    # delay=100 means 100ms between each keystroke
    username.type("tomsmith", delay=100)
    
    expect(username).to_have_value("tomsmith")


def test_text_input_clear(page):
    """
    METHOD: clear()
    ACTION: Clears input field
    REAL-WORLD USE: Reset forms, edit existing values
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username = page.get_by_placeholder("Username")
    
    # Fill some text
    username.fill("some_text")
    expect(username).to_have_value("some_text")
    
    # Clear the field
    username.clear()
    expect(username).to_have_value("")
    expect(username).to_be_empty()


def test_text_input_press_sequentially(page):
    """
    METHOD: press_sequentially()
    ACTION: Types text with configurable delay
    REAL-WORLD USE: Autocomplete testing, search suggestions
    
    This is the newer, preferred method over type()
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    username = page.get_by_label("Username")
    
    # Press each key with 50ms delay
    username.press_sequentially("tomsmith", delay=50)
    
    expect(username).to_have_value("tomsmith")

def test_textarea_multiline(page):
    """
    ELEMENT: <textarea>
    ACTION: Enter multiline text
    REAL-WORLD USE: Comments, descriptions, messages
    """
    
    page.goto("https://the-internet.herokuapp.com/tinymce")
    
    # This page has an iframe with TinyMCE editor
    # For now, let's use a simpler example
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Let's demonstrate with a regular input
    # Textareas work the same way
    username = page.get_by_label("Username")
    username.fill("line1")
    
    # For actual textarea with newlines:
    # textarea.fill("Line 1\nLine 2\nLine 3")

def test_select_by_value(page):
    """
    ELEMENT: <select> dropdown
    METHOD: select_option(value="...")
    ACTION: Select option by value attribute
    REAL-WORLD USE: Country selectors, category filters
    """
    
    page.goto("https://the-internet.herokuapp.com/dropdown")
    
    dropdown = page.locator("#dropdown")
    
    # Select by value attribute
    dropdown.select_option(value="1")
    
    # Verify selection
    expect(dropdown).to_have_value("1")


def test_select_by_label(page):
    """
    METHOD: select_option(label="...")
    ACTION: Select option by visible text
    REAL-WORLD USE: Most common - matches what users see
    """
    
    page.goto("https://the-internet.herokuapp.com/dropdown")
    
    dropdown = page.locator("#dropdown")
    
    # Select by visible text
    dropdown.select_option(label="Option 2")
    
    # Verify selection
    expect(dropdown).to_have_value("2")


def test_select_by_index(page):
    """
    METHOD: select_option(index=N)
    ACTION: Select option by position (0-based)
    REAL-WORLD USE: When value/label are dynamic
    
     STABILITY: Low - breaks if order changes
    """
    
    page.goto("https://the-internet.herokuapp.com/dropdown")
    
    dropdown = page.locator("#dropdown")
    
    # Select second option (index 1, since 0 is "Please select")
    dropdown.select_option(index=1)
    
    expect(dropdown).to_have_value("1")


def test_select_multiple(page):
    """
    METHOD: select_option([...])
    ACTION: Select multiple options
    REAL-WORLD USE: Multi-select dropdowns
    """
    
    # Note: the-internet doesn't have multi-select
    # This is the syntax for when you encounter one:
    
    # dropdown.select_option(value=["option1", "option2", "option3"])
    # OR
    # dropdown.select_option(label=["Red", "Green", "Blue"])
    
    pass  # Placeholder - syntax demonstration only


def test_get_selected_option(page):
    """
    CONCEPT: Reading current selection
    REAL-WORLD USE: Verify default selection, form state
    """
    
    page.goto("https://the-internet.herokuapp.com/dropdown")
    
    dropdown = page.locator("#dropdown")
    
    # Select an option
    dropdown.select_option(label="Option 1")
    
    # Get selected value
    selected_value = dropdown.input_value()
    assert selected_value == "1"
    
    # Alternative: check the selected option's text
    selected_option = dropdown.locator("option:checked")
    expect(selected_option).to_have_text("Option 1")

def test_custom_dropdown(page):
    """
    ELEMENT: Custom dropdown (div-based)
    ACTION: Click to open, then click option
    REAL-WORLD USE: Most modern UI frameworks
    
    HOW TO IDENTIFY:
    - No <select> element in HTML
    - Usually divs with click handlers
    - Often has aria-* attributes
    """
    
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # SauceDemo has a custom sort dropdown
    # It's a <select> but let's demonstrate the pattern
    
    sort_dropdown = page.locator("[data-test='product-sort-container']")
    
    # For native select, use select_option
    sort_dropdown.select_option(label="Price (low to high)")
    
    # Verify sorting changed
    first_price = page.locator(".inventory_item_price").first
    expect(first_price).to_have_text("$7.99")  # Cheapest item


def test_custom_dropdown_click_pattern(page):
    """
    PATTERN: Custom dropdown that requires clicking
    
    Steps:
    1. Click dropdown trigger
    2. Wait for options to appear
    3. Click desired option
    """
    
    # This is a common pattern for custom dropdowns:
    
    # # Step 1: Click the dropdown trigger
    # page.locator(".dropdown-trigger").click()
    
    # # Step 2: Wait for options
    # options = page.locator(".dropdown-options")
    # expect(options).to_be_visible()
    
    # # Step 3: Click desired option
    # page.locator(".dropdown-option", has_text="My Choice").click()
    
    # # Step 4: Verify dropdown closed
    # expect(options).to_be_hidden()
    
    pass  # Pattern demonstration

def test_checkbox_check(page):
    """
    ELEMENT: <input type="checkbox">
    METHOD: check()
    ACTION: Checks the checkbox (idempotent)
    REAL-WORLD USE: Terms acceptance, feature toggles
    
    IDEMPOTENT: Calling check() on already-checked box does nothing
    """
    
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    # Get both checkboxes
    checkboxes = page.locator("input[type='checkbox']")
    checkbox1 = checkboxes.nth(0)
    checkbox2 = checkboxes.nth(1)
    
    # Check the first checkbox (currently unchecked)
    checkbox1.check()
    expect(checkbox1).to_be_checked()
    
    # Check again - no change (idempotent)
    checkbox1.check()
    expect(checkbox1).to_be_checked()


def test_checkbox_uncheck(page):
    """
    METHOD: uncheck()
    ACTION: Unchecks the checkbox (idempotent)
    """
    
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    checkboxes = page.locator("input[type='checkbox']")
    checkbox2 = checkboxes.nth(1)  # This one starts checked
    
    # Verify it starts checked
    expect(checkbox2).to_be_checked()
    
    # Uncheck it
    checkbox2.uncheck()
    expect(checkbox2).not_to_be_checked()


def test_checkbox_toggle(page):
    """
    METHOD: click()
    ACTION: Toggles checkbox state
    REAL-WORLD USE: When you need to toggle regardless of current state
    """
    
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    checkbox = page.locator("input[type='checkbox']").first
    
    # Get initial state
    initial_state = checkbox.is_checked()
    
    # Click toggles the state
    checkbox.click()
    
    # Verify state changed
    if initial_state:
        expect(checkbox).not_to_be_checked()
    else:
        expect(checkbox).to_be_checked()


def test_checkbox_set_checked(page):
    """
    METHOD: set_checked(True/False)
    ACTION: Sets checkbox to specific state
    REAL-WORLD USE: Setting form to known state before test
    """
    
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    checkbox = page.locator("input[type='checkbox']").first
    
    # Set to checked (regardless of current state)
    checkbox.set_checked(True)
    expect(checkbox).to_be_checked()
    
    # Set to unchecked
    checkbox.set_checked(False)
    expect(checkbox).not_to_be_checked()

def test_radio_buttons(page):
    """
    ELEMENT: <input type="radio">
    METHOD: check()
    ACTION: Selects the radio button
    REAL-WORLD USE: Single choice selections (gender, payment method)
    
    NOTE: Radio buttons in same group auto-deselect others
    """
    
    # The Internet doesn't have radio buttons
    # Let's use a different pattern demonstration
    
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    # Radio button syntax (similar to checkbox):
    # page.locator("input[type='radio'][value='option1']").check()
    # expect(page.locator("input[type='radio'][value='option1']")).to_be_checked()
    
    # Other options auto-deselect:
    # page.locator("input[type='radio'][value='option2']").check()
    # expect(page.locator("input[type='radio'][value='option1']")).not_to_be_checked()
    # expect(page.locator("input[type='radio'][value='option2']")).to_be_checked()
    
    pass  # Pattern demonstration


def test_radio_button_by_label(page):
    """
    PATTERN: Select radio by label text
    REAL-WORLD USE: More readable tests
    """
    
    # Common pattern:
    # page.get_by_label("Male").check()
    # page.get_by_label("Female").check()
    # page.get_by_label("Credit Card").check()
    
    pass  # Pattern demonstration

def test_keyboard_enter(page):
    """
    METHOD: press()
    ACTION: Press a keyboard key
    REAL-WORLD USE: Submit forms, trigger shortcuts
    """
    
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Fill form
    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("SuperSecretPassword!")
    
    # Press Enter to submit (instead of clicking button)
    page.get_by_label("Password").press("Enter")
    
    # Verify login worked
    expect(page).to_have_url("https://the-internet.herokuapp.com/secure")


def test_keyboard_tab_navigation(page):
    """
    METHOD: press("Tab")
    ACTION: Move focus to next element
    REAL-WORLD USE: Accessibility testing, form navigation
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username = page.get_by_placeholder("Username")
    password = page.get_by_placeholder("Password")
    
    # Click username field
    username.click()
    expect(username).to_be_focused()
    
    # Tab to password field
    page.keyboard.press("Tab")
    expect(password).to_be_focused()
    
    # Tab to login button
    page.keyboard.press("Tab")
    login_button = page.get_by_role("button", name="Login")
    expect(login_button).to_be_focused()


def test_keyboard_escape(page):
    """
    METHOD: press("Escape")
    ACTION: Close modals, cancel operations
    REAL-WORLD USE: Modal dialogs, dropdowns
    """
    
    # Pattern for closing modals:
    # page.locator(".modal-trigger").click()
    # expect(page.locator(".modal")).to_be_visible()
    # page.keyboard.press("Escape")
    # expect(page.locator(".modal")).to_be_hidden()
    
    pass  # Pattern demonstration


def test_keyboard_shortcuts(page):
    """
    METHOD: press() with modifiers
    ACTION: Keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)
    REAL-WORLD USE: Copy/paste, undo/redo, save
    
    MODIFIER SYNTAX:
    - Control+Key (Windows/Linux)
    - Meta+Key (Mac Command key)
    """
    
    page.goto("https://www.saucedemo.com/")
    
    username = page.get_by_placeholder("Username")
    password = page.get_by_placeholder("Password")
    
    # Type in username
    username.fill("standard_user")
    
    # Select all (Ctrl+A)
    username.press("Control+a")
    
    # Copy (Ctrl+C)
    username.press("Control+c")
    
    # Click password and paste (Ctrl+V)
    password.click()
    password.press("Control+v")
    
    # Both fields should have same value now
    expect(password).to_have_value("standard_user")


def test_keyboard_arrow_keys(page):
    """
    METHOD: press() with arrow keys
    ACTION: Navigate within elements
    REAL-WORLD USE: Dropdown navigation, sliders, date pickers
    """
    
    page.goto("https://the-internet.herokuapp.com/dropdown")
    
    dropdown = page.locator("#dropdown")
    
    # Focus dropdown
    dropdown.focus()
    
    # Use arrow keys to select
    dropdown.press("ArrowDown")  # Move to first option
    dropdown.press("ArrowDown")  # Move to second option
    dropdown.press("Enter")      # Select
    
    expect(dropdown).to_have_value("2")

def test_mouse_click_types(page):
    """
    METHODS: click(), dblclick(), click(button="right")
    ACTION: Various click types
    REAL-WORLD USE: Context menus, double-click to edit
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    # Regular click
    link = page.get_by_role("link", name="Context Menu")
    link.click()
    
    expect(page).to_have_url("https://the-internet.herokuapp.com/context_menu")


def test_mouse_right_click(page):
    """
    METHOD: click(button="right")
    ACTION: Right-click (context menu)
    REAL-WORLD USE: Context menus, custom right-click actions
    """
    
    page.goto("https://the-internet.herokuapp.com/context_menu")
    
    # Right-click on the box
    hot_spot = page.locator("#hot-spot")
    hot_spot.click(button="right")
    
    # This triggers a JavaScript alert
    # We'll handle this in the dialogs section


def test_mouse_double_click(page):
    """
    METHOD: dblclick()
    ACTION: Double-click
    REAL-WORLD USE: Edit modes, open files, select words
    """
    
    page.goto("https://the-internet.herokuapp.com/")
    
    # Navigate to add/remove elements page
    page.get_by_role("link", name="Add/Remove Elements").click()
    
    # Double-click example (just demonstrating syntax)
    button = page.get_by_role("button", name="Add Element")
    
    # Single click adds one element
    button.click()
    expect(page.locator(".added-manually")).to_have_count(1)
    
    # Double click would add two more
    button.dblclick()
    expect(page.locator(".added-manually")).to_have_count(3)


def test_mouse_click_modifiers(page):
    """
    METHOD: click(modifiers=[...])
    ACTION: Click with modifier keys
    REAL-WORLD USE: Open in new tab, multi-select
    """
    
    # Ctrl+Click to open in new tab
    # page.get_by_role("link").click(modifiers=["Control"])
    
    # Shift+Click for range selection
    # page.locator(".item").first.click()
    # page.locator(".item").nth(5).click(modifiers=["Shift"])
    
    pass  # Pattern demonstration


def test_mouse_click_position(page):
    """
    METHOD: click(position={"x": N, "y": N})
    ACTION: Click at specific position within element
    REAL-WORLD USE: Image maps, canvas, sliders
    """
    
    page.goto("https://www.saucedemo.com/")
    
    login_button = page.get_by_role("button", name="Login")
    
    # Click at specific position within the button
    # x=10, y=10 means 10 pixels from top-left of element
    login_button.click(position={"x": 10, "y": 10})
    
    # Error should appear (no credentials)
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()

def test_mouse_hover(page):
    """
    METHOD: hover()
    ACTION: Move mouse over element
    REAL-WORLD USE: Dropdown menus, tooltips, reveal actions
    """
    
    page.goto("https://the-internet.herokuapp.com/hovers")
    
    # Get all user figures
    figures = page.locator(".figure")
    first_figure = figures.first
    
    # Info is hidden initially
    info = first_figure.locator(".figcaption")
    expect(info).to_be_hidden()
    
    # Hover to reveal info
    first_figure.hover()
    
    # Info should now be visible
    expect(info).to_be_visible()
    expect(info).to_contain_text("user1")


def test_hover_dropdown_menu(page):
    """
    PATTERN: Hover to reveal dropdown menu
    REAL-WORLD USE: Navigation menus
    """
    
    # Common pattern:
    # page.locator(".menu-item").hover()
    # expect(page.locator(".submenu")).to_be_visible()
    # page.locator(".submenu-item").click()
    
    pass  # Pattern demonstration

def test_drag_and_drop(page):
    """
    METHOD: drag_to()
    ACTION: Drag element to another element
    REAL-WORLD USE: Kanban boards, file managers, sortable lists
    """
    
    page.goto("https://the-internet.herokuapp.com/drag_and_drop")
    
    # Get source and target
    column_a = page.locator("#column-a")
    column_b = page.locator("#column-b")
    
    # Verify initial state
    expect(column_a.locator("header")).to_have_text("A")
    expect(column_b.locator("header")).to_have_text("B")
    
    # Drag A to B
    column_a.drag_to(column_b)
    
    # Verify swap (positions should be swapped)
    # Note: This specific site swaps the headers, not positions
    expect(column_a.locator("header")).to_have_text("B")
    expect(column_b.locator("header")).to_have_text("A")


def test_drag_and_drop_manual(page):
    """
    PATTERN: Manual drag and drop (for complex scenarios)
    REAL-WORLD USE: When drag_to() doesn't work
    """
    
    page.goto("https://the-internet.herokuapp.com/drag_and_drop")
    
    source = page.locator("#column-a")
    target = page.locator("#column-b")
    
    # Get bounding boxes
    source_box = source.bounding_box()
    target_box = target.bounding_box()
    
    # Manual drag using mouse
    page.mouse.move(
        source_box["x"] + source_box["width"] / 2,
        source_box["y"] + source_box["height"] / 2
    )
    page.mouse.down()
    page.mouse.move(
        target_box["x"] + target_box["width"] / 2,
        target_box["y"] + target_box["height"] / 2
    )
    page.mouse.up()

def test_file_upload_single(page):
    """
    METHOD: set_input_files()
    ACTION: Upload file(s)
    REAL-WORLD USE: Profile pictures, documents, attachments
    """
    
    page.goto("https://the-internet.herokuapp.com/upload")
    
    # Get the file input
    file_input = page.locator("#file-upload")
    
    # Create a test file first
    import os
    test_file = "test_upload.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for upload")
    
    try:
        # Upload the file
        file_input.set_input_files(test_file)
        
        # Click upload button
        page.get_by_role("button", name="Upload").click()
        
        # Verify upload success
        expect(page.locator("#uploaded-files")).to_have_text("test_upload.txt")
    
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)


def test_file_upload_multiple(page):
    """
    METHOD: set_input_files([...])
    ACTION: Upload multiple files
    REAL-WORLD USE: Photo galleries, bulk upload
    """
    
    # Create test files
    import os
    test_files = ["file1.txt", "file2.txt"]

    for f in test_files:
        with open(f, "w") as file:
            file.write(f"Content of {f}")

    try:
        page.goto("https://the-internet.herokuapp.com/upload")

        file_input = page.locator("#file-upload")

        # This page only supports single file upload; upload one file
        file_input.set_input_files(test_files[0])

        page.get_by_role("button", name="Upload").click()

        from playwright.sync_api import expect
        expect(page.locator("#uploaded-files")).to_have_text("file1.txt")

    finally:
        # Cleanup
        for f in test_files:
            if os.path.exists(f):
                os.remove(f)


def test_file_upload_clear(page):
    """
    METHOD: set_input_files([])
    ACTION: Clear file selection
    REAL-WORLD USE: Cancel upload, change file selection
    """
    
    import os
    test_file = "test_clear.txt"
    
    with open(test_file, "w") as f:
        f.write("Test content")
    
    try:
        page.goto("https://the-internet.herokuapp.com/upload")
        
        file_input = page.locator("#file-upload")
        
        # Set a file
        file_input.set_input_files(test_file)
        
        # Clear the selection
        file_input.set_input_files([])
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_file_upload_hidden_input(page):
    """
    PATTERN: Upload when input is hidden (styled uploads)
    REAL-WORLD USE: Custom-styled upload buttons
    """
    
    # Many sites hide the actual input and use a styled button
    # The pattern is the same - find the input and set files
    
    # page.locator("input[type='file']").set_input_files("myfile.txt")
    
    pass  # Pattern demonstration

def test_file_download(page_with_downloads):
    """
    METHOD: expect_download()
    ACTION: Download a file and verify
    REAL-WORLD USE: Reports, exports, attachments
    """
    
    page = page_with_downloads
    
    page.goto("https://the-internet.herokuapp.com/download")
    
    # Start waiting for download BEFORE clicking
    with page.expect_download() as download_info:
        # Click the download link
        page.get_by_role("link", name="some-file.txt").click()
    
    # Get the download
    download = download_info.value
    
    # Verify download started
    assert download.suggested_filename == "some-file.txt"
    
    # Save to specific location
    download_path = f"{page.download_dir}/{download.suggested_filename}"
    download.save_as(download_path)
    
    # Verify file exists
    import os
    assert os.path.exists(download_path)
    
    # Verify file content
    with open(download_path, "r") as f:
        content = f.read()
        # Add assertions about content if needed


def test_download_wait_for_completion(page_with_downloads):
    """
    CONCEPT: Wait for download to complete
    REAL-WORLD USE: Large files, slow networks
    """
    
    page = page_with_downloads
    
    page.goto("https://the-internet.herokuapp.com/download")
    
    with page.expect_download() as download_info:
        page.get_by_role("link", name="some-file.txt").click()
    
    download = download_info.value
    
    # Wait for download to complete (returns path to temp file)
    path = download.path()
    
    # File is now fully downloaded
    assert path is not None

def test_alert_accept(page):
    """
    DIALOG: alert()
    ACTION: Accept the alert
    REAL-WORLD USE: Notification messages
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Set up dialog handler BEFORE triggering
    page.on("dialog", lambda dialog: dialog.accept())
    
    # Click button that triggers alert
    page.get_by_role("button", name="Click for JS Alert").click()
    
    # Verify result
    result = page.locator("#result")
    expect(result).to_have_text("You successfully clicked an alert")


def test_confirm_accept(page):
    """
    DIALOG: confirm()
    ACTION: Click OK
    REAL-WORLD USE: Delete confirmations
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Accept the confirm
    page.on("dialog", lambda dialog: dialog.accept())
    
    # Trigger confirm
    page.get_by_role("button", name="Click for JS Confirm").click()
    
    # Verify OK was clicked
    result = page.locator("#result")
    expect(result).to_have_text("You clicked: Ok")


def test_confirm_dismiss(page):
    """
    DIALOG: confirm()
    ACTION: Click Cancel
    REAL-WORLD USE: Cancel delete operation
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Dismiss (cancel) the confirm
    page.on("dialog", lambda dialog: dialog.dismiss())
    
    # Trigger confirm
    page.get_by_role("button", name="Click for JS Confirm").click()
    
    # Verify Cancel was clicked
    result = page.locator("#result")
    expect(result).to_have_text("You clicked: Cancel")


def test_prompt_with_input(page):
    """
    DIALOG: prompt()
    ACTION: Enter text and accept
    REAL-WORLD USE: User input dialogs
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Handle prompt with text input
    def handle_prompt(dialog):
        # Enter text and accept
        dialog.accept("Hello from Playwright!")
    
    page.on("dialog", handle_prompt)
    
    # Trigger prompt
    page.get_by_role("button", name="Click for JS Prompt").click()
    
    # Verify input was captured
    result = page.locator("#result")
    expect(result).to_have_text("You entered: Hello from Playwright!")


def test_prompt_dismiss(page):
    """
    DIALOG: prompt()
    ACTION: Click Cancel (dismiss)
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    page.on("dialog", lambda dialog: dialog.dismiss())
    
    page.get_by_role("button", name="Click for JS Prompt").click()
    
    result = page.locator("#result")
    expect(result).to_have_text("You entered: null")


def test_dialog_read_message(page):
    """
    CONCEPT: Read dialog message before handling
    REAL-WORLD USE: Verify correct message shown
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    dialog_message = None
    
    def handle_dialog(dialog):
        nonlocal dialog_message
        # Store the message for assertion
        dialog_message = dialog.message
        dialog.accept()
    
    page.on("dialog", handle_dialog)
    
    page.get_by_role("button", name="Click for JS Alert").click()
    
    # Verify the dialog message
    assert dialog_message == "I am a JS Alert"


def test_dialog_once_handler(page):
    """
    CONCEPT: One-time dialog handler
    REAL-WORLD USE: Handle specific dialog, then remove handler
    """
    
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    
    # Use once() for single-use handler
    page.once("dialog", lambda dialog: dialog.accept())
    
    # First dialog will be handled
    page.get_by_role("button", name="Click for JS Alert").click()
    expect(page.locator("#result")).to_have_text("You successfully clicked an alert")
    
    # Set up another handler for second dialog
    page.once("dialog", lambda dialog: dialog.dismiss())
    
    page.get_by_role("button", name="Click for JS Confirm").click()
    expect(page.locator("#result")).to_have_text("You clicked: Cancel")

def test_complete_checkout_form(page):
    """
    REAL-WORLD EXAMPLE: Complete checkout flow
    Combines: text inputs, dropdowns, form submission
    """
    
    # Login
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    
    # Add item to cart
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    
    # Go to cart
    page.locator(".shopping_cart_link").click()
    
    # Proceed to checkout
    page.get_by_role("button", name="Checkout").click()
    
    # Fill checkout form
    first_name = page.get_by_placeholder("First Name")
    last_name = page.get_by_placeholder("Last Name")
    postal_code = page.get_by_placeholder("Zip/Postal Code")
    
    # Use clear() to ensure fields are empty
    first_name.clear()
    last_name.clear()
    postal_code.clear()
    
    # Fill fields
    first_name.fill("John")
    last_name.fill("Doe")
    postal_code.fill("12345")
    
    # Verify values before submitting
    expect(first_name).to_have_value("John")
    expect(last_name).to_have_value("Doe")
    expect(postal_code).to_have_value("12345")
    
    # Submit form
    page.get_by_role("button", name="Continue").click()
    
    # Verify we're on overview page
    expect(page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")
    
    # Complete purchase
    page.get_by_role("button", name="Finish").click()
    
    # Verify success
    expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")


def test_form_validation_errors(page):
    """
    REAL-WORLD EXAMPLE: Test form validation
    Combines: empty submit, error messages, field highlighting
    """
    
    page.goto("https://www.saucedemo.com/")
    
    # Try to login without credentials
    page.get_by_role("button", name="Login").click()
    
    # Verify error message
    error = page.locator("[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Username is required")
    
    # Fill username only
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_role("button", name="Login").click()
    
    # New error message
    expect(error).to_contain_text("Password is required")
    
    # Fill wrong password
    page.get_by_placeholder("Password").fill("wrong_password")
    page.get_by_role("button", name="Login").click()
    
    # Authentication error
    expect(error).to_contain_text("Username and password do not match")
    
    # Clear error by clicking X
    error_button = page.locator("[data-test='error-button']")
    error_button.click()
    expect(error).to_be_hidden()
