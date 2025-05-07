from pydantic import BaseModel
from pathlib import Path

import yaml
from nonebot import logger


class Config(BaseModel):
    host: str
    port: int
    username: str
    password: str

    @classmethod
    def load_from_yaml(cls) -> "Config":
        config_path = Path.cwd() / Path("ts3man.yaml")
        if not config_path.exists():
            logger.warning("未找到配置文件，已创建默认配置文件。")
            default_config = {
                "TS3_SERVER": [
                    {
                        "host": "localhost",
                        "port": 10011,
                        "username": "serveradmin",
                        "password": "password",
                    }
                ]
            }
            config_path.write_text(yaml.dump(default_config))
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 提取第一个服务器配置
        server_config = data.get("TS3_SERVER", [])[0]
        return cls(**server_config)

    @classmethod
    def reload(cls) -> "Config":
        return Config.load_from_yaml()
