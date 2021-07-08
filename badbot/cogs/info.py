from discord.ext import commands
from discord import Embed
import random
from datetime import date
import aiohttp
import flag

def avatar_url(userid):
    return f"https://tetr.io/user-content/avatars/{userid}.jpg"

def create_info_embed(js):
    user = js["data"]["user"]
    league = user['league']
    e = Embed(title=user["username"], url=f"https://ch.tetr.io/u/{user['username']}")
    e.set_thumbnail(url=avatar_url(user["_id"]))
    e.add_field(name="Tetra league", value=f"{league['rating']:.2f} TR 🌎 {league['standing']} / {flag.flag(user['country'])} {league['standing_local']}")
    e.add_field(name="PPS", value=f"{league['pps']:.2f}")
    e.add_field(name="APM", value=f"{league['apm']:.2f}")
    e.add_field(name="VS", value=f"{league['vs']:.2f}")
    e.add_field(name="GPM", value=f"{league['vs']*.6-league['apm']:.2f}")
    return e


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["stats"])
    async def info(self, ctx, tetrioname = None):
        """Generates a random fortune for the day.
        """
        target = tetrioname or ctx.author.nick
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ch.tetr.io/api/users/{target}") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = create_info_embed(js)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Something bad happened :( (HTTP status {r.status}")
                    
def setup(bot):
    bot.add_cog(Info(bot))
