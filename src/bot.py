import discord
import asyncio

from courses import Course
from datetime import datetime

from token_fetcher import get_token
token = get_token()

from discord.ext import commands
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

def fetch_course(crn: str) -> str:
    season = "spring"
    now = datetime.now()
    term = ''

    if season.lower() == 'spring':
        term = f'{now.year + 1}' + '02' if now.month > 4 else f'{now.year}' + '02'
    else:
        term = f'{now.year}' + '05' if season.lower() == 'summer' else f'{now.year}' + '08'
    course = Course(crn, term)
    return str(course)

@bot.command()
async def info(ctx, crn):
    await ctx.send(fetch_course(crn))

bot.run(token)