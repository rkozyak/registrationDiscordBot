import discord
import asyncio

from courses import Course
from datetime import datetime

from token_fetcher import get_token
token = get_token()


intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):
    message_content = message.content
    message_author = message.author
    message_channel = message.channel
    print(f'New message -> {message_author} said: {message_content}')
    if not message_author.bot:
        await message_channel.send(content="Fetching info for CRN: " + message_content)
        await message_channel.send(content=fetch_course(message_content))

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

client.run(token)