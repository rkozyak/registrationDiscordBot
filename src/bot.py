import discord
import asyncio

from courses import Course
from datetime import datetime
import threading

from tracking import TrackRequest

from token_fetcher import get_token
from loader import load_request_list, save_request_list, construct_request_dict, construct_user_dict

from discord.ext import commands
from discord.ext import tasks

token = get_token()
global_request_list = load_request_list()
request_dict = construct_request_dict(global_request_list)
user_dict = construct_user_dict(global_request_list)

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.command()
async def info(ctx: commands.Context, *crns):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if len(crns) == 0:
        await ctx.reply("Error: Please specify at least one CRN", mention_author=False)
        return
    crns = list(dict.fromkeys(crns))  # de-duplicate
    courses = []

    def fetch_info(crn):
        courses.append(Course(crn, "202502"))

    threads = [threading.Thread(target=fetch_info, args=(crn,)) for crn in crns]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    successful_courses = []
    failed_crns = []

    for course in courses:
        if course.data['seats'] == -1:
            failed_crns.append(course.crn)
        else:
            successful_courses.append(course)

    embed = discord.Embed(
        title="Course Information",
        color=discord.Color.blue(),
    )

    if successful_courses:
        for course in successful_courses:
            embed.add_field(
                name=f"{course.name} - {course.crn}",
                value=(
                    f"Seats: **{course.data['seats']}**\n"
                    f"Taken: **{course.data['taken']}**\n"
                    f"Vacant: **{course.data['vacant']}**\n"
                    f"Waitlist Open: **{'Yes' if course.data.get('waitlist_open', False) else 'No'}**"
                ),
                inline=False
            )

    if failed_crns:
        embed.add_field(
            name="Failed to Retrieve",
            value=", ".join(f"`{crn}`" for crn in failed_crns),
            inline=False
        )

    if not successful_courses and not failed_crns:
        await ctx.reply("No valid course information found.", mention_author=False)
    else:
        await ctx.reply(embed=embed, mention_author=False)

@bot.command()
async def track(ctx: commands.Context, *crns):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if ctx.guild is None:
        await ctx.reply("Error: Can only call $track from a channel in a server", mention_author=False)
        return
    if len(crns) == 0:
        await ctx.reply(f"Error: Please specify at least one CRN", mention_author=False)
        return
    crns = list(dict.fromkeys(crns))  # de-duplicate

    successCrns = []
    alreadyTrackingCrns = []
    failedCrns = []

    def attempt_track(crn: str):
        if ctx.author.id in user_dict and crn in user_dict[ctx.author.id]:
            alreadyTrackingCrns.append(crn)
            return
        if crn in request_dict:
            request_dict[crn].userIds.append(ctx.author.id)
            request_dict[crn].channelIds.append(ctx.channel.id)
            successCrns.append(crn)
            if ctx.author.id in user_dict:
                user_dict[ctx.author.id].append(crn)
            else:
                user_dict[ctx.author.id] = [crn]
            return
        newRequest = TrackRequest(crn, "202502", [ctx.author.id], [ctx.channel.id])
        if newRequest.course.data['seats'] == -1:
            failedCrns.append(crn)
        else:
            global_request_list.append(newRequest)
            request_dict[crn] = newRequest
            successCrns.append(crn)
            if ctx.author.id in user_dict:
                user_dict[ctx.author.id].append(crn)
            else:
                user_dict[ctx.author.id] = [crn]

    threads = [threading.Thread(target=attempt_track, args=(crn,)) for crn in crns]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if len(successCrns) > 0:
        save_request_list(global_request_list)

    embed = discord.Embed(
        title="Tracking Status",
        color=discord.Color.green() if len(successCrns) > 0 else discord.Color.red()
    )

    # Success message
    if len(successCrns) > 0:
        successCrns = [f"`{crn}`" for crn in successCrns]
        embed.add_field(
            name="Now Tracking CRNs",
            value=f"Now tracking CRN{'s' if len(successCrns) > 1 else ''}: {', '.join(successCrns)}",
            inline=False
        )

    # Already tracking message
    if len(alreadyTrackingCrns) > 0:
        alreadyTrackingCrns = [f"`{crn}`" for crn in alreadyTrackingCrns]
        embed.add_field(
            name="Already Tracking CRNs",
            value=f"You are already tracking CRN{'s' if len(alreadyTrackingCrns) > 1 else ''}: {', '.join(alreadyTrackingCrns)}",
            inline=False
        )

    # Failure message
    if len(failedCrns) > 0:
        failedCrns = [f"`{crn}`" for crn in failedCrns]
        embed.add_field(
            name="Failed to Track CRNs",
            value=f"Error: Could not retrieve CRN{'s' if len(failedCrns) > 1 else ''}: {', '.join(failedCrns)}",
            inline=False
        )

    # If no success
    if not successCrns and not alreadyTrackingCrns and not failedCrns:
        await ctx.reply("No valid courses to track.", mention_author=False)
    else:
        await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def tracking(ctx: commands.Context):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    linked_requests: list[TrackRequest] = []
    
    # Check if the user is tracking any courses
    if ctx.author.id in user_dict:
        for crn in user_dict[ctx.author.id]:
            linked_requests.append(request_dict[crn])

    # If the user is not tracking any courses, send a simple message
    if len(linked_requests) == 0:
        await ctx.reply("You are not tracking any courses", mention_author=False)
    else:
        # Build the embed response
        embed = discord.Embed(
            title="Courses You Are Tracking",
            description="Here are the courses you're currently tracking:",
            color=discord.Color.blue()
        )
        
        # Add the courses as fields
        for request in linked_requests:
            embed.add_field(
                name=request.course.name,
                value=f"CRN: `{request.course.crn}`",
                inline=False
            )
        
        # Send the embed
        await ctx.reply(embed=embed, mention_author=False)

@bot.command()
async def untrack(ctx: commands.Context, *crns):
    print(f"\"{ctx.message.content}\" from user {ctx.author.name}")
    if len(crns) == 0:
        await ctx.reply(f"Error: Please specify at least one CRN", mention_author=False)
        return
    if ctx.author.id not in user_dict:
        await ctx.reply("You are not tracking any CRNs")
        return
    crns = list(dict.fromkeys(crns)) #de-duplicate
    successCrns = []
    failedCrns = []
    if crns[0] == "all":
        crns = user_dict[ctx.author.id][:]
    for crn in crns:
        if crn in user_dict[ctx.author.id]:
            index = request_dict[crn].userIds.index(ctx.author.id)
            del request_dict[crn].userIds[index]
            del request_dict[crn].channelIds[index]
            user_dict[ctx.author.id].remove(crn)
            successCrns.append(crn)
        else:
            failedCrns.append(crn)
    message = ""
    if len(successCrns) > 0:
        removedAnything = False
        for crn in successCrns:
            if len(request_dict[crn].userIds) == 0:
                global_request_list.remove(request_dict[crn])
                del request_dict[crn]
                removedAnything = True
        if removedAnything:
            save_request_list(global_request_list)
        if len(user_dict[ctx.author.id]) == 0:
            del user_dict[ctx.author.id]
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
