import discord
import asyncio

from courses import Course
from datetime import datetime

from tracking import TrackRequest

from token_fetcher import get_token
from loader import load_request_list, save_request_list

from discord.ext import commands
from discord.ext import tasks

token = get_token()
global_request_list = load_request_list()

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.command()
async def info(ctx: commands.Context, *crns):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if len(crns) == 0:
        await ctx.reply(f"Please specify at least one CRN")
        return        
    courses: list[Course] = [Course(crn, "202502") for crn in crns]
    for course in courses:
        if course.data['seats'] == -1:
            await ctx.reply(f"Error retrieving CRN: `{course.crn}`")
            return
    course_info: list[str] = [str(course) for course in courses]
    await ctx.reply('\n'.join(course_info))

@bot.command()
async def track(ctx: commands.Context, crn: str = None):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if ctx.guild is None:
        await ctx.reply("Can only call $track from a channel in a server")
        return
    if crn is None:
        await ctx.reply("Please specify a CRN")
        return
    for request in global_request_list:
        if request.crn == crn and request.userId == ctx.author.id:
            if request.channelId == ctx.channel.id:
                await ctx.reply(f"You are already tracking CRN: `{crn}`")
            else:
                await ctx.reply(f"You are already tracking CRN: `{crn}` in channel <#{request.channelId}>")
            return
    newRequest = TrackRequest(crn,"202502",ctx.author.id,ctx.channel.id)
    if newRequest.course.data['seats'] == -1:
        await ctx.reply(f"Error retrieving CRN: `{crn}`")
        return
    else:
        global_request_list.append(newRequest)
        save_request_list(global_request_list)
        await ctx.reply(f"Now tracking CRN: `{crn}`")

@bot.command()
async def tracking(ctx: commands.Context):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    linked_requests: list[TrackRequest] = []
    for request in global_request_list:
        if request.userId == ctx.author.id:
            linked_requests.append(request)
    if len(linked_requests) == 0:
        await ctx.reply("You are not tracking any courses")
    else:
        message = "You are tracking:\n"
        for request in linked_requests:
            message += f"{request.course.name}\n"
        await ctx.reply(message)

@bot.command()
async def untrack(ctx: commands.Context, crn: str = None):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if crn is None:
        await ctx.reply("Please specify a CRN")
        return
    for request in global_request_list:
        if request.userId == ctx.author.id and request.crn == crn:
            global_request_list.remove(request)
            save_request_list(global_request_list)
            await ctx.reply(f"You are no longer tracking CRN: `{crn}`")
            return
    await ctx.reply(f"You are not tracking CRN: `{crn}`")

bot.remove_command('help')
@bot.command()
async def help(ctx: commands.Context):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    await ctx.reply(
    """
    Commands:
        `$help`: Displays all commands.
        `$info CRN1 CRN2 ...` Displays info about one or more CRNs.
        `$track CRN` Adds a CRN to be tracked. User will be pinged when the status changes.
        `$untrack CRN` Removes a CRN from your tracking list.
        `$tracking` Displays all the courses you are tracking.
    """)

@tasks.loop(seconds=10)
async def check_crn():
    messages = []
    for request in global_request_list:
        if request.fetch():
            text = (f"<@{request.userId}> course status changed:" 
            + "\n" + str(request.course))
            messages.append((request.channelId,text))
        print(f"Scraped {request.course.name}")
    for message in messages:
        await bot.get_channel(message[0]).send(message[1],
                                               allowed_mentions=discord.AllowedMentions(users=True))

@bot.listen()
async def on_ready():
    check_crn.start()

bot.run(token)
