"""
pages/components/sidebar_menu.py
Sidebar Menu Component
"""

from playwright.sync_api import Page, Locator, expect


class SidebarMenu:
    """
    Sidebar/hamburger menu component
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    # ============================================================
    # LOCATORS
    # ============================================================
    
    @property
    def menu_container(self) -> Locator:
        """Menu container"""
        return self.page.locator(".bm-menu")
    
    @property
    def close_button(self) -> Locator:
        """Close menu button"""
        return self.page.get_by_role("button", name="Close Menu")
    
    @property
    def all_items_link(self) -> Locator:
        """All Items link"""
        return self.page.locator("#inventory_sidebar_link")
    
    @property
    def about_link(self) -> Locator:
        """About link"""
        return self.page.locator("#about_sidebar_link")
    
    @property
    def logout_link(self) -> Locator:
        """Logout link"""
        return self.page.locator("#logout_sidebar_link")
    
    @property
    def reset_app_state_link(self) -> Locator:
        """Reset App State link"""
        return self.page.locator("#reset_sidebar_link")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def close(self) -> "SidebarMenu":
        """Close the menu"""
        self.close_button.click()
        expect(self.menu_container).to_be_hidden()
        return self
    
    def go_to_all_items(self) -> "SidebarMenu":
        """Navigate to all items"""
        self.all_items_link.click()
        return self
    
    def go_to_about(self) -> "SidebarMenu":
        """Navigate to about page"""
        self.about_link.click()
        return self
    
    def logout(self) -> "SidebarMenu":
        """Logout"""
        self.logout_link.click()
        return self
    
    def reset_app_state(self) -> "SidebarMenu":
        """Reset app state"""
        self.reset_app_state_link.click()
        return self
    
    # ============================================================
    # ASSERTIONS
    # ============================================================
    
    def is_open(self) -> bool:
        """Check if menu is open"""
        return self.menu_container.is_visible()
    
    def verify_open(self) -> "SidebarMenu":
        """Verify menu is open"""
        expect(self.menu_container).to_be_visible()
        return self
    
    def verify_closed(self) -> "SidebarMenu":
        """Verify menu is closed"""
        expect(self.menu_container).to_be_hidden()
        return self
