import ts3
import time
from nonebot import logger


class User:
    """
    Opreation of User
    """

    def __init__(self, ts3conn, uid):
        self.ts3conn = ts3conn
        self.uid = uid

    def kick_channel(self, reason):
        return self.ts3conn.clientkick(clid=self.uid, reasonid=4, reasonmsg=reason)

    def kick_server(self, reason):
        return self.ts3conn.clientkick(clid=self.uid, reasonid=5, reasonmsg=reason)

    def ban(self, time, reason):
        return self.ts3conn.banclient(clid=self.uid, time=time, banreason=reason)

    def unban(self):
        return self.ts3conn.bandel(self.uid)

    def move(self, cid):
        return self.ts3conn.client_move(self.uid, cid)


class Server:
    """
    Opreations on the server
    """

    def __init__(self, ts3conn):
        self.ts3conn = ts3conn
        self.error = ""

    def get_online_users(self) -> list:
        # 获取在线用户信息
        try:
            self.ts3conn.use(sid=1)
            response = self.ts3conn.clientlist(
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
    server = Server(ts3conn)
    return server.get_online_users(), server.error


def timeformat(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
