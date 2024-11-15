import discord
import asyncio

from courses import Course
from datetime import datetime

from tracking import TrackRequest, TrackList

from token_fetcher import get_token
from loader import load_request_list, save_request_list

from discord.ext import commands
from discord.ext import tasks

token = get_token()
global_request_list = load_request_list()

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.command()
async def info(ctx: commands.Context, *crns):
    course_info: list[str] = [str(Course(crn, "202502")) for crn in crns]
    await ctx.send('\n'.join(course_info))

@bot.command()
async def track(ctx: commands.Context, crn: str):
    if ctx.guild is None:
        await ctx.reply("Error: Can only call $track from a channel in a server")
    else:
        for request in global_request_list.trackRequests:
            if request.crn == crn and request.userId == ctx.author.id:
                if request.channelId == ctx.channel.id:
                    await ctx.reply(f"You are already tracking CRN: {crn}")
                else:
                    await ctx.reply(f"You are already tracking CRN: {crn} in channel <#{request.channelId}>")
                return
        global_request_list.new_request(TrackRequest(crn,"202502",ctx.author.id,ctx.channel.id))
        save_request_list(global_request_list)
        await ctx.reply("Now tracking CRN: " + crn + " for user " + ctx.author.name)

@tasks.loop(seconds=10)
async def check_crn():
    messages = []
    for request in global_request_list.trackRequests:
        if request.fetch():
            text = (f"<@{request.userId}> course status changed:" 
            + "\n" + str(request.course))
            messages.append((request.channelId,text))
        print(request.course)
    for message in messages:
        await bot.get_channel(message[0]).send(message[1],
                                               allowed_mentions=discord.AllowedMentions(users=True))

@bot.listen()
async def on_ready():
    check_crn.start()

bot.run(token)
