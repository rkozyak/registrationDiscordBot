import discord
import asyncio

from courses import Course
from datetime import datetime
import threading

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
        await ctx.reply(f"Error: Please specify at least one CRN", mention_author=False)
        return
    crns = list(dict.fromkeys(crns)) #de-duplicate
    courses = []
    def fetch_info(crn):
        courses.append(Course(crn, "202502"))
    threads = [threading.Thread(target=fetch_info,args=(crn,)) for crn in crns]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    successfulCourses = []
    failedCrns = []
    for course in courses:
        if course.data['seats'] == -1:
            failedCrns.append(course.crn)
        else:
            successfulCourses.append(f"```\n{str(course)}```")
    message = '\n'.join(successfulCourses)
    if len(failedCrns) > 0:
        failedCrns = [f"`{crn}`" for crn in failedCrns]
        message += "Error: Could not retrieve CRN{}: {}\n".format("s" if len(failedCrns) > 1 else "", ", ".join(failedCrns))
    if len(message) > 2000:
        await ctx.reply("Error: Message longer than 2000 characters. Request fewer CRNs!", mention_author=False)
    else:
        await ctx.reply(message, mention_author=False)

@bot.command()
async def track(ctx: commands.Context, *crns):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if ctx.guild is None:
        await ctx.reply("Error: Can only call $track from a channel in a server", mention_author=False)
        return
    if len(crns) == 0:
        await ctx.reply(f"Error: Please specify at least one CRN", mention_author=False)
        return
    crns = list(dict.fromkeys(crns)) #de-duplicate

    successCrns = []
    alreadyTrackingCrns = []
    failedCrns = []

    def attempt_track(crn):
        for request in global_request_list:
            if request.crn == crn:
                if ctx.author.id in request.userIds:
                    alreadyTrackingCrns.append(crn)
                    return
                else:
                    request.userIds.append(ctx.author.id)
                    request.channelIds.append(ctx.channel.id)
                    successCrns.append(crn)
                    return
        newRequest = TrackRequest(crn,"202502",[ctx.author.id],[ctx.channel.id])
        if newRequest.course.data['seats'] == -1:
            failedCrns.append(crn)
        else:
            global_request_list.append(newRequest)
            save_request_list(global_request_list)
            successCrns.append(crn)
    threads = [threading.Thread(target=attempt_track,args=(crn,)) for crn in crns]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    message = ""
    if len(successCrns) > 0:
        successCrns = [f"`{crn}`" for crn in successCrns]
        message += "Now tracking CRN{}: {}\n".format("s" if len(successCrns) > 1 else "", ", ".join(successCrns))
    if len(alreadyTrackingCrns) > 0:
        alreadyTrackingCrns = [f"`{crn}`" for crn in alreadyTrackingCrns]
        message += "Error: You are already tracking CRN{}: {}\n".format("s" if len(alreadyTrackingCrns) > 1 else "", ", ".join(alreadyTrackingCrns))
    if len(failedCrns) > 0:
        failedCrns = [f"`{crn}`" for crn in failedCrns]
        message += "Error: Could not retrieve CRN{}: {}\n".format("s" if len(failedCrns) > 1 else "", ", ".join(failedCrns))
    await ctx.reply(message, mention_author=False)

@bot.command()
async def tracking(ctx: commands.Context):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    linked_requests: list[TrackRequest] = []
    for request in global_request_list:
        if ctx.author.id in request.userIds:
            linked_requests.append(request)
    if len(linked_requests) == 0:
        await ctx.reply("You are not tracking any courses", mention_author=False)
    else:
        message = "You are tracking:\n"
        for request in linked_requests:
            message += f"`{request.course.name}`\n"
        await ctx.reply(message, mention_author=False)

@bot.command()
async def untrack(ctx: commands.Context, *crns):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if len(crns) == 0:
        await ctx.reply(f"Error: Please specify at least one CRN", mention_author=False)
        return
    crns = list(dict.fromkeys(crns)) #de-duplicate
    successCrns = []
    failedCrns = []
    if crns[0] == "all":
        for request in global_request_list[:]:
            if ctx.author.id in request.userIds:
                global_request_list.remove(request)
                successCrns.append(request.crn)
        if len(successCrns) == 0:
            await ctx.reply("You are not tracking any CRNs")
            return
    else:
        for crn in crns:
            foundCRN = False
            for request in global_request_list:
                if ctx.author.id in request.userIds and request.crn == crn:
                    global_request_list.remove(request)
                    foundCRN = True
                    successCrns.append(crn)
                    break
            if not foundCRN:
                failedCrns.append(crn)
    save_request_list(global_request_list)
    message = ""
    if len(successCrns) > 0:
        successCrns = [f"`{crn}`" for crn in successCrns]
        message += "You are no longer tracking CRN{}: {}\n".format("s" if len(successCrns) > 1 else "", ", ".join(successCrns))
    if len(failedCrns) > 0:
        failedCrns = [f"`{crn}`" for crn in failedCrns]
        message += "Error: You are not tracking CRN{}: {}\n".format("s" if len(failedCrns) > 1 else "", ", ".join(failedCrns))
    await ctx.reply(message, mention_author=False)

bot.remove_command('help')
@bot.command()
async def help(ctx: commands.Context):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    await ctx.reply(
    """
    Commands:
        `$help`: Displays all commands.
        `$info CRN1 CRN2 ...` Displays info about one or more CRNs.
        `$track CRN1 CRN2 ...` Adds one or more CRNs to be tracked. User will be pinged when the status changes.
        `$untrack CRN1 CRN2 ...` Removes one or more CRNs from your tracking list.
        `$untrack all` Removes all CRNs from your tracking list.
        `$tracking` Displays all the courses you are tracking.
    """, mention_author=False)

@tasks.loop(seconds=10)
async def check_crn():
    tstart = datetime.now()
    threads = [threading.Thread(target=request.fetch) for request in global_request_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    tend = datetime.now()
    telapsed = tend - tstart
    print(f"Scraped {str(len(global_request_list))} courses in {telapsed.total_seconds()}s")
    messages = []
    for request in global_request_list:
        if request.statusChanged:
            channels = {}
            for i in range(len(request.userIds)):
                userId = request.userIds[i]
                channelId = request.channelIds[i]
                if channelId in channels:
                    channels[channelId].append(userId)
                else:
                    channels[channelId] = [userId]
            for channelId, userIds in channels.items():
                mentions = [f"<@{userId}>" for userId in userIds]
                text = f"{' '.join(mentions)} course status changed:\n```\n{str(request.course)}```" 
                messages.append((channelId,text))
    for message in messages:
        await bot.get_channel(message[0]).send(message[1],
                                               allowed_mentions=discord.AllowedMentions(users=True))

@bot.listen()
async def on_ready():
    if not check_crn.is_running():
        check_crn.start()

bot.run(token)
