import os
import json
from playwright.sync_api import BrowserContext

class AuthManager:
    def __init__(self, base_path="auth_states"):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def get_state_path(self, platform_name):
        return os.path.join(self.base_path, f"{platform_name}.json")

    def save_state(self, context: BrowserContext, platform_name):
        """Save storage state (cookies, local storage) to file."""
        path = self.get_state_path(platform_name)
        context.storage_state(path=path)
        print(f"[{platform_name}] Session saved to {path}")

    def load_state(self, platform_name):
        """Return path to storage state if it exists, else None."""
        path = self.get_state_path(platform_name)
        if os.path.exists(path):
            return path
        return None

