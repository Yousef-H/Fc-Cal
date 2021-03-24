import discord
import json
import asyncio
from discord.ext import commands
from define_stuff import Funcs

with open("./config.json") as f:
    config = json.load(f)


class User_guild_setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.functions = Funcs()

    @commands.command()
    async def setup(self, ctx):  # user setup requires define_stuff obv
        if isinstance(ctx.channel, discord.channel.DMChannel):
            embed = self.functions.embed_basic(title=f"Welcome to {self.bot.user.name} user setup!",
                                               desc=f"Please react with "
                                                    f"✅ within 10 "
                                                    f"seconds to confirm "
                                                    f"you're ready.\nYou "
                                                    f"may also click ❌ "
                                                    f"before the time is "
                                                    f"up to cancel early "
                                                    f"this command will "
                                                    f"set up the "
                                                    f"following"
                                                    f":\niCalender "
                                                    f"Link\nIf you want "
                                                    f"the bot to dm you "
                                                    f"when it detects a "
                                                    f"new assignment.")
            msg = await ctx.send(embed=embed)

            await msg.add_reaction("✅")
            await msg.add_reaction("❌")

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']

            try:
                await asyncio.sleep(.250)
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                if reaction.emoji == '✅':
                    def link_check(msg):
                        if "http://" in msg.content or "https://" in msg.content:
                            return msg.content
                        else:
                            msg.content = "INVALID"
                            return msg.content

                    def true_false_check(var):
                        if var.content == "1" or var.content == "0":
                            return var.content
                        elif var.content == "true":
                            var.content = "1"
                            return var.content
                        elif var.content == "false":
                            var.content = "0"
                            return var.content
                        else:
                            var.content = "INVALID"
                            return var.content

                    try:
                        await ctx.send("What is your iCalender link (can be found at https://lms.fcps.edu/settings/account) please replace 'webcal://' with 'http://'")
                        await asyncio.sleep(.250)
                        user_input = await self.bot.wait_for('message', timeout=60, check=link_check)
                        if user_input.content == "INVALID":
                            error_msg = self.functions.error_embed(title="Error!",
                                                                   error="Invalid URL! This URL is needed for a lot of the features to work, command has been cancelled because all user settings need an ICAL link")
                            await ctx.send(embed=error_msg)
                            raise asyncio.TimeoutError
                        await ctx.send(
                            f"Would you like me ({self.bot.user.name}) to notify you when I detect a new assignment? **Please Note**; You must answer with 1 being **True**, and 2 being **False**")
                        await asyncio.sleep(.250)
                        true_or_false = await self.bot.wait_for('message', timeout=60, check=true_false_check)
                        if true_or_false.content == "INVALID":
                            await ctx.send("Invalid option inputted!")
                            raise asyncio.TimeoutError
                        final_msg = await ctx.send(
                            f"Just to confirm these are the following setting you'd like to use:\nICAL Link:{user_input.content}\n{true_or_false.content} (0 is **False** and 1 is **True**) for up coming assignments")
                        await final_msg.add_reaction("✅")
                        await final_msg.add_reaction("❌")
                        await asyncio.sleep(.250)
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                        if reaction.emoji == '✅':
                            try:
                                if self.functions.check_if_user_setup_in_db(user_id=ctx.message.author.id) is False:
                                    self.functions.insert_user_setup(user_id=ctx.message.author.id,
                                                                     ical_link=user_input.content,
                                                                     assignment_announce=true_or_false.content)
                                    await ctx.send("Your settings has been updated!")
                                    return
                                else:
                                    confirm_overide = await ctx.send(
                                        "You have already completed this setup, please confirm that you want to override it.")
                                    await confirm_overide.add_reaction("✅")
                                    await confirm_overide.add_reaction("❌")
                                    try:
                                        await asyncio.sleep(.250)
                                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15,
                                                                                 check=check)
                                        if reaction.emoji == '✅':
                                            self.functions.update_user_setup(user_id=ctx.message.author.id,
                                                                             ical_link=user_input.content,
                                                                             assignment_announce=true_or_false.content)
                                            await ctx.send("Your settings has been updated!")
                                            return
                                        else:
                                            raise asyncio.TimeoutError
                                    except asyncio.TimeoutError:
                                        raise asyncio.TimeoutError

                            except Exception as e:
                                await ctx.send(f"An error has occured please open a ticket in the support server!")
                                self.functions.webhook_error(error=e, remind_id=f"N/A", user_id=ctx.message.author.id,
                                                             channel_id=f"DMS (SETUP Command)",
                                                             date=f"Check when posted", reminder=f"N/A")
                        else:
                            raise asyncio.TimeoutError

                    except asyncio.TimeoutError:
                        raise asyncio.TimeoutError

                elif reaction.emoji == '❌':
                    raise asyncio.TimeoutError

            except asyncio.TimeoutError:  # Indent error here, delete one tabulation
                await ctx.send(
                    f"Cancelled setup! You may always do `{ctx.prefix}setup` to set up "
                    f"some cool features!")
        else:
            error_msg = self.functions.error_embed(title="Invalid channel!",
                                                   error=f"This command can only be used in Direct Messages for privacy reasons!")
            await ctx.send(embed=error_msg)

    #    _____       _ _     _   _____                                           _
    #   |  __ \     (_) |   | | /  __ \                                         | |
    #   | |  \/_   _ _| | __| | | /  \/ ___  _ __ ___  _ __ ___   __ _ _ __   __| |___
    #   | | __| | | | | |/ _` | | |    / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
    #   | |_\ \ |_| | | | (_| | | \__/\ (_) | | | | | | | | | | | (_| | | | | (_| \__ \
    #    \____/\__,_|_|_|\__,_|  \____/\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/
    #  Yes this was necessary

    @commands.command()
    async def prefix(self, ctx, prefix: str = None):
        if prefix is None:
            error_msg = self.functions.error_embed(title="Invalid usage!", error=f"{ctx.prefix}prefix <prefix>")
            await ctx.send(embed=error_msg)
        else:
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                if ctx.message.author.guild_permissions.administrator:
                    if len(prefix) > 4:
                        error_msg = self.functions.error_embed(title="Invalid usage!",
                                                               error=f"Prefix limit is 4!")
                        await ctx.send(embed=error_msg)
                    else:
                        await self.functions.update_prefix(prefix=prefix, guild_id=ctx.guild.id)
                        await ctx.send(f"The prefix has been changed to {prefix}\nYou can now use {self.bot.user.mention} or {prefix} to do commands.")

                else:
                    error_msg = self.functions.error_embed(title="Invalid permissions!",
                                                           error=f"You're missing the guild permission ADMINISTRATOR.")
                    await ctx.send(embed=error_msg, delete_after=10)
            else:
                error_msg = self.functions.error_embed(title="Invalid channel!",
                                                       error=f"This command can only be used in Guilds.")
                await ctx.send(embed=error_msg)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):  # when the bot joins the guild!
        bot_entry = await guild.audit_logs(action=discord.AuditLogAction.bot_add).flatten()
        try:
            embed = discord.Embed(title=f'Hey thanks for inviting me!',
                                  description=f'Hello I am {self.bot.user.mention} my default prefix is "." but it can be changed by doing .prefix <prefix> if you encounter any problems/errors please report it to https://discord.gg/S326bXmU\n', color=0x00d4f0)
            embed.set_footer(icon_url="https://i.imgur.com/v2Bz33Z.png")
            await bot_entry[0].user.send(embed=embed)
        except Exception as e:
            pass
        await self.functions.insert_guild_id(guild.id)

    #       join_logger = self.functions.guild_join_logger(name=guild, guild_id=guild.id)

    #   @commands.Cog.listener()
    #   async def on_guild_remove(self, guild):
    #       leave_logger = self.functions.guild_leave_logger(name=guild, guild_id=guild.id)

    @commands.command()
    async def guildsetup(self, ctx):
        middle_school_channel_id = None
        high_school_channel_id = None
        color_list = ['<:red:773547060091420714>', '<:orange:773547060371914824>', '<:yellow:773547060179501139>',
                      '<:green:773547060619640882>', '<:lime:773547060682948629>', '<:blue:773547060619378748>',
                      '<:cyan:773548140557107230>', '<:purple:773547060212793375>', '<:black:773547060300873740>',
                      '<:white:773547060892139550>', '<:brown:773547060603125830>', '<:gray:773547060611383296>']
        role_id = "N/A"
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.message.author.guild_permissions.administrator:
                embed = self.functions.embed_basic(title=f"Welcome to {self.bot.user.name} guild setup!",
                                                   desc=f"Please react with "
                                                        f"✅ within 10 "
                                                        f"seconds to confirm "
                                                        f"you're ready.\nYou "
                                                        f"may also click ❌ "
                                                        f"before the time is "
                                                        f"up to cancel early "
                                                        f"this command will "
                                                        f"set up the "
                                                        f"following"
                                                        f":\nEmbed color\nClass reminders")
                msg = await ctx.send(embed=embed)

                await msg.add_reaction("✅")
                await msg.add_reaction("❌")

                def check(reaction, user):
                    return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']

                try:
                    await asyncio.sleep(.250)
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                    if reaction.emoji == '✅':
                        def embed_color_check(react, user_):
                            return user_ == ctx.message.author and str(react.emoji) in color_list

                        def check_channel(msg):
                            return msg.author == ctx.message.author and msg.content

                        try:
                            test = await ctx.send(
                                f"Select a color by reacting to this message (wait for **all** color options to show)")
                            for x in color_list:
                                await test.add_reaction(x)
                            await asyncio.sleep(.250)
                            guild_color, user_ = await self.bot.wait_for('reaction_add', timeout=15,
                                                                         check=embed_color_check)
                            guild_color = str(guild_color).split(":")[1]
                            try:
                                middle_school = await ctx.send("Would you like me to tag a role 5 minutes before "
                                                               "class starts/ends (middle school schedule)")
                                await middle_school.add_reaction("✅")
                                await middle_school.add_reaction("❌")
                                await asyncio.sleep(.250)
                                reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                                if reaction.emoji == '✅':
                                    want_middle_school = True

                                elif reaction.emoji == '❌':
                                    want_middle_school = False
                                try:
                                    high_school = await ctx.send("Would you like me to tag a role 5 minutes "
                                                                 "before class starts/ends (high school schedule)")
                                    await high_school.add_reaction("✅")
                                    await high_school.add_reaction("❌")
                                    await asyncio.sleep(.250)
                                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                                    if reaction.emoji == '✅':
                                        want_high_school = True
                                    elif reaction.emoji == '❌':
                                        want_high_school = False
                                    if want_middle_school is True:
                                        try:
                                            await ctx.send(
                                                "Either send the channel ID or tag the channel you'd lke MIDDLE school class alerts in")
                                            await asyncio.sleep(.250)
                                            msg, user__ = await self.bot.wait_for('message', timeout=30, check=check_channel)
                                            middle_school_channel_id = msg.content
                                        except asyncio.TimeoutError:
                                            raise asyncio.TimeoutError
                                    if want_high_school is True:
                                        try:
                                            await ctx.send(
                                                "Either send the channel ID or tag the channel you'd lke HIGH school class alerts in")
                                            await asyncio.sleep(.250)
                                            msg = await self.bot.wait_for('message', timeout=30, check=check_channel)
                                            high_school_channel_id = msg.content
                                        except asyncio.TimeoutError:
                                            raise asyncio.TimeoutError
                                    if want_high_school is True or want_middle_school is True:
                                        try:
                                            await ctx.send(
                                                "Please send the role ID or mention the role (not recommended if people have the role) to be mentioned for class alerts. you can say 'default' for `@everyone`")
                                            await asyncio.sleep(.250)
                                            msg = await self.bot.wait_for('message', timeout=30, check=check_channel)
                                            if str(msg.content).lower == "default":
                                                role_id = "default"
                                            else:
                                                role_id = msg.content
                                        except asyncio.TimeoutError:
                                            raise asyncio.TimeoutError
                                    try:
                                        print("asd")
                                        final_msg = await ctx.send(
                                            f"Just to confirm these are the following setting you'd like to use:\nColor:{guild_color}\nMiddle school channel: {want_middle_school} (true false), {middle_school_channel_id} < channel id if true (will say None if not selected.)\nHigh School: {want_high_school} (true false) {high_school_channel_id} < channel id if true (will say None if not selected.)\nRole ID: {role_id} (default = `@everyone`)")
                                        await final_msg.add_reaction("✅")
                                        await final_msg.add_reaction("❌")
                                        await asyncio.sleep(.250)
                                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15,
                                                                                 check=check)
                                        if reaction.emoji == '✅':
                                            if self.functions.check_guild_settings(guild_id=ctx.guild.id) is False:
                                                self.functions.insert_guild_settings(guild_id=ctx.guild.id,
                                                                                     guild_color=guild_color,
                                                                                     want_middle_school=want_middle_school,
                                                                                     want_high_school=want_high_school,
                                                                                     middle_school_channel_id=middle_school_channel_id,
                                                                                     high_school_channel_id=high_school_channel_id,
                                                                                     role_id=role_id)
                                                await ctx.send(
                                                    f"Your guild settings has been updated!\nTo change the prefix use {ctx.prefix}prefix <prefix>")
                                            elif self.functions.check_guild_settings(guild_id=ctx.guild.id) is True:
                                                confirm_msg = await ctx.send(
                                                    "You have already completed this setup, please confirm that you'd like to override it.")
                                                await confirm_msg.add_reaction("✅")
                                                await confirm_msg.add_reaction("❌")
                                                await asyncio.sleep(.250)
                                                reaction, user = await self.bot.wait_for('reaction_add', timeout=15,
                                                                                         check=check)
                                                if reaction.emoji == '✅':
                                                    self.functions.insert_guild_settings(guild_id=ctx.guild.id,
                                                                                         guild_color=guild_color,
                                                                                         want_middle_school=want_middle_school,
                                                                                         want_high_school=want_high_school,
                                                                                         middle_school_channel_id=middle_school_channel_id,
                                                                                         high_school_channel_id=high_school_channel_id,
                                                                                         role_id=role_id)
                                                    await ctx.send(
                                                        f"Your guild settings has been updated!\nTo change the prefix use {ctx.prefix}prefix <prefix>")
                                                else:
                                                    raise asyncio.TimeoutError
                                        else:
                                            raise asyncio.TimeoutError

                                    except asyncio.TimeoutError:
                                        raise asyncio.TimeoutError

                                except asyncio.TimeoutError:
                                    raise asyncio.TimeoutError

                            except asyncio.TimeoutError:
                                raise asyncio.TimeoutError

                        except asyncio.TimeoutError:
                            raise asyncio.TimeoutError

                    elif reaction.emoji == '❌':
                        raise asyncio.TimeoutError

                except asyncio.TimeoutError:  # Indent error here, delete one tabulation
                    await ctx.send(
                        f"Cancelled setup! You may always do `{ctx.prefix}guildsetup` to set up "
                        f"some cool features!")
            else:
                error_msg = self.functions.error_embed(title="Invalid permissions!",
                                                       error=f"You're missing the guild permission ADMINISTRATOR.")
                await ctx.send(embed=error_msg, delete_after=10)
        else:
            error_msg = self.functions.error_embed(title="Invalid channel!",
                                                   error=f"This command can only be used in guilds.")
            await ctx.send(embed=error_msg)


#  @commands.Cog.listener()
#  async def on_reaction_add(self,reaction, user):
#      print(f"{reaction}, {user}")


def setup(bot):
    bot.add_cog(User_guild_setup(bot))
