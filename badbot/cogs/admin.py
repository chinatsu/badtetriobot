from discord.ext import commands
from .util import checks

FAIL = "\N{LOUDLY CRYING FACE}"
OK = "\N{SLIGHTLY SMILING FACE}"


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_module(self, module):
        return f"cogs.{module}"

    @commands.command(hidden=True, name="close", aliases=["quit"])
    @checks.is_admin()
    async def close(self, ctx):
        """Logs the bot off, admin only
        """
        await ctx.send("baibai~~")
        await self.bot.close()
    

    @commands.command(hidden=True, name="load_module", aliases=["load"])
    @checks.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module, owner only
        """
        try:
            self.bot.load_extension(self.format_module(module))
        except Exception as e:
            await ctx.send(FAIL)
            await ctx.send("{}: {}".format(type(e).__name__, e))
        else:
            await ctx.send(OK)

    @commands.command(hidden=True, name="unload_module", aliases=["unload"])
    @checks.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module, owner only
        """
        try:
            self.bot.unload_extension(self.format_module(module))
        except Exception as e:
            await ctx.send(FAIL)
            await ctx.send("{}: {}".format(type(e).__name__, e))
        else:
            await ctx.send(OK)

    @commands.command(name="reload_module", hidden=True, aliases=["reload"])
    @checks.is_owner()
    async def reload(self, ctx, *, module):
        """Reloads a module, owner only
        """
        try:
            self.bot.unload_extension(self.format_module(module))
            self.bot.load_extension(self.format_module(module))
        except Exception as e:
            await ctx.send(FAIL)
            await ctx.send("{}: {}".format(type(e).__name__, e))
        else:
            await ctx.send(OK)


def setup(bot):
    bot.add_cog(Admin(bot))