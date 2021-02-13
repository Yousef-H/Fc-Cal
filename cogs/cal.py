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

with open("./config.json") as f:
    config = json.load(f)
try:
    bot_owner = int(config['bot_owner_id'])
except Exception as e:
    print(f"Error! {e} (could be caused by an invalid config, or if you didn't put the DISCORD ID) (cal.py file)")

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
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            }
            icalfile = requests.get(url, headers=HEADERS).text
            gcal = Calendar.from_ical(icalfile)
            for component in gcal.walk():
                if component.name == "VEVENT":
                    summary = component.get('summary')
                    description = component.get('description')
                    location = component.get('location')
                    startdt = component.get('dtstart').dt
                    enddt = component.get('dtend').dt
                    exdate = component.get('exdate')
                    link = component.get('url')
                    #                if component.get('rrule'):
                    #                    reoccur = component.get('rrule').to_ical().decode('utf-8') # I got part of this from the internet, I honestly couldn't have figured it out
                    #                    for item in parse_recurrences(reoccur, startdt, exdate): # link: https://gist.github.com/meskarune/63600e64df56a607efa211b9a87fb443
                    #                        print("{0} {1}: {2} - {3}\n".format(item, summary, description, location))
                    #                else:
                    if len(giant_str + f"{summary}\nLink: {link}\nDue Date:{enddt}\n\n") < 1000:
                        giant_str = str(giant_str) + f"{summary}\nLink: {link}\n Due Date: {enddt}\n\n"
                    else:
                        temp.append(giant_str)
                        giant_str = ""
                        continue
            temp.append(giant_str)
            giant_str = ""
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
                    await warning_msg.delete()
        else:
            embed = self.functions.error_embed(title=f"Error!",
                                               error=f"You were not found in the database!\nPlease use `.setup` (in Direct Messages) to set up your calender!")
            await ctx.send(embed=embed)

    @commands.command()
    async def silentcheck(self, ctx, user_id=None): #debug command to seee if someone changed ical files...
        user_id = ctx.message.author.id if user_id is None else user_id
        if ctx.message.author.id != bot_owner: 
            return
        if self.functions.check_if_user_setup_in_db(user_id=user_id) is True:
            user = self.bot.get_user(int(user_id))
            gcal = None
            ical_str = ""
            old = self.functions.get_old_cal_text(user_id=user_id)
            old = str(old)
            url = self.functions.get_cal_link(user_id=user_id)
            url = str(url).split(",")[2].replace("'", "")
            icalfile = requests.get(url).text
            try:
                gcal = Calendar.from_ical(icalfile)
            except ValueError:
                user = self.bot.get_user(user_id)
                try:
                    await user.send("You disabled your ical link. if you didn't contact the owner of this bot!")
                except:
                    pass
                self.functions.force_ical_updates_off(user_id=user_id)
                await ctx.send("DEBUG: User turned their ICAL Link off.")
                return
            if old.startswith("("):
                old = old[1:]
            if old.endswith(",)"):
                old = old[:-2]
            #if old == "None":
            #    no_text = False
            #else:
            #    no_text = True
            no_text = False if old == "None" else True # this line wasnt tested if its broken delete and uncomment the commented code above it
            if gcal is None:
                await ctx.send(f"DEBUG: Error! gcal value was None/Null!")
                return
            for component in gcal.walk():
                if component.name == "VEVENT":
                    summary = component.get('summary')
                    description = component.get('description')
                    location = component.get('location')
                    startdt = component.get('dtstart').dt
                    enddt = component.get('dtend').dt
                    exdate = component.get('exdate')
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
                self.functions.update_ical_text(user_id=user_id, text=ical_str)
                await ctx.send(f"no_text was false.\nSuccess! Updated {user.mention}'s Calender")
            else:
                temp = [x for x in ical_str.split(":s:")]
                old_list = [x for x in str(old.replace("\n", "").replace("'", "")).split(":s:")]
                print("DEBUG INFO:")
                print("TEMP")
                print(temp)
                print("")
                for x in old_list:
                    if x in temp:
                        temp.remove(x)
                print("OLD_LIST:")
                print(old_list)
                print("")
                if temp:
                    print("NEW TEMP")
                    print(temp)

                    for x in temp:
                        for component in gcal.walk():
                            if component.name == f"VEVENT":
                                summary = component.get('summary')
                                description = component.get('description')
                                location = component.get('location')
                                startdt = component.get('dtstart').dt
                                enddt = component.get('dtend').dt
                                exdate = component.get('exdate')
                                link = component.get('url')
                                full_link = link
                                link = link.replace("\n", "") if "\n" in str(link) else link
                                link = link.replace("'", "") if "'" in str(link) else link
                                link = str(link).split("/")[4]
                                if link == f"{x}":
                                    description = str(description).split("- Link:")[0] if "- Link:" in str(
                                        description) else description
                                    summary = str(summary).replace("\n", "") if "\n" in str(summary) else summary
                                    summary = str(summary).replace("'", "") if "'" in str(summary) else summary
                                    print("")
                                    print(f"FOUND MATCH:\n{summary}\n{full_link} ({link})\n {description}")
                    self.functions.update_ical_text(user_id=ctx.message.author.id, text=ical_str)
                    await ctx.send(f"Success! Updated {user.mention}'s Calender, debug info has been printed.")
                else:
                    await ctx.send(f"Success! Updated {user.mention}'s Calender, debug info has been printed.")
        else:
            embed = self.functions.error_embed(title=f"Error!",
                                               error=f"User was not found in the database!")
            await ctx.send(embed=embed)

    @commands.command()
    async def forcecheck(self, ctx, user_id=None):
        user_id = ctx.message.author.id if user_id is None else user_id
        if ctx.message.author.id != bot_owner:
            return
        if self.functions.check_if_user_setup_in_db(user_id=user_id) is True:
            user = self.bot.get_user(int(user_id))
            gcal = None
            ical_str = ""
            old = self.functions.get_old_cal_text(user_id=user_id)
            old = str(old)
            url = self.functions.get_cal_link(user_id=user_id)
            url = str(url).split(",")[2].replace("'", "")
            icalfile = requests.get(url).text
            try:
                gcal = Calendar.from_ical(icalfile)
            except ValueError:
                user = self.bot.get_user(user_id)
                try:
                    await user.send("You disabled your ical link. if you didn't contact Yousef#9999")
                except:
                    pass
                self.functions.force_ical_updates_off(user_id=user_id)
                await ctx.send("DEBUG: User turned their ICAL Link off.")
                return
            if old.startswith("("):
                old = old[1:]
            if old.endswith(",)"):
                old = old[:-2]
            if old == "None":
                no_text = False
            else:
                no_text = True
            if gcal is None:
                await ctx.send(f"DEBUG: Error! gcal value was None/Null!")
                return
            for component in gcal.walk():
                if component.name == "VEVENT":
                    summary = component.get('summary')
                    description = component.get('description')
                    location = component.get('location')
                    startdt = component.get('dtstart').dt
                    enddt = component.get('dtend').dt
                    exdate = component.get('exdate')
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
                self.functions.update_ical_text(user_id=user_id, text=ical_str)
                await ctx.send(f"no_text was false.\nSuccess! Updated {user.mention}'s Calender")
            else:
                temp = [x for x in ical_str.split(":s:")]
                old_list = [x for x in str(old.replace("\n", "").replace("'", "")).split(":s:")]
                for x in old_list:
                    if x in temp:
                        temp.remove(x)
                if temp:
                    for x in temp:
                        for component in gcal.walk():
                            if component.name == f"VEVENT":
                                summary = component.get('summary')
                                description = component.get('description')
                                location = component.get('location')
                                startdt = component.get('dtstart').dt
                                enddt = component.get('dtend').dt
                                exdate = component.get('exdate')
                                link = component.get('url')
                                full_link = link
                                link = link.replace("\n", "") if "\n" in str(link) else link
                                link = link.replace("'", "") if "'" in str(link) else link
                                link = str(link).split("/")[4]
                                if link == f"{x}":
                                    description = str(description).split("- Link:")[0] if "- Link:" in str(
                                        description) else description
                                    summary = str(summary).replace("\n", "") if "\n" in str(summary) else summary
                                    summary = str(summary).replace("'", "") if "'" in str(summary) else summary
                                    dm_user = self.bot.get_user(user_id)
                                    embed = self.functions.dm_user_embed(title=f"{summary}",
                                                                         desc=f"{description}\n\nLink: {full_link}",
                                                                         footer=f"Due date: {enddt}")
                                    try:
                                        await dm_user.send(f"{dm_user.mention}")
                                        await dm_user.send(embed=embed)
                                    finally:
                                        continue
                    self.functions.update_ical_text(user_id=ctx.message.author.id, text=ical_str)
                    await ctx.send(f"Success! Updated {user.mention}'s Calender")
                else:
                    await ctx.send(f"Success! Updated {user.mention}'s Calender")
        else:
            embed = self.functions.error_embed(title=f"Error!",
                                               error=f"User was not found in the database!")
            await ctx.send(embed=embed)

    @tasks.loop(minutes=1)
    async def check_assignments(self): #background task to check for any new calender updates
        if datetime.now().minute % 5 == 0:
            want_updates = self.functions.get_userid_and_ical()
            for user in want_updates:
                gcal = None
                ical_str = ""
                user = user[0]
                old = self.functions.get_old_cal_text(user_id=user)
                old = str(old)
                url = self.functions.get_cal_link(user_id=int(user))
                url = str(url).split(",")[2].replace("'", "")
                icalfile = requests.get(url).text
                try:
                    gcal = Calendar.from_ical(icalfile)
                except ValueError:
                    user = self.bot.get_user(int(user))
                    try:
                        await user.send("You disabled your ical link. if you didn't contact Yousef#9999")
                    except:
                        pass
                    self.functions.force_ical_updates_off(user_id=int(user.id))
                    print(f"forced {user}'s thing off")
                    continue
                if old.startswith("("):
                    old = old[1:]
                if old.endswith(",)"):
                    old = old[:-2]
                if old == "None":
                    no_text = False
                else:
                    no_text = True
                if gcal is None:
                    continue
                for component in gcal.walk():
                    if component.name == "VEVENT":
                        summary = component.get('summary')
                        description = component.get('description')
                        location = component.get('location')
                        startdt = component.get('dtstart').dt
                        enddt = component.get('dtend').dt
                        exdate = component.get('exdate')
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
                    self.functions.update_ical_text(user_id=user, text=ical_str)
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
                                    location = component.get('location')
                                    startdt = component.get('dtstart').dt
                                    enddt = component.get('dtend').dt
                                    exdate = component.get('exdate')
                                    link = component.get('url')
                                    full_link = link
                                    link = link.replace("\n", "") if "\n" in str(link) else link
                                    link = link.replace("'", "") if "'" in str(link) else link
                                    link = str(link).split("/")[4]
                                    if link == f"{x}":
                                        description = str(description).split("- Link:")[0] if "- Link:" in str(
                                            description) else description
                                        summary = str(summary).replace("\n", "") if "\n" in str(summary) else summary
                                        summary = str(summary).replace("'", "") if "'" in str(summary) else summary
                                        dm_user = self.bot.get_user(int(user))
                                        embed = self.functions.dm_user_embed(title=f"{summary}",
                                                                             desc=f"{description}\n\nLink: {full_link}",
                                                                             footer=f"Due date: {enddt}")
                                        try:
                                            message = await dm_user.send(f"{dm_user.mention}")
                                            try:
                                                await message.edit(embed=embed)
                                            except Exception as e:
                                                await dm_user.send(embed=embed) # this also wasnt tested but it catches errors
                                        finally:
                                            continue
                        self.functions.update_ical_text(user_id=user, text=ical_str)
                        continue
                    else:
                        continue

    @check_assignments.error
    async def check_assigements_error(self, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            pass


def setup(bot):
    bot.add_cog(Cal(bot))
