from discord.ext import commands
import discord.utils


def is_admin():
    def is_admin_check(ctx):
        return ctx.message.author.id in [125307006260084736, 267593890377367553, 243590632180809728] # cn, 시아미즈 and SEOUL

    return commands.check(is_admin_check)

def is_owner():
    def is_owner_check(ctx):
        return ctx.message.author.id == 125307006260084736 # cn only

    return commands.check(is_owner_check)