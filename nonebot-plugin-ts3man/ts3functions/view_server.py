import ts3


class ChannelTreeNode(object):
    def __init__(self, info, parent, root, clients=None):

        self.info = info
        self.childs = list()

        if root is None:
            self.parent = None
            self.clients = None
            self.root = self

        else:
            self.parent = parent
            self.root = root
            self.clients = clients if clients is not None else list()
        return None

    @classmethod
    def init_root(cls, info):

        return cls(info, None, None, None)

    def is_root(self):

        return self.parent is None

    def is_channel(self):
        return self.parent is not None

    @classmethod
    def build_tree(cls, ts3conn, sid):
        ts3conn.use(sid=sid, virtual=True)

        resp = ts3conn.serverinfo()
        serverinfo = resp.parsed[0]

        resp = ts3conn.channellist()
        channellist = resp.parsed

        resp = ts3conn.clientlist()
        clientlist = resp.parsed

        clientlist = {
            cid: [client for client in clientlist if client["cid"] == cid]
            for cid in map(lambda e: e["cid"], channellist)
        }

        root = cls.init_root(serverinfo)
        for channel in channellist:
            resp = ts3conn.channelinfo(cid=channel["cid"])
            channelinfo = resp.parsed[0]

            channelinfo.update(channel)

            channel = cls(
                info=channelinfo,
                parent=root,
                root=root,
                clients=clientlist[channel["cid"]],
            )
            root.insert(channel)
        return root

    def insert(self, channel):
        self.root._insert(channel)
        return None

    def _insert(self, channel):
        if self.is_root():
            i = 0
            while i < len(self.childs):
                child = self.childs[i]
                if channel.info["cid"] == child.info["pid"]:
                    channel.childs.append(child)
                    self.childs.pop(i)
                else:
                    i += 1

        elif channel.info["pid"] == self.info["cid"]:
            self.childs.append(channel)
            return True

        for child in self.childs:
            if child._insert(channel):
                return True
        if self.is_root():
            self.childs.append(channel)
        return False

    def tostr(self, indent=0):
        tree = ""
        if self.is_root():
            tree += (
                " " * (indent * 3)
                + "|- "
                + self.info["virtualserver_name"]
                + " [SERVER]\n"
            )
        else:
            tree += (
                " " * (indent * 3) + "|- " + self.info["channel_name"] + " [CHANNEL]\n"
            )
            for client in self.clients:
                if client["client_type"] == "1":
                    continue
                tree += (
                    " " * (indent * 3 + 3)
                    + "-> "
                    + client["client_nickname"]
                    + " [USER]\n"
                )
        for child in self.childs:
            tree += child.tostr(indent=indent + 1)
        return tree


def get(ts3conn, sid=1):
    tree = ChannelTreeNode.build_tree(ts3conn, sid)
    return tree.tostr()
