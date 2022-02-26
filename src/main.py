
from imageman.processing import *

from discord.ext import commands
from contest_data import contests
from message_parser import find_type, ContentType

import discord, os, random

client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    print("Started Bot!")

@client.event
async def on_message(message: discord.Message):
    content = message.content.lower()
    if not content.startswith("cloo give me"):
        return
    
    try:
        parsed, content_type = find_type(content)
    except AssertionError as error:
        error_message = error.args[0]
        await message.channel.send(f"```\n{error_message}\n```")

        return
    
    if content_type in (ContentType.SPECIFIC, ContentType.PSPECIFIC):
        contest_type, year, num, *rest = parsed
        part = rest[0] if rest else None
    
    elif content_type in (ContentType.CRANDOM, ContentType.RANDOM):
        contest_type = parsed if content_type == ContentType.CRANDOM else random.choice(list(contests))

        total_questions, years = contests[contest_type]
        
        year = random.randint(*years)
        part = None

        if contest_type in ('cimc', 'csmc'):

            part = random.choice(('A', 'B'))
            num = random.randint(1, 6 if part == 'A' else 3)
        else:
            num = random.randint(1, total_questions)
        
    contest = save_contest(contest_type, year)
    save_image(get_question(contest, num, part))
    
    information_str = f"**{contest_type.upper()}** {year} Question {num}"

    await message.channel.send(information_str, file=discord.File('saved.jpeg'))

    for file in ['saved.jpeg', contest]:
        if os.path.exists(file):
            os.remove(file)

client.run(TOKEN_HERE)
