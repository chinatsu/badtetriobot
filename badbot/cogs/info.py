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

DATEFORMAT = "%Y-%m-%d / %H:%M UTC +9"

def to_korean_time(ts):
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    tz = pytz.timezone('Asia/Seoul')
    return dt.astimezone(tz)


def avatar_url(userid):
    return f"https://tetr.io/user-content/avatars/{userid}.jpg"

def create_info_embed(js):
    user = js["data"]["user"]
    league = user['league']
    reg_date = to_korean_time(user["ts"]).strftime(DATEFORMAT)
    ts = int(datetime.now().timestamp())
    country = ""
    if user['country']:
        country = f"{flag.flag(user['country'])} "
    e = Embed(title=f"{country}{user['username'].upper()}", url=f"https://ch.tetr.io/u/{user['username']}")
    e.set_thumbnail(url=f"{avatar_url(user['_id'])}?ts={ts}")
    pps = league["pps"]
    apm = league["apm"]
    vs = league["vs"]
    gpm = vs*.6-apm
    app = apm/pps/60
    atkp = apm/.6/vs*100
    league_info = f"{rank_to_emoji(league['rank'])} {league['rating']:.2f} TR"
    if league['standing'] == -1:
        pass
    elif user["country"]:
        league_info += f"\n🌏 {league['standing']} / {flag.flag(user['country'])} {league['standing_local']}"
    else:
        league_info += f"\n🌏 {league['standing']}"
    e.add_field(name="테트라 리그", value=league_info, inline=False)
    e.add_field(name="스탯", value=f"**PPS** {pps:.2f}\n**APM** {apm:.2f} ({atkp:.2f}%)\n**VS** {vs:.2f}\n**GPM** {gpm:.2f}\n**APP** {app:.2f}", inline=True)
    e.set_footer(text=f"시작한 날 {reg_date}")
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
        e.add_field(name="기록", value="\n".join(solo_records), inline=True)
    return e

def username(ctx, tetrioname = ""):
    target = tetrioname or ctx.author.nick
    target = "".join([x.lower() for x in target if x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890-_'])
    return target

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["stats", "정보"])
    async def info(self, ctx, tetrioname = None):
        """Shows info for a specified TETR.IO user.
        If no TETR.IO username is provided, it will try to use your nickname as TETR.IO username.
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
            result += "- 게임 기록 없음"
        else:
            length = len(max([game["endcontext"][0]['user']['username'] for game in data] + [game["endcontext"][1]['user']['username'] for game in data], key=len))
            total_length = length + len(target) + 3
            result = "**" + target.upper() + "의 최근 " + str(len(data)) + " 게임 결과**\n"
            result += "```diff\n"
            result += f"  {'결과': <{total_length}}　　　APM     GPM     PPS    APP    공격비율　　　시각\n"
            for game in data:
                end = game['endcontext']
                user = 0 if (end[0]['user']['username'] == target.lower()) else 1
                stats = end[user]["points"]
                apm = stats["secondary"]
                pps = stats["tertiary"]
                vs = stats["extra"]["vs"]
                gpm = vs*.6-apm
                app = apm/pps/60 if pps else 0.0
                atkp = f"{apm/.6/vs*100:.2f}%" if vs else "0.00%"
                formatted_time = to_korean_time(game['ts']).strftime(DATEFORMAT)
                if (end[0]['user']['username'] == target.lower()):
                    result += f"+ W {end[0]['user']['username']} {end[0]['wins']} - {end[1]['wins']} {end[1]['user']['username']: <{length}} {apm:<7.2f} {gpm:<7.2f} {pps:<6.2f} {app:<6.2f} {atkp:<7}      {formatted_time}\n"
                else:
                    result += f"- L {end[1]['user']['username']} {end[1]['wins']} - {end[0]['wins']} {end[0]['user']['username']: <{length}} {apm:<7.2f} {gpm:<7.2f} {pps:<6.2f} {app:<6.2f} {atkp:<7}      {formatted_time}\n"
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

        result += f"`   {'name': <{length}} TR      ` {TRANSPARENT} {TRANSPARENT} {TRANSPARENT}`Wins          APM    PPS  GPM   APP   VS   `\n"
        for idx, user in enumerate(data):
            league = user['league']
            apm = league['apm']
            pps = league['pps']
            vs = league['vs']
            app = apm/pps/60
            gpm = vs*.6-apm
            position = idx + 1
            result += f"`{position: >2} {user['username']: <{length}} {league['rating']:.2f}` "
            result += f"{flag.flag(user['country'])} " if user['country'] != None else TRANSPARENT
            result += VERIFIED if user['verified'] else TRANSPARENT
            result += SUPPORTER if 'supporter' in user else TRANSPARENT
            result += f" `{user['league']['gameswon']}"
            result += f" ({(user['league']['gameswon'] / user['league']['gamesplayed'] * 100):.2f}%)"
            result += f"  {apm:.1f}  {pps:.1f}  {gpm:.1f}  {app:.2f}  {vs:.1f}`"
            result += f"\n"

        await ctx.send(result)

def setup(bot):
    bot.add_cog(Info(bot))
