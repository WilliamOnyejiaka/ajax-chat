from streamlit_cookies_manager import EncryptedCookieManager

class CookieManger:

    manager = None

    def __init__(self, prefix: str, password: str):
        self.manager = EncryptedCookieManager(prefix=prefix, password=password)

    def ready(self):
        return self.manager.ready()

    def set(self, key: str, value: any):
        self.manager[key] = value
        self.manager.save()

    def get(self, key: str):
        return self.manager.get(key, "")

    def delete(self, key: str):
        self.manager[key] = ""
        self.manager.save()