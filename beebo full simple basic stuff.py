import openai
import discord
from discord.ext import commands
import time

openai.api_key = "your OpenAI API code goes here"

intents = discord.Intents.all()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="", intents=intents)

last_request_time = 0
request_cooldown = 3  # seconds between requests
max_tokens = 128

project_triggered_user = None  # Variable to store the user who triggered the project list

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}')

@bot.event
async def on_message(message):
    global last_request_time
    global project_triggered_user

    if message.author.bot:
        return

    print(f'{message.author.name}#{message.author.discriminator}: {message.content}')

    if 'B-b0' in message.content or 'Beebo' in message.content:
        user_input = message.content.replace('B-b0', '').replace('Beebo', '').strip()

        # Use the default prompt without the project context
        prompt = f'{user_input}\nB-b0: '
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            stop=None,
            temperature=0.21,
        )

        await message.channel.send(response['choices'][0]['message']['content'])

bot.run('your Discord API goes here')
