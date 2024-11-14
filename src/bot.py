import discord
import asyncio

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

client.run(token)