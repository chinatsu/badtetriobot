from discord.ext import commands
from discord import Embed
import random
from datetime import date
import aiohttp
import flag

def rank_to_emoji(rank):
    ranks = {
        "x": "<:rankX:845092185052413952>",
        "u": "<:rankU:845092171438882866>",
        "ss": "<:rankSS:845092157139976192>",
        "s+": "<:rankSplus:845092140471418900>",
        "s": "<:rankS:845092120662376478>",
        "s-": "<:rankSminus:845092009101230080>",
        "a+": "<:rankAplus:845091973248581672>",
        "a": "<:rankA:845091931994587166>",
        "a-": "<:rankAminus:845091885286424596>",
        "b+": "<:rankBplus:845091818911301634>",
        "b": "<:rankB:845089923089825812>",
        "b-": "<:rankBminus:845089882698154044>",
        "c+": "<:rankCplus:845088318509285416>",
        "c": "<:rankC:845088262611533844>",
        "c-": "<:rankCminus:845088252322775041>",
        "d+": "<:rankDplus:845088230588284959>",
        "d": "<:rankD:845088198966640640>",
        "d-": "<:rankDminus:845105375015600138>",
    }
    return ranks[rank]

def avatar_url(userid):
    return f"https://tetr.io/user-content/avatars/{userid}.jpg"

def create_info_embed(js):
    user = js["data"]["user"]
    league = user['league']
    country = flag.flag(user['country'])
    e = Embed(title=f"{country} {user['username'].upper()}", url=f"https://ch.tetr.io/u/{user['username']}")
    e.set_thumbnail(url=avatar_url(user["_id"]))
    pps = league["pps"]
    apm = league["apm"]
    vs = league["vs"]
    gpm = vs*.6-apm
    e.add_field(name="Tetra league", value=f"{rank_to_emoji(league['rank'])} {league['rating']:.2f} TR\n🌏 {league['standing']} / {flag.flag(user['country'])} {league['standing_local']}", inline=False)
    e.add_field(name="Stats", value=f"**PPS** {pps:.2f}\n**APM** {apm:.2f}\n**VS** {vs:.2f}\n**GPM** {gpm:.2f}", inline=True)
    return e

def add_records(e, js):
    solo_records = []
    if "data" in js and "records" in js["data"]:
        records = js["data"]["records"]
        if "40l" in records:
            sprint_record = records["40l"]["record"]["endcontext"]["finalTime"]/1000
            solo_records.append(f"**Sprint (40L)** {sprint_record:.3f}s")
        if "blitz" in records:
            blitz_record = records["blitz"]["record"]["endcontext"]["score"]
            solo_records.append(f"**Blitz** {blitz_record}")

    e.add_field(name="Solo Records", value="\n".join(solo_records), inline=True)
    return e


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["stats", "정보"])
    async def info(self, ctx, tetrioname = None):
        """Shows info for a specified TETR.IO user.
        If no TETR.IO username is provided, it will try to use the calling user's nickname as TETR.IO username
        """
        target = tetrioname or ctx.author.nick
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ch.tetr.io/api/users/{target}") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = create_info_embed(js)
                else:
                    await ctx.send(f"Something bad happened :( (HTTP status {r.status}")
                    return
            async with session.get(f"https://ch.tetr.io/api/users/{target}/records") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = add_records(embed, js)
                else:
                    await ctx.send(f"Something bad happened :( (HTTP status {r.status}")
                    return
        await ctx.send(embed=embed)
                    
def setup(bot):
    bot.add_cog(Info(bot))
