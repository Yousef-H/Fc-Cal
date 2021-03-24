import discord
import json
import re
import asyncio
import sqlite3
import time
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from define_stuff import Funcs  # custom import from define_stuff.py its very much needed across all of the bot.

with open("./config.json") as f:
    config = json.load(f)


# the config isnt used at all in this file.

class ChannelNotFound:
    """
    Raised when the bot cant find a channel
    """
    pass

class UserNotFound:
    """
    Raised when the bot cant find a user
    """
    pass

class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.functions = Funcs()
        self.reminder_check.start()

    @commands.command(aliases=['remind','remindme'])
    async def reminder(self, ctx, reminder_time, date, *, reminder):
        if len(reminder) < 450:
            am_pm_match = re.search(r'\b((1[0-2]|0?[1-9]):([0-5][0-9])([AaPp][Mm]))', reminder_time)
            if am_pm_match:
                reminder_time = self.functions.convert_am_pm_army(time_convert=reminder_time)
            time_match = re.search(r'(\d:\d+)', reminder_time)
            date_match = re.search(r'(\d{2}(\/?)){3}', date)
            if time_match and date_match:
                str_convert = str(reminder_time).replace(f"{reminder_time}", f"{reminder_time}:00")
                final_time = str_convert + f"/{date}"
                if await self.functions.check_valid(f"{final_time}") is True:
                    if await self.functions.check_if_reminder_in_db(user_id=ctx.message.author.id,
                                                              channel_id=ctx.message.channel.id, date=final_time,
                                                              reminder=reminder) is False:
                        await self.functions.insert_reminder(user_id=ctx.message.author.id,channel_id=ctx.message.channel.id,date=final_time, reminder=reminder)
                        embed = self.functions.embed_basic(title="Success", desc=f"I will remind you when the time is up!")
                        await ctx.send(embed=embed)
                    else:
                        error_embed = self.functions.error_embed(title="Error",
                                                                 error=f"You are already set to be reminded about this.")
                        await ctx.send(embed=error_embed)
                else:
                    error_embed = self.functions.error_embed(title="Error", error=f"{reminder_time} {date} is already in the past. Please input a future date.")
                    await ctx.send(embed=error_embed)

            else:
                error_embed = self.functions.error_embed(title="Invalid usage!",
                                                         error=f"{ctx.prefix}remind <time> <date> <reminder>")
                await ctx.send(embed=error_embed)
        else:
            error_embed = self.functions.error_embed(title="Error",
                                                     error=f"Your reminder is over the character limit of 450. ({len(reminder)})")
            await ctx.send(embed=error_embed)


    @commands.command(aliases=['rlog','remindlog'])
    async def reminderlog(self, ctx):
        reminder_page_str = ""
        temp = []
        pages = {}
        page_count = 0
        reminder_page = 1
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            color = self.functions.get_guild_color(ctx.guild.id)
        else:
            color = 0x00d4f0
        reminder_list = self.functions.get_all_user_reminders(user_id=ctx.message.author.id)
        print(reminder_list)
        if not reminder_list:
            error_embed = self.functions.error_embed(title="Error!", error="You have no reminders in my database!")
            await ctx.send(embed=error_embed)
            return
        else:
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ['⬅️', '➡️']
            for reminder in reminder_list:
                print(reminder)
                r_id = reminder[0]
                time_date = reminder[3]
                remind = reminder[4]
                valid_or_not = reminder[5]
                if valid_or_not == 0:
                    valid_or_not = "Expired"
                elif valid_or_not == 1:
                    valid_or_not = "Not Expired"
                separate_time_date = time_date.split('/')
                db_time = separate_time_date[0]
                date = separate_time_date[1] + "/" + separate_time_date[2] + "/20" + separate_time_date[3]
                if len(
                        reminder_page_str + f"{r_id}. {valid_or_not} reminder\nExpire Time: {db_time} Date: {date}\nReminder: {remind}\n") < 475:
                    reminder_page_str = reminder_page_str + f"{r_id}. {valid_or_not} reminder\nExpire Time: {db_time} Date: {date}\nReminder: {remind}\n"
                else:
                    temp.append(reminder_page_str)
                    reminder_page_str = ""
                    continue
            if temp:
                for x in temp:
                    print(x)
                    page_count = page_count + 1
                    pages["page{0}".format(page_count)] = f"{x}"
                if not isinstance(ctx.channel, discord.channel.DMChannel):
                    embed = self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log", current_page=f"1",
                                                     max_page=f"{page_count}", desc=pages[f"page{reminder_page}"], color=color)
                else:
                    embed = self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log", current_page=f"1",
                                                     max_page=f"{page_count}", desc=pages[f"page{reminder_page}"])
                temp.clear()
            else:
                embed = self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log", current_page=f"1",
                                                 max_page=f"1", desc=reminder_page_str,
                                                 color=color)
            msg = await ctx.send(embed=embed)
            if isinstance(ctx.channel, discord.channel.DMChannel):
                warning = self.functions.warning_embed(title="Warning!",warning="This is a Direct Message channel for the best experience it's recomended to use this in a guild over private messages.\nYou will have to react and unreact each time you want to change the page")
                warning_msg = await ctx.send(embed=warning)
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")
            try:
                while reminder_page <= page_count:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                    if reaction.emoji == '➡️':
                        if reminder_page < page_count:
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('➡️', ctx.message.author)
                            reminder_page = reminder_page + 1
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.edit(
                                embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log",
                                                               current_page=f"{reminder_page}",
                                                               max_page=f"{page_count}",
                                                               desc=pages[f"page{reminder_page}"], color=color))
                            else:
                                await msg.edit(
                                embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log",
                                                               current_page=f"{reminder_page}",
                                                               max_page=f"{page_count}",
                                                               desc=pages[f"page{reminder_page}"]))
                        else:
                            await ctx.send(f"You're already on the last page! {ctx.message.author.mention}", delete_after=5)
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('➡️', ctx.message.author)
                    elif reaction.emoji == '⬅️':
                        if reminder_page - 1 > 0:
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('⬅️', ctx.message.author)
                            reminder_page = reminder_page - 1
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.edit(
                                embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log",
                                                               current_page=f"{reminder_page}",
                                                               max_page=f"{page_count}",
                                                               desc=pages[f"page{reminder_page}"], color=color))
                            else:
                                await msg.edit(
                                embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Reminder Log",
                                                               current_page=f"{reminder_page}",
                                                               max_page=f"{page_count}",
                                                               desc=pages[f"page{reminder_page}"]))
                        else:
                            await ctx.send(f"You're on the first page already! {ctx.message.author.mention}",
                                           delete_after=5)
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('⬅️', ctx.message.author)
            except asyncio.TimeoutError:  # Indent error here, delete one tabulation
                await ctx.send(
                    f"{ctx.message.author.name} is inactive... Deleting their reminder log so there isn't spam.")
                await asyncio.sleep(30)
                await msg.delete()
                if not isinstance(ctx.channel, discord.channel.DMChannel):
                    await ctx.message.delete()
                else:
                    await warning_msg.delete()

    @tasks.loop(seconds=1)
    async def reminder_check(self):
        await self.bot.wait_until_ready()
        if datetime.now().second == 00:
            row_date = self.functions.check_time_pass()
            for item in row_date:
                row = item[0]
                print(item)
                if self.functions.check_if_time_expire(item[3]) is True:
                    reminder_info = self.functions.expire_msg(row=row)
                    r_id = reminder_info[0]
                    u_id = reminder_info[1]
                    c_id = reminder_info[3]
                    remind = reminder_info[4]
                    embed = self.functions.embed_basic(f"Reminder expired!", desc=f"{remind}")
                    embed.set_footer(text=f"Reminder ID: {r_id}")
                    try:
                        channel = self.bot.get_channel(id=c_id)
                        if channel is None:
                            raise ChannelNotFound
                        else:
                            msg = await channel.send(f"<@!{u_id}>")
                            await msg.edit(embed=embed)
                    except Exception as e:
                        try:
                            user = self.bot.get_user(u_id)
                            if user is not None:
                                msg = await user.send(
                                f"<@!{u_id}> I could not remind you in the guild due to an error so I am reminding you here!")
                                await msg.edit(embed=embed)
                            else:
                                user = await self.bot.fetch_user(u_id)
                                if user is not None:
                                    try:
                                        msg = await user.send(
                                            f"<@!{u_id}> I could not remind you in the guild due to an error so I am reminding you here!")
                                        await msg.edit(embed=embed)
                                    except:
                                        pass
                                else:
                                    raise UserNotFound
                        except:
                            pass
                    self.functions.mark_invaild_reminder(reminder_id=r_id)


    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            error_embed = self.functions.error_embed(title="Invalid Usage!",
                                                     error=f"{ctx.prefix}reminder <time> <date> <reminder>")
            await ctx.send(embed=error_embed)
        elif isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            error_embed = self.functions.error_embed(title="Invalid Time/Date!",
                                                     error=f"if you put the full year shorten it to the last 2 digits "
                                                           f"(2020 = 20 2021 = 21)")
            await ctx.send(embed=error_embed)
        else:
            raise error



def setup(bot):
    bot.add_cog(Remind(bot))
