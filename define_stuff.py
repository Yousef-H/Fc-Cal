import sqlite3
import time
import discord
import json
from sqlite3 import Error
from discord_webhook import DiscordWebhook, DiscordEmbed


# Welcome to the main file functions if u look at the reminders.py file the reminder command is just functions this
# file is the most important part of the bot

with open("./config.json") as configfile:
    config = json.load(configfile)
    web_hook_link = str(config.get('logger_webhook'))

class Funcs:
    def __int__(self, bot):
        self.bot = bot

    async def insert_guild_id(self, guild_id) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT * FROM guild_settings WHERE guild_id = {guild_id}")
        cursor.execute(sql)
        check = cursor.fetchone()
        if check is None:
            sql2 = ("INSERT INTO guild_settings(guild_id,prefix,guild_embed_color,done_setup) VALUES(?,?,?,?)")
            val2 = (guild_id, ".", "cyan", 0)
            cursor.execute(sql2, val2)
            db.commit()
            cursor.close()
            db.close()
            return
        else:
            return

    async def update_prefix(self, prefix, guild_id) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"UPDATE guild_settings SET prefix = ? WHERE guild_id = ?")
        val = (prefix, guild_id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return


    def convert_am_pm_army(self, time_convert) -> str:
        time_convert = str(time_convert).lower()
        if time_convert.endswith('am'):
            time_convert = time_convert[:-2]
            actual_convert = time_convert.split(":")[0]
            rest_of_time = time_convert.split(":")[1]
            return f"{actual_convert}:{rest_of_time}"
        elif time_convert.endswith('pm'):
            time_convert = time_convert[:-2]
            actual_convert = int(time_convert.split(":")[0])
            rest_of_time = int(time_convert.split(":")[1])
            final_convert = actual_convert + 12
            return f"{final_convert}:{rest_of_time}"
        else:
            return "00:00"

    async def check_valid(self, date) -> bool:
        get_time = time.strftime("%H:%M:%S/%m/%d/%y")
        current_time = time.strptime(get_time, "%H:%M:%S/%m/%d/%y")
        final_date = time.strptime(date, "%H:%M:%S/%m/%d/%y")
        if current_time < final_date:
            return True
        else:
            return False

    async def insert_reminder(self, user_id, channel_id, date, reminder) -> None:
        try:
            db = sqlite3.connect('bot_db.sqlite')
            cursor = db.cursor()
            sql = (f"INSERT INTO reminders(user_id, channel_id, date, reminder, valid) VALUES(?,?,?,?,?)")
            val = (user_id, channel_id, date, reminder, 1)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            return
        except Exception as error:
            self.webhook_error(error=error, user_id=user_id, channel_id=channel_id, date=date, reminder=reminder)

    async def check_if_reminder_in_db(self, user_id, channel_id, date, *, reminder: str) -> bool:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = ("SELECT ? FROM reminders WHERE channel_id = ? AND date = ? AND reminder = ?")
        val = (user_id, channel_id, date, reminder)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result is None:
            return False
        else:
            return True

    def get_all_user_reminders(self, user_id) -> list:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f'SELECT * FROM reminders WHERE user_id = {user_id}')
        cursor.execute(sql)
        return cursor.fetchall()

    def webhook_error(self, error, remind_id="n/a", user_id="n/a", channel_id="n/a", date="n/a", reminder="n/a") -> None:
        webhook = DiscordWebhook(
            url=web_hook_link,
            username=f"Bot Error!")
        embed = DiscordEmbed(title='An error has occurred!',
                             description=f'`{error}` has occurred! Debug info:\n Remind ID= ||{remind_id}||\nUser Mention/ID= ||<@{user_id}> + {user_id}||\nChannel ID = ||{channel_id}||\nDate Sent to SQL= ||{date}||\nReminder Text= ||{reminder}||',
                             color=0xd60000)
        embed.set_footer(text=f"Error logger (Mainly for devs to look at and try to fix)")
        webhook.add_embed(embed)
        webhook.execute()
        return

    def embed_basic(self, title, desc=None) -> discord.Embed:
        if desc is None:
            embed = discord.Embed(title=title, color=0x00d4f0)
        else:
            embed = discord.Embed(title=title, description=desc, color=0x00d4f0)
        return embed

    def check_time_pass(self) -> list:
        #current_valids = []
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = ('SELECT * FROM reminders WHERE valid=1')
        cursor.execute(sql)
        #for x in cursor.fetchall():
        #    string_line = str(x).split(",")
        #    current_valids.append(
        #        string_line[0].replace("'", "").replace(" ", "").replace("(", "") + "-" + string_line[3].replace("'",
        #                                                                                                         "").replace(
        #            " ", ""))
        #cursor.close()
        #db.close()
        return cursor.fetchall()

    def check_if_time_expire(self, date):
        get_time = time.strftime("%H:%M:%S/%m/%d/%y")
        current_time = time.strptime(get_time, "%H:%M:%S/%m/%d/%y")
        final_date = time.strptime(date, "%H:%M:%S/%m/%d/%y")
        if current_time < final_date:
            return False
        else:
            return True

    def expire_msg(self, row) -> list:
        if row is None or False:
            return []
        else:
            db = sqlite3.connect('bot_db.sqlite')
            cursor = db.cursor()
            row = int(row)
            sql = (f'SELECT * FROM reminders WHERE reminder_id={row}')
            cursor.execute(sql)
            return cursor.fetchone()

    def mark_invaild_reminder(self, reminder_id) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = ('UPDATE reminders SET valid = ? WHERE reminder_id = ?')
        val = (0, reminder_id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return

    def cal_embed(self, title, current_page, max_page, desc=None, color=0x00d4f0) -> discord.Embed:
        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text=f"Page: {current_page}/{max_page}")
        return embed

    def get_cal_link(self, user_id) -> list:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM user_settings WHERE discord_user_id = {user_id}')
        result = cursor.fetchone()
        return result

    def check_if_user_setup_in_db(self, user_id) -> bool:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM user_settings WHERE discord_user_id = {user_id}')
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            db.close()
            return False
        elif result is not None:
            cursor.close()
            db.close()
            return True

    def insert_user_setup(self, user_id, ical_link, assignment_announce) -> None:
        try:
            db = sqlite3.connect('bot_db.sqlite')
            cursor = db.cursor()
            # cursor.execute(f'SELECT * from user_settings WHERE discord_user_id= {user_id}')
            sql = ("INSERT INTO user_settings(discord_user_id, ical_link, assignment_announce) VALUES(?,?,?)")
            val = (user_id, ical_link, assignment_announce)
            cursor.execute(sql, val)
            cursor.close()
            db.commit()
            db.close()
            return
        except Exception as e:
            print(f'Error in "insert_user_setup" {e}')
            return

    def update_user_setup(self, user_id, ical_link, assignment_announce) -> None:
        try:
            db = sqlite3.connect('bot_db.sqlite')
            cursor = db.cursor()
            sql = ("UPDATE user_settings SET ical_link = ? WHERE discord_user_id = ?")
            val = (ical_link, user_id)
            cursor.execute(sql, val)
            sql2 = ("UPDATE user_settings SET assignment_announce = ? WHERE discord_user_id = ?")
            val2 = (assignment_announce, user_id)
            cursor.execute(sql2, val2)
            cursor.close()
            db.commit()
            db.close()
            return
        except Exception as e:
            print(f'Error in "update_user_setup" {e}')
            return

    def remove_user_setup(self, user_id) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"DELETE FROM user_settings WHERE discord_user_id = {user_id}")
        try:
            cursor.execute(sql)
            cursor.close()
            db.commit()
            db.close()
            return
        except Exception as e:
            self.webhook_error(error=e, remind_id="N/A", user_id=user_id, channel_id=f"In DMS (SETUP Command)",
                               date=f"Check when was posted",
                               reminder=f"Not a reminder!")
            cursor.close()
            db.close()
            return

    def error_embed(self, title=f"An Error has Occurred!", error="Please make a ticket!") -> discord.Embed:
        embed = discord.Embed(title=title, description=error, color=0xd60000)
        return embed

    def warning_embed(self, title="Warning!", warning="ops this wasn't defined properly!") -> discord.Embed:
        embed = discord.Embed(title=title, description=warning, color=0xea8b06)
        return embed

    def get_old_cal_text(self, user_id) -> list:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f'SELECT old_text FROM user_settings WHERE discord_user_id = {user_id}')
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result

    async def update_ical_text(self, user_id, text) -> None:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f'UPDATE user_settings SET old_text = ? WHERE discord_user_id = ?')
        val = (text, user_id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return

    @staticmethod
    def get_userid_and_ical() -> list:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f'SELECT discord_user_id, ical_link FROM user_settings WHERE assignment_announce = 1')
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def dm_user_embed(self, title, desc, footer) -> discord.Embed:
        embed = discord.Embed(title=title, description=desc, color=0x00d4f0)
        embed.set_footer(text=footer, icon_url="https://i.imgur.com/v2Bz33Z.png")
        return embed

    def check_guild_settings(self, guild_id) -> bool:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT done_setup FROM guild_settings WHERE guild_id = {guild_id}")
        cursor.execute(sql)
        result = cursor.fetchone()
        if result[0] == 0:
            return False
        elif result[0] == 1:
            return True

    def insert_guild_settings(self, guild_id, guild_color, want_middle_school, want_high_school,
                              middle_school_channel_id, high_school_channel_id, role_id) -> None:
        commands = [f"UPDATE guild_settings SET guild_embed_color = '{guild_color}' WHERE guild_id = {guild_id}",
                    f"UPDATE guild_settings SET done_setup = 1 WHERE guild_id = {guild_id}"]
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        if want_middle_school is True:
            commands.append(f"UPDATE guild_settings SET middle_school_noti = 1 WHERE guild_id = {guild_id}")
            commands.append(f"UPDATE guild_settings SET middle_school_channel = {middle_school_channel_id} WHERE guild_id = {guild_id}")
        else:
            commands.append(f"UPDATE guild_settings SET middle_school_noti = 0 WHERE guild_id = {guild_id}")
            commands.append(f"UPDATE guild_settings SET middle_school_channel = NULL where guild_id = {guild_id}")
        if want_high_school is True:
            commands.append(f"UPDATE guild_settings SET high_school_noti = 1 WHERE guild_id = {guild_id}")
            commands.append(f"UPDATE guild_settings SET high_school_channel = {high_school_channel_id} WHERE guild_id = {guild_id}")
        else:
            commands.append(f"UPDATE guild_settings SET high_school_noti = 0 WHERE guild_id = {guild_id}")
            commands.append(f"UPDATE guild_settings SET high_school_channel = NULL WHERE guild_id = {guild_id}")
        if want_high_school or middle_school_channel_id is True:
            commands.append(f"UPDATE guild_settings SET class_mention_role_id = {role_id} WHERE guild_id = {guild_id}")
        elif want_high_school and want_middle_school is False:
            commands.append(f"UPDATE guild_settings SET class_mention_role_id = NULL WHERE guild_id = {guild_id}")
        for cmd in commands:
            try:
                cursor.execute(cmd)
            except Error as e:
                print(f"error with sqlite:\n{e}")
        cursor.close()
        db.commit()
        db.close()
        return

    def get_guild_color(self, guild_id) -> int:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT guild_embed_color FROM guild_settings where guild_id = {guild_id}")
        cursor.execute(sql)
        result = cursor.fetchone()
        color = {'cyan':0x00d4f0,
                 'red':0xd60000,
                 'purple':0xd580ff,
                 'pink':0xffb3d9,
                 'orange':0xea8b06,
                 'lime':0x27ec48,
                 'brown':0x2eb82e,
                 'green':0x2eb82e,
                 'black':0x000000,
                 'blue':0x0a40a3,
                 'gray':0xbfbfbf,
                 'white':0xffffff,
                 'yellow':0xd4e208}
        return color[f'{result[0]}']

    def get_guilds_high(self) -> list:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT guild_id FROM guild_settings WHERE high_school_noti = 1")
        cursor.execute(sql)
        return cursor.fetchall()

    def get_guilds_middle(self) -> list:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT guild_id FROM guild_settings WHERE middle_school_noti = 1")
        cursor.execute(sql)
        return cursor.fetchall()

    def get_guild_channel_high(self, guild_id) -> str:
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT high_school_channel FROM guild_settings WHERE guild_id = {guild_id}")
        cursor.execute(sql)
        channel_id = cursor.fetchone()
        channel_id = channel_id[0]
        if "<#" in str(channel_id):
            channel_id = str(channel_id).replace("<#", "").replace(">", "")
        return channel_id

    def get_guild_channel_middle(self, guild_id):
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT middle_school_channel FROM guild_settings WHERE guild_id = {guild_id}")
        cursor.execute(sql)
        channel_id = cursor.fetchone()
        if "('<#" in str(channel_id):
            channel_id = str(channel_id).replace("('<#", "").replace(">',)", "")
        elif "('" in str(channel_id):
            channel_id = str(channel_id).replace("('", "").replace("',)", "")
        return channel_id

    def get_guild_mention_role(self, guild_id):
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT class_mention_role_id FROM guild_settings WHERE guild_id = {guild_id}")
        cursor.execute(sql)
        role_id = cursor.fetchone()
        role_id = role_id[0]
        if role_id is None:
            return "default"
        if "<@&" in str(role_id):
            role_id = str(role_id).replace("<@&", "").replace(">", "")
        if str(role_id.lower()) == "default":
            return "default"
        else:
            return role_id

    @staticmethod
    def force_ical_updates_off(user_id):
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = ("UPDATE user_settings SET assignment_announce = ? WHERE discord_user_id = ?")
        val = (0, user_id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return

    def is_user_blacklisted(self, user_id):
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT * FROM blacklist WHERE blacklisted_user_id = {user_id}")
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

    def get_blacklist_info(self, user_id):
        db = sqlite3.connect('bot_db.sqlite')
        cursor = db.cursor()
        sql = (f"SELECT * FROM blacklist WHERE blacklisted_user_id = {user_id}")
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is not None:
            return result
        else:
            return result
