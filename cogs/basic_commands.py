import discord
import json
from discord.ext import commands
from define_stuff import Funcs  # custom import from define_stuff.py its very much needed across all of the bot.
from blacklist_functions import Blacklist


with open("./config.json") as f:
    config = json.load(f)

try:
    bot_owner = int(config['bot_owner_id'])
except Exception as e:
    print(f"Error! {e} (could be caused by an invalid config, or if you didn't put the DISCORD ID) (basic_commands.py)")

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.functions = Funcs()
        self.blacklist = Blacklist()

    # BOT_CHECK IS GLOBAL BLACKLISTING

    async def bot_check(self, ctx):
        if ctx.message.author.id == bot_owner: # bypass blacklists.
            return True
        elif self.blacklist.is_user_blacklisted(ctx.message.author.id) is True:
            em = self.functions.error_embed(title=f"Error!", error=f"You're blacklisted!")
            await ctx.send(embed=em, delete_after=5)
            return False
        else:
            return True


    @commands.command()
    async def help(self, ctx):  # Custom help command no.
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            embed = discord.Embed(title=f"{self.bot.user.name} Help!", url="https://discord.gg/s4g9RwzZkT",
                                  description="This bot was made to help students keep track assignments this is a VERY vague outline on the commands we currently have on this bot.",
                                  color=self.functions.get_guild_color(ctx.guild.id))
        if isinstance(ctx.channel, discord.channel.DMChannel):
            embed = discord.Embed(title=f"{self.bot.user.name} Help!", url="https://discord.gg/s4g9RwzZkT",
                                  description="This bot was made to help students keep track assignments this is a VERY vague outline on the commands we currently have on this bot.",
                                  color=0x00fbff)
        embed.add_field(name=f"{ctx.prefix}Setup",
                        value=f"This command allows you (the user) to set up some of the core functions of the bot.",
                        inline=False)
        embed.add_field(name=f"{ctx.prefix}Remind <time> <date> <reminder>",
                        value=f"Allows you to set a reminder to expire on a certain time/day\nExample: {ctx.prefix}remind 10:43pm 6/2/21 Example",
                        inline=False)
        embed.add_field(name=f"{ctx.prefix}Remindlog",
                        value="Shows you your reminders, as well as tells you if they're expired or not.", inline=False)
        embed.add_field(name=f"{ctx.prefix}calendar",
                        value="Shows you your calender", inline=False)
        embed.add_field(name=f"{ctx.prefix}Guildsetup",
                        value=f"Sets up the current guild with some cool features such as setting the embed color.",
                        inline=False)
        embed.set_footer(
            text=f"Help requested by {ctx.message.author.name}. Join the support server if you encounter any problems.")
        msg = await ctx.send(embed=embed)

    @commands.command()
    async def blacklist(self, ctx, user_id, *, reason=None):
        if ctx.message.author.id == bot_owner: # only bot owner can blacklist.
            if reason is None:
                reason = "No reason provided."
            if "<@!" in str(user_id) or "<@" in str(user_id):
                user_id = str(user_id).replace("<@!", "")
                user_id = str(user_id).replace("<@", "")
            if ">" in str(user_id):
                user_id = str(user_id).replace(">", "")
            check_if_blacklist = self.blacklist.is_user_blacklisted(user_id=user_id)
            if check_if_blacklist is True:
                await ctx.send(f"<@{user_id}> is already blacklisted.")
            elif check_if_blacklist is False:
                self.blacklist.insert_blacklist(user_id=user_id, punishier_id=ctx.message.author.id, reason=reason)
                await ctx.send(f"<@{user_id}> is now blacklisted with the reason:\n\n{reason}")
                user = self.bot.get_user(int(user_id))
                try:
                    embed = discord.Embed(title=f"You are now blacklisted!",
                                          description=f"You were blacklisted by {ctx.message.author.mention} with the reason:\n\n{reason}",
                                          color=0xd60000)
                    embed.set_footer(
                        text=f"If you think this was a mistake you may appeal it in a support ticket at: https://discord.gg/s4g9RwzZkT")
                    await user.send(embed=embed)
                except:
                    pass
                channel = self.bot.get_channel(id=config['black_list_log_id'])
                em = discord.Embed(title=f"User Blacklisted!",
                                   description=f"{user.mention} was blacklisted by {ctx.message.author.mention}\nUser ID: {user.id}\nReason: {reason}",
                                   color=0xd60000)
                await channel.send(embed=em)
        else:
            return

    @commands.command()
    async def unblacklist(self, ctx, user_id):
        if ctx.message.author.id == bot_owner: # only bot owner can unblacklist.
            if "<@!" in str(user_id) or "<@" in str(user_id):
                user_id = str(user_id).replace("<@!", "")
                user_id = str(user_id).replace("<@", "")
            if ">" in str(user_id):
                user_id = str(user_id).replace(">", "")
            check_if_blacklist = self.blacklist.is_user_blacklisted(user_id=user_id)
            user = self.bot.get_user(int(user_id))
            if check_if_blacklist is True:
                self.blacklist.unblacklist_user(user_id=user_id)
                await ctx.send(f"<@{user_id}> is no longer blacklisted")
                try:
                    embed = discord.Embed(title=f"You are no longer blacklisted!",
                                          description=f"{ctx.message.author.mention} has unblacklisted you from using {self.bot.user.mention}\n\nTry not to abuse our bot to avoid being blacklisted again, as we're now keeping an eye on you",
                                          color=0x2eb82e)
                    embed.set_footer(text="https://discord.gg/s4g9RwzZkT")
                    await user.send(embed=embed)
                except Exception as E:
                    pass
                channel = self.bot.get_channel(id=config['black_list_log_id'])
                em = discord.Embed(title=f"User Unblacklisted!",
                                   description=f"{user.mention} was unblacklisted by {ctx.message.author.mention}\nUser ID: {user.id}",
                                   color=0x2eb82e)
                await channel.send(embed=em)
            elif check_if_blacklist is False:
                await ctx.send(f"{user_id} isn't blacklisted..")
        else:
            return

    @commands.command()
    async def checkblacklist(self, ctx, user_id):
        if ctx.message.author.id == bot_owner: # only bot owner can check blacklists.
            if "<@!" in str(user_id) or "<@" in str(user_id):
                user_id = str(user_id).replace("<@!", "")
                user_id = str(user_id).replace("<@", "")
            if ">" in str(user_id):
                user_id = str(user_id).replace(">", "")
            check_if_blacklist = self.blacklist.is_user_blacklisted(user_id=user_id)
            if check_if_blacklist is True:
                await ctx.send(f"I have dmed you info regarding {user_id}'s ban")
                requester = self.bot.get_user(ctx.message.author.id)
                info = self.blacklist.get_blacklist_info(user_id=user_id)
                ban_id = info[0]
                punisher = info[1]
                user_id = info[2]
                reason = info[3]
                try:
                    punisher_mention = self.bot.get_user(int(punisher))
                    user = self.bot.get_user(int(user_id))
                    embed = discord.Embed(title=f"INFO ON {user} ({user.id})'s BLACKLIST",
                                          description=f"Here is the info you requested:\n\nBan ID: {ban_id}\nPunisher ID + Mention: {punisher} / {punisher_mention.mention}\nReason: {reason}",
                                          color=0x00d4f0)
                    await requester.send(embed=embed)
                except:
                    pass
            elif check_if_blacklist is False:
                await ctx.send(f"{user_id} is not blacklisted.")
        else:
            return


def setup(bot):
    bot.add_cog(Commands(bot))
