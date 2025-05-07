import ts3
import asyncio

from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent

from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot import logger, on_command

from .ts3functions import view_server, view_online_users
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ts3man",
    description="TeamSpeak服务器管理插件",
    usage="NONE",
    type="application",
    homepage="https://github.com/Cloudwhile/nonebot-plugin-ts3man",
    config=Config,
    supported_adapters=["~onebot.v11"],
)

config = Config.load_from_yaml()
logger.info("[TS3MAN] 配置文件加载成功")
USER, PASS, HOST, PORT = config.username, config.password, config.host, config.port


ts_list = on_command("lsts_all", rule=to_me(), permission=SUPERUSER)


@ts_list.handle()
async def handle_private_message():
    try:
        with ts3.query.TS3Connection(HOST, PORT) as ts3conn:
            ts3conn.login(client_login_name=USER, client_login_password=PASS)
            result = view_server.get(ts3conn, sid=1)
            await asyncio.sleep(1)
            await ts_list.send("TeamSpeak 服务器全览\n\n" + result)
    except ts3.query.TS3QueryError as e:
        await asyncio.sleep(1)
        await ts_list.send(f"发生错误：{e}")


ts_users_list = on_command("lsts_users", rule=to_me(), permission=SUPERUSER)


@ts_users_list.handle()
async def _(event: PrivateMessageEvent, args: Message = CommandArg()):
    if str := args.extract_plain_text():
        str_list = str.split()
        if len(str_list) and str_list[0] == "all":
            try:
                with ts3.query.TS3Connection(HOST, PORT) as ts3conn:
                    ts3conn.login(client_login_name=USER, client_login_password=PASS)
                    ts3conn.use(sid=1)
                    result, error = view_online_users.get_online_users(ts3conn)
                    if error == "":
                        if result:
                            text = "在线用户列表：\n"
                            for user in result:
                                online_time = view_online_users.timeformat(
                                    user["online_time"]
                                )
                                text += (
                                    f"用户名: {user['username']}, UID: {user['uid']}, \n"
                                    f"\t客户端ID: {user['client_id']}, 在线时长: {online_time}\n"
                                )
                            await asyncio.sleep(1)
                            await ts_users_list.send(text)
                        else:
                            await asyncio.sleep(1)
                            await ts_users_list.send("当前没有在线用户。")
                    else:
                        await asyncio.sleep(1)
                        await ts_users_list.send(f"发生错误：{error}")

            except ts3.query.TS3QueryError as e:
                await asyncio.sleep(1)
                await ts_users_list.send(f"发生错误：{e}")
