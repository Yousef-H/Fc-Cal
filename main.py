import discord
import json
import sqlite3
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from define_stuff import Funcs


intents = discord.Intents.default()
intents.members = True

with open("./config.json") as configfile:
    config = json.load(configfile)
    bot_owner = int(config.get('bot_owner_id'))


def insert_guild_id(guild_id):
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


def get_guild_prefix(g_id):  # per guild prefix
    db = sqlite3.connect('bot_db.sqlite')
    cursor = db.cursor()
    sql = f"SELECT prefix FROM guild_settings WHERE guild_id = {g_id}"
    cursor.execute(f"{sql}")
    result = cursor.fetchone()
    if result is None:
        insert_guild_id(g_id)
        return "."
    else:
        return str(result[0])


def get_prefix(bot, message):
    if not isinstance(message.channel, discord.channel.DMChannel):
        return when_mentioned_or(get_guild_prefix(message.guild.id))(bot, message)
    else:
        return when_mentioned_or(".")(bot, message)


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')
# These are the extensions in the ./cogs folder. I don't recommend removing any if you want the whole bot to work as it did before I released code..
cogs = [
    'cogs.reminder',
    'cogs.cal',
    'cogs.user_guild_setup',
    'cogs.changelog',
    'cogs.basic_commands',
    'cogs.before_after_class']

print(f"Discord.py version installed {discord.__version__}\n")

@bot.event
async def on_ready():
    for mod in cogs:
        try:
            bot.load_extension(mod)
        except commands.ExtensionNotFound:
            print(f"Could not find module {mod}")
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            pass
    await bot.change_presence(status=discord.Status.do_not_disturb,
                              activity=discord.Activity(type=discord.ActivityType.watching, name="Bug fixes maybe?"))
    print(f"Logged in as {bot.user}")
    db = sqlite3.connect('bot_db.sqlite')
    cursor = db.cursor()
    commands_ = ('''
        CREATE TABLE IF NOT EXISTS reminders(
        reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        channel_id TEXT,
        date TEXT,
        reminder TEXT,
        valid INTEGER
        )
    ''', '''
        CREATE TABLE IF NOT EXISTS blacklist(
        blacklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        punisher_user_id TEXT,
        blacklisted_user_id TEXT,
        reason TEXT,
        valid INT
        )
        ''','''
        CREATE TABLE IF NOT EXISTS user_settings(
        custom_user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_user_id TEXT,
        ical_link TEXT,
        assignment_announce INT,
        old_text TEXT

        )
    ''', '''
        CREATE TABLE IF NOT EXISTS guild_settings(
            guild_id INTEGER PRIMARY KEY,
            prefix TEXT DEFAULT ".",
            guild_embed_color TEXT DEFAULT "cyan",
            middle_school_noti INT,
            high_school_noti INT,
            middle_school_channel TEXT,
            high_school_channel TEXT,
            done_setup INT,
            class_mention_role_id TEXT
            
        )
    ''')
    for cmd in commands_:
        cursor.execute(cmd)
    cursor.close()
    db.commit()
    db.close()


@bot.command()
async def status(ctx, *, status_=None):
    if ctx.message.author.id == bot_owner:
        if status_ is None:
            await ctx.send(f"Invaild useage of the command! {ctx.prefix}status <status>")
        else:
            await bot.change_presence(status=discord.Status.do_not_disturb,
                                      activity=discord.Activity(type=discord.ActivityType.watching,
                                                                name=f"{status_}"))
            await ctx.send(f"Don't tell anyone but I changed the status to {status_}")

@bot.command()
async def reload(ctx, cog):
    if ctx.message.author.id == bot_owner:
        if cog == "*" or cog == "all":
            for mod in cogs:
                try:
                    bot.unload_extension(mod)
                except Exception as e:
                    await ctx.send(f"Error while unloading cog ({mod})! {e}")
            msg = await ctx.send(f"All cogs have been unloaded...")
            for mod in cogs:
                try:
                    bot.load_extension(mod)
                except Exception as e:
                    await ctx.send(f"Error while loading cog ({mod})! {e}")
            await msg.edit(content=f"All cogs have been loaded")
        else:
            if not str(cog).startswith("cogs."):
                cog = f"cogs.{cog}"
            msg = await ctx.send(f"Attempting to reload {cog}")
            try:
                if cog in cogs:
                    bot.unload_extension(cog)
                    bot.load_extension(cog)
                    await msg.edit(content=f"Loaded {cog}")
                else:
                    await ctx.send(f"That is not a valid extension!\nValid options are:\n{cogs}")
            except Exception as e:
                await ctx.send(f"Error while loading cog ({cog})! {e}")
                await msg.edit(content=f"An error occurred")

@bot.command()
async def load(ctx, cog):
    if ctx.message.author.id == bot_owner:
        if cog == "*" or cog == "all":
            msg = await ctx.send("Attempting to load all cogs...")
            for mod in cogs:
                try:
                    bot.load_extension(mod)
                except Exception as e:
                    await ctx.send(f"Error while loading cog ({mod})! {e}")
            await msg.edit(content=f"Loaded all cogs")
        else:
            if not str(cog).startswith("cogs."):
                cog = f"cogs.{cog}"
            msg = await ctx.send(f"Attempting to load {cog}...")
            try:
                if cog in cogs:
                    bot.load_extension(cog)
                else:
                    await ctx.send(f"That is not a valid extension!\nValid options are:\n{cogs}")
            except Exception as e:
                await ctx.send(f"Error while loading {cog}! {e}")
                await msg.edit(content=f"An error occurred")
            await msg.edit(content=f"Loaded {cog}")

@bot.command()
async def unload(ctx, cog):
    if ctx.message.author.id == bot_owner:
        if cog == "*" or cog == "all":
            msg = await ctx.send("Attempting to unload all cogs...")
            for mod in cogs:
                try:
                    bot.unload_extension(mod)
                except Exception as e:
                    await ctx.send(f"Error while unloading cog ({mod})! {e}")
            await msg.edit(content=f"Unloaded all cogs")
        else:
            if not str(cog).startswith("cogs."):
                cog = f"cogs.{cog}"
            msg = await ctx.send(f"Attempting to unload {cog}...")
            try:
                if cog in cogs:
                    bot.unload_extension(cog)
                else:
                    await ctx.send(f"That is not a valid extension!\nValid options are:\n{cogs}")
            except Exception as e:
                await ctx.send(f"Error while unloading {cog}! {e}")
                await msg.edit(content=f"An error occurred")
            await msg.edit(content=f"Unloaded {cog}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        return




bot.run(config['token'])
