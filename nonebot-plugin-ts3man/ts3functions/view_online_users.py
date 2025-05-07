import ts3
import time
from nonebot import logger


# 获取teamspeak服务器在线用户
# 返回username(nickname),uid,client_id,online_time
class online_users(object):
    def __init__(self):
        # 初始化连接参数
        self.error = ""

    def get_online_users(self, ts3conn) -> list:
        # 获取在线用户信息
        try:
            ts3conn.use(sid=1)
            response = ts3conn.clientlist(
                country=True, uid=True, times=True, voice=True, away=True
            )

            users = []
            for client in response:
                if client.get("client_type") == "0":  # 排除服务器查询用户
                    online_time = int(time.time()) - int(
                        client.get("client_lastconnected", 0)
                    )
                    users.append(
                        {
                            "username": client.get("client_nickname"),
                            "uid": client.get("client_unique_identifier"),
                            "client_id": client.get("clid"),
                            "online_time": online_time,
                        }
                    )
            return users
        except ts3.query.TS3QueryError as e:
            self.error = f"Error: {e.resp.error['msg']}"
        except Exception as e:
            self.error = f"Unexpected error: {e}"
        return []


def get_online_users(ts3conn):
    return online_users().get_online_users(ts3conn), online_users().error


def timeformat(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
