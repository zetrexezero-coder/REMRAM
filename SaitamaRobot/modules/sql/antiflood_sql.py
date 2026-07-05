import threading
from SaitamaRobot.modules.sql import BASE, SESSION
from sqlalchemy import Column, String, Integer, UnicodeText, BigInteger

DEF_COUNT = 0
DEF_LIMIT = 0
DEF_OBJ = (None, DEF_COUNT, DEF_LIMIT)

INSERTION_LOCK = threading.RLock()

# In-memory flood tracker
CHAT_FLOOD = {}


class FloodControl(BASE):
    __tablename__ = "flood_control"
    chat_id = Column(String(14), primary_key=True)
    user_id = Column(BigInteger, default=None)
    count = Column(Integer, default=0)
    limit = Column(Integer, default=0)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)
        self.user_id = None
        self.count = 0
        self.limit = 0

    def __repr__(self):
        return "<FloodControl for {}>".format(self.chat_id)


class FloodSettings(BASE):
    __tablename__ = "flood_settings"
    chat_id = Column(String(14), primary_key=True)
    flood_mode = Column(Integer, default=1)
    value = Column(UnicodeText, default="0")

    def __init__(self, chat_id, mode=1, value="0"):
        self.chat_id = str(chat_id)
        self.flood_mode = mode
        self.value = value

    def __repr__(self):
        return "<FloodSettings {}>".format(self.chat_id)


FloodControl.__table__.create(checkfirst=True)
FloodSettings.__table__.create(checkfirst=True)


def update_flood(chat_id: str, user_id):
    with INSERTION_LOCK:
        flood = SESSION.query(FloodControl).get(str(chat_id))
        if not flood:
            flood = FloodControl(str(chat_id))
            SESSION.add(flood)

        if not flood.limit:
            SESSION.close()
            return False

        if user_id is None:
            flood.user_id = None
            flood.count = 0
            SESSION.commit()
            SESSION.close()
            return False

        if flood.user_id == user_id:
            flood.count += 1
            if flood.count > flood.limit:
                SESSION.commit()
                SESSION.close()
                return True
        else:
            flood.user_id = user_id
            flood.count = 1

        SESSION.commit()
        SESSION.close()
        return False


def set_flood(chat_id, amount):
    with INSERTION_LOCK:
        flood = SESSION.query(FloodControl).get(str(chat_id))
        if not flood:
            flood = FloodControl(str(chat_id))
            SESSION.add(flood)

        flood.limit = amount
        SESSION.commit()
        SESSION.close()


def get_flood_limit(chat_id):
    flood = SESSION.query(FloodControl).get(str(chat_id))
    if not flood:
        SESSION.close()
        return 0
    SESSION.close()
    return flood.limit


def get_flood_setting(chat_id):
    setting = SESSION.query(FloodSettings).get(str(chat_id))
    if setting:
        return setting.flood_mode, setting.value
    return 1, "0"


def set_flood_strength(chat_id, flood_mode, value):
    with INSERTION_LOCK:
        setting = SESSION.query(FloodSettings).get(str(chat_id))
        if not setting:
            setting = FloodSettings(str(chat_id), flood_mode, value)
            SESSION.add(setting)
        else:
            setting.flood_mode = flood_mode
            setting.value = value
        SESSION.commit()
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        flood = SESSION.query(FloodControl).get(str(old_chat_id))
        if flood:
            flood.chat_id = str(new_chat_id)
            SESSION.commit()
        setting = SESSION.query(FloodSettings).get(str(old_chat_id))
        if setting:
            setting.chat_id = str(new_chat_id)
            SESSION.commit()
        SESSION.close()
