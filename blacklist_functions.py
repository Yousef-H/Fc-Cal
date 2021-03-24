import discord
import sqlite3


class Blacklist:
    def __int__(self, bot):
        self.bot = bot

    def is_user_blacklisted(self, user_id) -> bool:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT valid FROM blacklist WHERE blacklisted_user_id = {user_id} AND valid = 1")
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            db.close()
            return False
        elif result is not None:
            cursor.close()
            db.close()
            return True

    def get_blacklist_info(self, user_id) -> [list, None]:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT * FROM blacklist WHERE blacklisted_user_id = {user_id} AND valid = 1")
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is not None:
            return result
        else:
            return None

    def insert_blacklist(self, user_id, reason, punishier_id) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = ("INSERT INTO blacklist(punisher_user_id,blacklisted_user_id,reason,valid) VALUES(?,?,?,?)")
        val = (punishier_id, user_id, reason, 1)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return

    def unblacklist_user(self, user_id) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"UPDATE blacklist SET valid = 0 WHERE blacklisted_user_id = {user_id}")
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
        return
