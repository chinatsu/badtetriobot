from discord.ext import commands
from discord import Embed
import aiohttp
import flag
from datetime import datetime
import pytz

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
        "z": "<:unranked:845092197346443284>",
    }
    return ranks[rank]

TRANSPARENT = "<:transparent:881270184822857808>"
SUPPORTER = "<:supporter:881270138740031528>"
VERIFIED = "<:verified:881270163599687762>"

def to_korean_time(ts):
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    tz = pytz.timezone('Asia/Seoul')
    return dt.astimezone(tz)


def avatar_url(userid):
    return f"https://tetr.io/user-content/avatars/{userid}.jpg"

def create_info_embed(js):
    user = js["data"]["user"]
    league = user['league']
    country = ""
    if user['country']:
        country = f"{flag.flag(user['country'])} "
    e = Embed(title=f"{country}{user['username'].upper()}", url=f"https://ch.tetr.io/u/{user['username']}")
    e.set_thumbnail(url=avatar_url(user["_id"]))
    pps = league["pps"]
    apm = league["apm"]
    vs = league["vs"]
    gpm = vs*.6-apm
    league_info = f"{rank_to_emoji(league['rank'])} {league['rating']:.2f} TR"
    if league['standing'] == -1:
        pass
    elif user["country"]:
        league_info += f"\n🌏 {league['standing']} / {flag.flag(user['country'])} {league['standing_local']}"
    else:
        league_info += f"\n🌏 {league['standing']}"
    e.add_field(name="Tetra league", value=league_info, inline=False)
    e.add_field(name="Stats", value=f"**PPS** {pps:.2f}\n**APM** {apm:.2f}\n**VS** {vs:.2f}\n**GPM** {gpm:.2f}", inline=True)
    return e

def add_records(e, js):
    solo_records = []
    if "data" in js and "records" in js["data"]:
        records = js["data"]["records"]
        if records["40l"]["record"]:
            sprint_record = records["40l"]["record"]["endcontext"]["finalTime"]/1000
            solo_records.append(f"**Sprint (40L)** {sprint_record:.3f}s")
        if records["blitz"]["record"]:
            blitz_record = records["blitz"]["record"]["endcontext"]["score"]
            solo_records.append(f"**Blitz** {blitz_record}")
    if len(solo_records) > 0:
        e.add_field(name="Solo Records", value="\n".join(solo_records), inline=True)
    return e

def username(ctx, tetrioname = None):
    target = tetrioname or ctx.author.nick
    target = "".join([x.lower() for x in target if x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890-_'])
    return target

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["stats", "정보"])
    async def info(self, ctx, tetrioname = None):
        """Shows info for a specified TETR.IO user.
        If no TETR.IO username is provided, it will try to use the calling user's nickname as TETR.IO username
        """
        target = username(ctx, tetrioname)
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


    @commands.command(name="match")
    async def match(self, ctx, tetrioname = None):
        """Shows the 10 last played TETRA LEAGUE matches for a specified TETR.IO user.
        If no TETR.IO username is provided, it will try to use the calling user's nickname as TETR.IO username
        """
        target = username(ctx, tetrioname)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ch.tetr.io/api/users/{target.lower()}') as r:
                if r.status == 200:
                    js = await r.json()
                    userid = js['data']['user']['_id']
                else:
                    await ctx.send(f"Something bad happened :( (HTTP status {r.status}")
                    return
            async with session.get(f"https://ch.tetr.io/api/streams/league_userrecent_{userid}") as r:
                if r.status == 200:
                    js = await r.json()
                    data = js['data']['records']
                else:
                    await ctx.send(f"Something bad happened :( (HTTP status {r.status}")
                    return

        result = "```diff\n"

        if (len(data) == 0):
            result += "- No match records"
        else:
            length = len(max([game["endcontext"][0]['user']['username'] for game in data] + [game["endcontext"][1]['user']['username'] for game in data], key=len))
            result = "**" + target.upper() + "'s last " + str(len(data)) + " match results**\n"
            result += "```diff\n"
            for game in data:
                end = game['endcontext']
                formatted_time = to_korean_time(game['ts']).strftime("%Y-%m-%d / %H:%M:%S")
                if (end[0]['user']['username'] == target.lower()):
                    result += f"+ W {end[0]['user']['username']}   {end[0]['wins']} - {end[1]['wins']}   {end[1]['user']['username']: <{length}} {formatted_time} KST/UTC +9\n"
                else:
                    result += f"- L {end[1]['user']['username']}   {end[1]['wins']} - {end[0]['wins']}   {end[0]['user']['username']: <{length}} {formatted_time} KST/UTC +9\n"
        result += "```"
        await ctx.send(result)


    @commands.command(name="top10")
    async def top10(self, ctx):
        """Shows the current top 10 players from TETRA LEAGUE
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://ch.tetr.io/api/users/lists/league") as r:
                js = await r.json()
                data = js['data']['users']

        data = data[:10]
        length = len(max((user['username'] for user in data), key=len))

        result = f"**TETR.IO Top 10 Leaderboard**\n"
        result += f"`   {'name': <{length}} TR      ` {TRANSPARENT} {TRANSPARENT} {TRANSPARENT}`Wins          APM    PPS  VS   `\n"
        for idx, user in enumerate(data):
            league = user['league']
            position = idx + 1
            result += f"`{position: >2} {user['username']: <{length}} {league['rating']:.2f}` "
            result += f"{flag.flag(user['country'])} " if user['country'] != None else TRANSPARENT
            result += VERIFIED if user['verified'] else TRANSPARENT
            result += SUPPORTER if 'supporter' in user else TRANSPARENT
            result += f" `{user['league']['gameswon']}"
            result += f" ({(user['league']['gameswon'] / user['league']['gamesplayed'] * 100):.2f}%)"
            result += f"  {user['league']['apm']:.1f}  {user['league']['pps']:.1f}  {user['league']['vs']:.1f}`"
            result += f"\n"

        await ctx.send(result)

def setup(bot):
    bot.add_cog(Info(bot))
