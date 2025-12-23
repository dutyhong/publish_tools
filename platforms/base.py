from abc import ABC, abstractmethod
from playwright.sync_api import Page, BrowserContext

class BasePublisher(ABC):
    def __init__(self, context: BrowserContext):
        self.context = context
        self.page = None

    @abstractmethod
    def login(self):
        """
        Handle login process. 
        Should check if logged in, if not, wait for user input (QR scan).
        """
        pass

    @abstractmethod
    def publish(self, article: dict):
        """
        Publish the article.
        article dict should contain:
        - title
        - content (html or text)
        - images (list of paths)
        """
        pass

