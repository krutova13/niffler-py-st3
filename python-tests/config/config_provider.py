import configparser
import os


class ConfigProvider:
    def __init__(self, env: str):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, '..', 'config.ini')
        config_path = os.path.abspath(config_path)
        self.env = env
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def get(self, key: str, section: str = None):
        section = section or self.env
        return self.config.get(section, key)
