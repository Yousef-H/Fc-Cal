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
    #    var = config.get('value')


def get_guild_prefix(g_id):  # per guild prefix
    db = sqlite3.connect('guild_settings.sqlite')
    cursor = db.cursor()
    sql = f"SELECT prefix FROM guild_settings WHERE guild_id = {g_id}"
    cursor.execute(f"{sql}")
    result = cursor.fetchone()
    return str(result[0])


def get_prefix(bot, message):
    if not isinstance(message.channel, discord.channel.DMChannel):
        return when_mentioned_or(get_guild_prefix(message.guild.id))(bot, message)
    else:
        return when_mentioned_or(".")(bot, message)

try:
    bot_owner = int(config['bot_owner_id'])
except Exception as e:
    print(f"Error! {e} (could be caused by an invalid config, or if you didn't put the DISCORD ID)")


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')
# These are the extensions in the ./cogs folder. I don't recommend removing any if you want the whole bot to work as it did before..
cogs = [
    'cogs.reminder',
    'cogs.cal',
    'cogs.user_guild_setup',
    'cogs.basic_commands',
    'cogs.before_after_class']

print(f"discord.py version installed: {discord.__version__}\nAttempting to load cogs...\n")

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
                              activity=discord.Activity(type=discord.ActivityType.watching, name="people's calenders"))
    print(f"Logged in as {bot.user}")
    try:
        await bot.wait_until_ready()
        if str(config['beta']).lower() == "true":
            print("Beta mode enabled")
            want_updates = Funcs.get_userid_and_ical()
            for user in want_updates:
                user = user[0]
                user_name = bot.get_user(user)
                Funcs.set_users_as_beta(user_id=user)
                print(f"Using beta I turned {user_name}'s ICAL due to beta! (Discord ID:{user})") #will say nontype since users arent in the cache
        elif str(config['beta']).lower() == "false":
            print("Production mode enabled")
        else:
            print("Production mode enabled - invalid argument in config")
    except KeyError:
        print("Production mode enabled - not specified in the config.")
    db = sqlite3.connect('reminders.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders(
        reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        channel_id TEXT,
        date TEXT,
        reminder TEXT,
        valid INTEGER
        )
    ''')
    cursor.close()
    db.commit()
    db.close()
    blacklist = sqlite3.connect('blacklist.sqlite')
    cursor2 = blacklist.cursor()
    cursor2.execute('''
        CREATE TABLE IF NOT EXISTS blacklist(
        blacklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        punisher_user_id TEXT,
        blacklisted_user_id TEXT,
        reason TEXT,
        valid INT
        )
        ''')
    cursor2.close()
    blacklist.commit()
    blacklist.close()
    user_settings = sqlite3.connect('user_settings.sqlite')
    cursor3 = user_settings.cursor()
    cursor3.execute('''
        CREATE TABLE IF NOT EXISTS user_settings(
        custom_user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_user_id TEXT,
        ical_link TEXT,
        assignment_announce INT,
        old_text TEXT

        )
    ''')
    cursor3.close()
    user_settings.commit()
    user_settings.close()
    guild_settings = sqlite3.connect('guild_settings.sqlite')
    cursor4 = guild_settings.cursor()
    cursor4.execute('''
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
    user_to_do = sqlite3.connect('user_to_do.sqlite')  # this is for a planned update but I never got around to creating it before i released the source.
    cursor5 = user_to_do.cursor()
    cursor5.execute('''
        CREATE TABLE IF NOT EXISTS user_to_do(
        user_id INTEGER PRIMARY KEY,
        to_do1 TEXT
        )
    ''')


@bot.command()
async def status(ctx, *, status=None):
    if ctx.message.author.id == bot_owner:
        if status is None:
            await ctx.send(f"Invaild useage of the command! {ctx.prefix}status <status>")
        else:
            await bot.change_presence(status=discord.Status.do_not_disturb,
                                      activity=discord.Activity(type=discord.ActivityType.watching,
                                                                name=f"{status}"))
            await ctx.send(f"Don't tell anyone but I changed the status to {status}")


@bot.command()
async def unbeta(ctx, user_id=None):
    if ctx.message.author.id == bot_owner:
        user_id = ctx.message.author.id if user_id is None else user_id
        if user_id == "*":
            want_updates = Funcs.get_beta_userid_and_ical()
            for user in want_updates:
                user = user[0]
                user_name = bot.get_user(user)
                Funcs.set_users_as_normal(user_id=user)
                print(f"{user_name}'s auto announce has been enabled ({user_id})")
        else:
            try:
                Funcs.set_users_as_normal(user_id=user_id)
                user_name = bot.get_user(user_id)
                print(f"{user_name}'s auto announce has been enabled ({user_id})")
                await ctx.send("Done!")
            except Exception as e:
                await ctx.send(f"Error! {e}")



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

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Bot Info", description="Hey! I am a bot that was made to help students keep track of work.\nYou can find my original creator at https://discord.gg/eQCAV3jF\nGitHub:\nOriginal author discord id: 292848897632632835", color=discord.colour.Color.purple())
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound): 
        return




bot.run(config['token'])
