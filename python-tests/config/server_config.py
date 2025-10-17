from config.config_provider import ConfigProvider


class Server:
    def __init__(self, env: str):
        self.config = ConfigProvider(env)
        self.gateway_url = self.config.get("gateway_url")
        self.auth_url = self.config.get("frontend_url")
