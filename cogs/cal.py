import discord
import json
import re
import asyncio
import requests
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from datetime import datetime, timedelta, timezone
import icalendar
from icalendar import Calendar
from dateutil.rrule import *
from define_stuff import Funcs
from .reminder import UserNotFound

with open("./config.json") as f:
    config = json.load(f)


def parse_recurrences(recur_rule, start, exclusions):
    """ Find all reoccuring events """
    rules = rruleset()
    first_rule = rrulestr(recur_rule, dtstart=start)
    rules.rrule(first_rule)
    if not isinstance(exclusions, list):
        exclusions = [exclusions]
        for xdate in exclusions:
            try:
                rules.exdate(xdate.dts[0].dt)
            except AttributeError:
                pass
    now = datetime.now(timezone.utc)
    this_year = now + timedelta(days=60)
    dates = []
    for rule in rules.between(now, this_year):
        dates.append(rule.strftime("%D %H:%M UTC "))
    return dates


class Cal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.functions = Funcs()
        self.check_assignments.start()

    @commands.command(aliases=['cal', 'calender', 'usercal',
                               'calenders'])  # Calender stuff, this was the 1st use of me making interactive msgs. (help and reminderlog are partly copy pasted)
    async def calendar(self, ctx):
        giant_str = ""
        warning_msg = None
        if self.functions.check_if_user_setup_in_db(user_id=ctx.message.author.id) is True:
            url = self.functions.get_cal_link(user_id=ctx.message.author.id)
            url = str(url).split(",")[2].replace("'", "").replace(" ", "")
            temp = []
            pages = {}
            page_count = 0
            calender_page = 1
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                color = self.functions.get_guild_color(ctx.guild.id)
            else:
                color = 0x00d4f0
            HEADERS = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
            }
            icalfile = requests.get(url, headers=HEADERS).text
            gcal = Calendar.from_ical(icalfile)
            for component in gcal.walk():
                if component.name == "VEVENT":
                    summary = component.get('summary')
                    enddt = component.get('dtend').dt
                    link = component.get('url')
                    if len(giant_str + f"{summary}\nLink: {link}\nDue Date:{enddt}\n\n") < 1000:
                        giant_str = str(giant_str) + f"{summary}\nLink: {link}\n Due Date: {enddt}\n\n"
                    else:
                        temp.append(giant_str)
                        giant_str = ""
                        continue
            temp.append(giant_str)
            for x in temp:
                page_count = page_count + 1
                pages["page{0}".format(page_count)] = f"{x}"
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                embed = self.functions.cal_embed(title=f"{ctx.message.author.name}'s Calender", current_page=f"1",
                                                 max_page=f"{page_count}", desc=pages[f"page{calender_page}"],
                                                 color=color)
            else:
                embed = self.functions.cal_embed(title=f"{ctx.message.author.name}'s Calender", current_page=f"1",
                                                 max_page=f"{page_count}", desc=pages[f"page{calender_page}"])
            temp.clear()

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ['⬅️', '➡️']

            msg = await ctx.send(embed=embed)
            if isinstance(ctx.channel, discord.channel.DMChannel):
                warning = self.functions.warning_embed(title="Warning!",
                                                       warning="This is a Direct Message channel for the best experience it's recomended to use this in a guild over private messages.\nYou will have to react and unreact each time you want to change the page")
                warning_msg = await ctx.send(embed=warning)
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")
            try:
                while calender_page <= page_count:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                    if reaction.emoji == '➡️':
                        if calender_page < page_count:
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('➡️', ctx.message.author)
                            calender_page = calender_page + 1
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.edit(
                                    embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Calender!",
                                                                   current_page=f"{calender_page}",
                                                                   max_page=f"{page_count}",
                                                                   desc=pages[f"page{calender_page}"], color=color))
                            else:
                                await msg.edit(
                                    embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Calender!",
                                                                   current_page=f"{calender_page}",
                                                                   max_page=f"{page_count}",
                                                                   desc=pages[f"page{calender_page}"], ))
                        else:
                            await ctx.send("You're already on the last page!", delete_after=5)
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('➡️', ctx.message.author)
                    elif reaction.emoji == '⬅️':
                        if calender_page - 1 > 0:
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('⬅️', ctx.message.author)
                            calender_page = calender_page - 1
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.edit(
                                    embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Calender!",
                                                                   current_page=f"{calender_page}",
                                                                   max_page=f"{page_count}",
                                                                   desc=pages[f"page{calender_page}"], color=color))
                            else:
                                await msg.edit(
                                    embed=self.functions.cal_embed(title=f"{ctx.message.author.name}'s Calender!",
                                                                   current_page=f"{calender_page}",
                                                                   max_page=f"{page_count}",
                                                                   desc=pages[f"page{calender_page}"], ))
                        else:
                            await ctx.send("You're on the first page already!", delete_after=5)
                            if not isinstance(ctx.channel, discord.channel.DMChannel):
                                await msg.remove_reaction('⬅️', ctx.message.author)

            except asyncio.TimeoutError:  # Indent error here, delete one tabulation
                await ctx.send(f"{ctx.message.author.name} is inactive... Deleting their calendar so there isn't spam.")
                await asyncio.sleep(60)
                await msg.delete()
                if not isinstance(ctx.channel, discord.channel.DMChannel):
                    await ctx.message.delete()
                else:
                    if warning_msg is not None:
                        await warning_msg.delete()
        else:
            embed = self.functions.error_embed(title=f"Error!",
                                               error=f"You were not found in the database!\nPlease use `.setup` (in Direct Messages) to set up your calender!")
            await ctx.send(embed=embed)

    @tasks.loop(minutes=1)
    async def check_assignments(self):
        if datetime.now().minute % 5 == 0:
            want_updates = self.functions.get_userid_and_ical()
            for user in want_updates:
                ical_str = ""
                user = user[0]
                old = self.functions.get_old_cal_text(user_id=user)
                old = old[0]
                url = self.functions.get_cal_link(user_id=int(user))
                icalfile = requests.get(url[2]).text
                try:
                    gcal = Calendar.from_ical(icalfile)
                except ValueError:
                    user = self.bot.get_user(int(user))
                    try:
                        await user.send("You disabled your ical link. if you didn't contact Yousef#9999")
                    except:
                        pass
                    self.functions.force_ical_updates_off(user_id=int(user.id))
                    print(f"forced {user}'s auto announce off")
                    continue
                no_text = False if old is None else True
                if gcal is None:
                    continue
                for component in gcal.walk():
                    if component.name == "VEVENT":
                        link = component.get('url')
                        link = link.replace("\n", "") if "\n" in str(link) else link
                        link = link.replace("'", "") if "'" in str(link) else link
                        link = str(link).split("/")[4]
                        if link == "":
                            continue
                        else:
                            ical_str = ical_str + f"{link}:s:"
                            continue
                if no_text is False:
                    await self.functions.update_ical_text(user_id=user, text=ical_str)
                    continue
                else:
                    temp = [x for x in ical_str.split(":s:")]
                    old_list = [x for x in str(old.replace("\n", "").replace("'", "")).split(":s:")]
                    for x in old_list:
                        if x in temp:
                            temp.remove(x)
                    old_list.clear()
                    if temp:
                        for x in temp:
                            for component in gcal.walk():
                                if component.name == f"VEVENT":
                                    summary = component.get('summary')
                                    description = component.get('description')
                                    enddt = component.get('dtend').dt
                                    link = component.get('url')
                                    full_link = link
                                    link = link.replace("\n", "") if "\n" in str(link) else link
                                    link = link.replace("'", "") if "'" in str(link) else link
                                    link = str(link).split("/")[4]
                                    if link == f"{x}":
                                        description = str(description).split("- Link:")[0] if "- Link:" in str(description) else description
                                        summary = str(summary).replace("\n", "") if "\n" in str(summary) else summary
                                        summary = str(summary).replace("'", "") if "'" in str(summary) else summary
                                        dm_user = self.bot.get_user(int(user))
                                        if dm_user is None:
                                            try:
                                                dm_user = await self.bot.fetch_user(int(user))
                                                if dm_user is None:
                                                    break
                                            except:
                                                break
                                        embed = self.functions.dm_user_embed(title=f"{summary}",
                                                                             desc=f"{description}\n\nLink: {full_link}",
                                                                             footer=f"Due date: {enddt}")
                                        try:
                                            message = await dm_user.send(f"{dm_user.mention}")
                                            await message.edit(embed=embed)
                                        finally:
                                            continue
                        await self.functions.update_ical_text(user_id=user, text=ical_str)
                        continue
                    else:
                        continue

    @check_assignments.error
    async def check_assigements_error(self, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            pass

def setup(bot):
    bot.add_cog(Cal(bot))
