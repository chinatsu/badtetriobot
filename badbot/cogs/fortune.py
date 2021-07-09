from discord.ext import commands
import random
from datetime import datetime
from pytz import timezone

fortunes = ["아주 좋아요! 🥳", "좋아요 😀", "꽤 괜찮아요 🙂", "그럭저럭.. 😐", "조금 안좋네요.. 🙁", "미스드랍이 심할 예정이예요.. 😧", "똥이예요 💩"]

class Fortune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_seed(self, user_id):
        return datetime.now(timezone('Asia/Seoul')).date().toordinal() + user_id

    @commands.command(name="fortune", aliases=["f", "운세", "에프"])
    async def fortune(self, ctx):
        """오늘의 운세를 확인해보세요
        """
        member = ctx.author
        seed = self.get_seed(member.id)
        random.seed(seed)
        fortune = random.choice(fortunes)
        await ctx.send(f"오늘의 운세: **{fortune}**")


def setup(bot):
    bot.add_cog(Fortune(bot))
