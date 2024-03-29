from discord.ext import commands
from discord import Embed
from datetime import datetime
import os
import pytz
import json


DATEFORMAT = "%Y-%m-%d / %H:%M UTC +9"

def to_korean_time(ts):
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    tz = pytz.timezone('Asia/Seoul')
    return dt.astimezone(tz)

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


def kr_rank_to_rank(rank):
    ranks = {
        "엑스": "x",
        "유": "u",
        "에스에스": "ss",
        "에스플러스": "s+",
        "에스": "s",
        "에스마이너스": "s-",
        "에이플러스": "a+",
        "에이": "a",
        "에이마이너스": "a-",
        "비플러스": "b+",
        "비": "b",
        "비마이너스": "b-",
        "씨플러스": "c+",
        "씨": "c",
        "씨마이너스": "c-",
        "디플러스": "d+",
        "디": "d",
        "디마이너스": "d-"
    }
    try:
        return ranks[rank]
    except:
        return rank

def ranks_to_embed(ranks):
    updated = datetime.strptime(ranks["date"], "%Y-%m-%d %H:%M:%S UTC").astimezone(pytz.timezone('Asia/Seoul')).strftime(DATEFORMAT)
    e = Embed(title=f"랭크 등급컷")
    e.set_footer(text=f"마지막 업데이트 {updated}")
    description = []
    for rank in ranks["thresholds"]:
        emoji = rank_to_emoji(rank["rank"])
        description.append(f"{emoji} **{rank['threshold']:.2f}TR** ({rank['percentage']}% / {rank['playerCount']} 유저)")
    e.description = "\n".join(description)
    return e

class Ranks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delimiters = [" 와 ", " 과 ", " 또 ", " 그리고 ", " 랑 ", " and ", " | ", "; ", ", ", ",", ";", "와", "과", "또", "그리고", "랑",  "|"]

    def split_choices(self, msg):
        for delimiter in self.delimiters:
            msg = "|".join(msg.split(delimiter))
        return msg.split("|")

    @commands.command(name="ranks", aliases=["rank", "랭크컷", "랭크"])
    async def ranks(self, ctx, * rank):
        """Shows info of TR requirements for each rank. Specify a rank to only show that.
        Example: ?랭크 x 와 u"""
        if os.path.exists("badbot/scripts/thresholds.json"):
            with open("badbot/scripts/thresholds.json", 'r') as f:
                data = json.load(f)
                if len(rank) > 0:
                    targets = []
                    target_ranks = [kr_rank_to_rank(x) for x in self.split_choices("|".join(rank).lower())]
                    for rank in data['thresholds']:
                        if rank['rank'] in target_ranks:
                            targets.append(rank)
                    data["thresholds"] = targets
            await ctx.send(embed=ranks_to_embed(data))
        else:
            await ctx.send("Rank data hasn't been received yet :(")


def setup(bot):
    bot.add_cog(Ranks(bot))
