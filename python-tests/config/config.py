from config.config_provider import ConfigProvider


class Server:
    def __init__(self, env: str):
        self.config = ConfigProvider(env)
        self.base_api_url = self.config.get("base_api_url")
        self.base_auth_url = self.config.get("base_auth_url")
