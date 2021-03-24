import discord
import json
import asyncio
import sqlite3
import time
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from define_stuff import Funcs
from discord.utils import find

with open("./config.json") as f:
    config = json.load(f)


# this is a pretty nice file I recommended it tbh


class User_guild_setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.functions = Funcs()
        self.high_school_mentions.start()
        self.middle_school_mentions.start()

    #   Tuesday odd
    #   Wednesday Evan
    #   Thursday Odd
    #   Friday Even
    #
    # Message idea: @everyone there is 5 minutes before {prd} starts! Be sure to join before that
    # @everyone there is only 5 minutes left of {prd}! :party:

    @tasks.loop(minutes=1)
    async def high_school_mentions(self):
        even_or_odd = ""
        x = datetime.today().strftime("%A")
        y = datetime.today().strftime("%I:%M%p")
        if x == "Wednesday" or x == "Friday":
            even_or_odd = "evan"
        elif x == "Tuesday" or x == "Thursday":
            even_or_odd = "odd"
        if even_or_odd == "":
            return
        else:
            period = ""
            try:
                if y == "08:05AM":
                    if even_or_odd == "evan":
                        period = "2nd"
                    elif even_or_odd == "odd":
                        period = "1st"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "09:25AM":
                    if even_or_odd == "evan":
                        period = "2nd"
                    elif even_or_odd == "odd":
                        period = "1st"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes!")
                elif y == "09:40AM":
                    if even_or_odd == "evan":
                        period = "4th"
                    elif even_or_odd == "odd":
                        period = "3rd"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "11:00AM":
                    if even_or_odd == "evan":
                        period = "4th"
                    elif even_or_odd == "odd":
                        period = "3rd"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes! Enjoy your lunch!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes! Enjoy your lunch!")
                elif y == "11:55AM":
                    if even_or_odd == "evan":
                        period = "6th"
                    elif even_or_odd == "odd":
                        period = "5th"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "01:15PM":
                    if even_or_odd == "evan":
                        period = "6th"
                    elif even_or_odd == "odd":
                        period = "5th"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes!")
                elif y == "01:30PM":
                    if even_or_odd == "evan":
                        period = "9th"
                    elif even_or_odd == "odd":
                        period = "7th"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "02:50PM":
                    if even_or_odd == "evan":
                        period = "8th"
                    elif even_or_odd == "odd":
                        period = "7th"
                    guilds = self.functions.get_guilds_high()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes! Enjoy the rest of your day :sunglasses:")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes! Enjoy the rest of your day :sunglasses:")
                else:
                    return
            except AttributeError:
                return

    @tasks.loop(minutes=1)
    async def middle_school_mentions(self):
        even_or_odd = ""
        x = datetime.today().strftime("%A")
        y = datetime.today().strftime("%I:%M%p")
        if x == "Wednesday" or x == "Friday":
            even_or_odd = "evan"
        elif x == "Tuesday" or x == "Thursday":
            even_or_odd = "odd"
        if even_or_odd == "":
            return
        else:
            period = ""
            try:
                if y == "07:25AM":
                    if even_or_odd == "evan":
                        period = "2nd"
                    elif even_or_odd == "odd":
                        period = "1st"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "08:45AM":
                    if even_or_odd == "evan":
                        period = "2nd"
                    elif even_or_odd == "odd":
                        period = "1st"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes!")
                elif y == "09:00AM":
                    if even_or_odd == "evan":
                        period = "4th"
                    elif even_or_odd == "odd":
                        period = "3rd"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "10:20AM":
                    if even_or_odd == "evan":
                        period = "4th"
                    elif even_or_odd == "odd":
                        period = "3rd"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes!")
                elif y == "11:10AM":
                    if even_or_odd == "evan":
                        period = "6th"
                    elif even_or_odd == "odd":
                        period = "5th"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "12:35PM":
                    if even_or_odd == "evan":
                        period = "6th"
                    elif even_or_odd == "odd":
                        period = "5th"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes!")
                elif y == "12:50PM":
                    if even_or_odd == "evan":
                        period = "9th"
                    elif even_or_odd == "odd":
                        period = "7th"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is starting in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is starting in 5 minutes!")
                elif y == "02:10PM":
                    if even_or_odd == "evan":
                        period = "8th"
                    elif even_or_odd == "odd":
                        period = "7th"
                    guilds = self.functions.get_guilds_middle()
                    for guild_id in guilds:
                        if "(" in str(guild_id):
                            guild_id = guild_id.replace("(", "").replace(",)", "")
                            guild_channel = self.functions.get_guild_channel_high(guild_id=guild_id)
                            role_id = self.functions.get_guild_mention_role(guild_id=guild_id)
                            channel = self.bot.get_channel(id=int(guild_channel))
                            if role_id == "default":
                                await channel.send(f"@everyone {period} period is ending in 5 minutes!")
                            else:
                                await channel.send(f"<@&{role_id}> {period} period is ending in 5 minutes!")
                else:
                    return
            except AttributeError:
                return


def setup(bot):
    bot.add_cog(User_guild_setup(bot))
