import configparser


class ConfigProvider:
    def __init__(self, env: str, config_path: str = "../config.ini"):
        self.env = env
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def get(self, key: str, section: str = None):
        section = section or self.env
        return self.config.get(section, key)
