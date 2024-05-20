import discord
from discord.ext import commands
from datetime import datetime, timedelta
import openai
import asyncio
import random
import re
import emoji
from collections import deque
import requests

# This script has some specific Discord roles related thingies 
# aaaand in the future I might make it so that it will create these roles when the bot joins to the server :3

openai.api_key = "OpenAI API"

intents = discord.Intents.all()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="", intents=intents)

max_tokens = 512

# Define a list of whitelisted words
whitelisted_words = ["whitelisted words go here"]

word_filter = ["bad words go here"]

allowed_characters = {'é', 'á', 'ö', 'ü', 'ó', 'ű', 'ú', 'ő', 'í'}

# Add your list of filtered words here
cooldown_time = timedelta(minutes=30)  # Updated cooldown time to 30 minutes
timeout_durations = [60, 600, 3600]
timeout_messages = [
    "You triggered a forbidden word. Timeout: 1 minute.",
    "Repeatedly triggering forbidden words. Timeout: 10 minutes.",
    "Continued violation. Timeout: 1 hour."
]

user_last_triggered = {}  # Dictionary to store the timestamp of the last trigger for each user

dm_responses_count = {}

sentenced_users = []

# Dictionary to store user message counts
user_message_counts = {}

# Initialize a deque to store the user IDs
user_id_history = deque(maxlen=10)

# List to store users who want to join the gaming session
gaming_players = []
triggered = False

is_bot_active = True  # Flag to indicate whether the bot is active
blackjack_active = False  # Flag to indicate whether the blackjack feature is active

blackjack_games = {}

rps_player_id = None

bomboclat_mode = False
disability_mode = False
specialchars_active = False
weeb_mode = False
haix_mode = False
brokey_mode = False
saul_mode = False
casual_mode = True

# Set the cooldown time to 10 minutes (600 seconds)
cooldown_time_fr = 600  

# Initialize last_triggered_time_fr as None initially
last_triggered_time_fr = None

# Bot's uptime
start_time = datetime.now()

battery_updated = False
original_battery_percentage = None  # Assume full battery at start
remaining_percentage = None  # Initialize to None
difference = 0

battery_warning = False

# Variable to track whether the "maybe check heaven?" mode is active
heaven_mode_active = False

# Fucking Stream announcement
streaming_yes = False
stream_checked = False
stream_stop_active = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}')

# Start the uptime check coroutine
    bot.loop.create_task(check_uptime())
    bot.loop.create_task(check_stream())

@bot.event
async def on_message(message):
    global is_bot_active, stream_stop_active, heaven_mode_active, start_time, battery_warning, battery_updated, original_battery_percentage, remaining_percentage, difference, blackjack_active, disability_mode, specialchars_active, last_triggered_time_fr, triggered, bomboclat_mode, weeb_mode, haix_mode, brokey_mode, casual_mode, saul_mode, rps_player_id

    if message.author.bot:
        return

    # Check if enough time has passed since the last trigger
    current_time = datetime.now()

    print(f'{message.author.name}#{message.author.discriminator}: {message.content}')

# On/Off
    
    # Check for shut down command
    if message.content.lower() == 'shut down':
        # Check if the user has the "epic gamer (mod)" role
        if any(role.name == 'epic gamer (mod)' for role in message.author.roles): # like this is role specific that's what I meant above
            await message.channel.send("Shut down process initiated...")

            # Countdown
            for i in range(3, 0, -1):
                await asyncio.sleep(1)
                await message.channel.send(f"{i}...")

            # Random bye bye phrase
            bye_phrases = ["Goodbye chat!",
                           "Farewell!",
                           "Adiós, amigos!",
                           "See you later!",
                           "See you later, alligator! In a while, crocodile!",
                           "Time to bounce, pounce, and flounce! Bye!",
                           "Catch you on the flip side, pancake pride!",
                           "Exit stage left, like a ninja in pajamas!",
                           "Toodle-oo, kangaroo! Keep it cool like a swimming pool!",
                           "Outta here like a rocketeer on roller skates. Bye-bye!",
                           "Smell you later, potato gratinator! Stay spud-tacular!",
                           "Time to vanish like a ninja cat on a stealth mission. Poof!"]
            random_bye_phrase = random.choice(bye_phrases)
            await message.channel.send(f"{random_bye_phrase} <:happi:1202300923460980756>")

            # Bot stops responding
            is_bot_active = False
            blackjack_active = False  # Deactivate blackjack when bot is shut down
        else:
            await message.channel.send("Nuh uh")

    # Check for wakey wakey command
    elif message.content.lower() == 'wakey wakey':
        # Check if the user has the "epic gamer (mod)" role
        if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
            hai_phrases = ["I'm awake and ready!",
                           "Rise and shine, my digital amigo! Ready for some banter?",
                           "Top of morning, tip of kok!", "Hello there!",
                           "Greetings, fellow citizen of the server!",
                           "Hey hey, disco dude! Ready to boogie through the bytes?",
                           "Greetings, Earthling! The bot is back and open for intergalactic conversations.",
                           "Good day, fine user! Let's embark on another epic chatventure.",
                           "Ahoy, matey! The bot sails back into the server seas. What's the word?",
                           "Hello, hello!",
                           "Salutations, sentient being! Let the chatter commence!",
                           "Suh dude"]
            random_hai_phrase = random.choice(hai_phrases)
            await message.channel.send(f"{random_hai_phrase} <:happi:1202300923460980756>")
            is_bot_active = True  # Set the flag to True to resume normal operations
            blackjack_active = False
        else:
            await message.channel.send("i slip")

    if message.content.lower() == 'rigged':
        blackjack_active = True

    if message.content.lower() == 'legit':
        blackjack_active = False

    # Your other message handling logic goes here
    if is_bot_active:

# Limit DMs

        # Define a list of user IDs exempt from the limit
        exempt_users = []  # Add the IDs of exempt users here, Discord ID goes here (bunch of numbers)

        author_id = message.author.id
        if message.guild is None:
            # Message is sent via DM
            author_id = message.author.id

            # Check if the user is exempt from the limit
            if author_id in exempt_users:
                # Process the message without limit
                pass
            else:
                if author_id not in dm_responses_count:
                    dm_responses_count[author_id] = 1
                else:
                    dm_responses_count[author_id] += 1

                # Check if the user has exceeded the response limit
                if dm_responses_count[author_id] > 5:
                    await message.channel.send("You have reached the maximum limit for DM responses.")
                    return


# No making bot say someting times fu - aka repetitive bot response prevention

        # Check for abusive message pattern
        content_lower = message.content.lower()

        if re.search(r"\b(?:say|spell|type)\b.*\b(?:time(?:s)?|backward(?:s)?)\b", content_lower):
            # Send a response to discourage abuse
            await message.channel.send("https://tenor.com/view/no-i-dont-think-i-will-captain-america-old-capt-gif-17162888")
            return
        
            # Word replacer
        if "cap" in content_lower:
            # Check if the message contains just "cap"
            if content_lower.strip() == "cap":
                await message.channel.send("🧢")

            # Check if the message has "no cap"
            if content_lower.strip() == "no cap":
                await message.channel.send("🚫🧢")
            else:
                match = re.search(r'\b(\w*cap\w*)\b', message.content.lower())
                if match:
                    word = match.group(1)
                    # Replace "cap" with "C A P" and capitalize each letter
                    replaced_word = word.replace("cap", "C A P")
                    # Send the modified word with the cap emoji
                    await message.channel.send(replaced_word.strip() + " 🧢")
                        
        # Check for other specific messages
        cool_list = ['cool', 'cooi']
        if any(cool in content_lower for cool in cool_list):
            # Delete the user's message and send the sunglasses emoji
            await message.delete()
            await message.channel.send("😎")
        
        if content_lower == "ok":
            # Delete the user's message and send the OK hand sign emoji
            await message.delete()
            await message.channel.send("👌")

        if content_lower == "fasz":
            await message.channel.send("8=D")

# Blackjack 1/2

        if "blackjack" in message.content.lower():
            if blackjack_active:
                await play_blackjack(message)
            else:
                await message.channel.send("Blackjack is not active right now. Wake up the bot and try again!")

# Wish the big luck

        if 'wish me luck' in message.content.lower():
            # Random wish phrase
            wish_phrases = ["Break a leg! But not literally, we need you in one piece!",
                            "May your luck be stronger than your Wi-Fi connection!",
                            "Good luck! Remember, even a broken clock is right twice a day!",
                            "May your luck be like a squirrel, relentless and a little bit nuts!",
                            "You've got this!",
                            "Go slay!",
                            "Luck mode: ON!"
                            "May the force be with you!",
                            "Take a deep breath, believe in yourself, and go make it happen!",
                            "May your luck be as plentiful as snacks in a gamer's lair. Go for it!",
                            "May your luck be as endless as cat videos on the internet. Good luck!",
                            "Go get 'em boah!",
                            "Good luck! If luck were pixels, you'd be playing in 8K resolution!",
                            "Hoping your luck is so good it's almost suspicious. Best of luck!",
                            "May your luck be as consistent as autocorrect fails!",
                            "Wishing you luck as persistent as spam emails",
                            "Break a pencil! (Because breaking legs is too mainstream.) Best of luck!"]
            random_wish_phrase = random.choice(wish_phrases)
            await message.channel.send(f"{random_wish_phrase} <:happi:1202300923460980756>")

# Gaming queue - for 5 player lobby

        content_lower = message.content.lower()
        
        if "who is ready for gaming guise" in content_lower:
            # Check if the author has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                await message.channel.send("Please send 'me' in the chat to play with the big nuster plis")
                triggered = True

        if triggered:
            if re.search(r'\bme\b', content_lower, re.IGNORECASE):
                if message.author in gaming_players:
                    await message.channel.send("You're already on the gaming list!")
                else:
                    gaming_players.append(message.author)
                    await message.channel.send(f"{message.author.mention} gotchu gamer!")

            if "show the gaming" in content_lower:
                # Check if the author has the "epic gamer (mod)" role
                if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                    # Ensure there are enough players for the gaming session
                    if len(gaming_players) >= 4:
                        # Randomly select 4 players from the list
                        selected_players = random.sample(gaming_players, k=4)
                        # Send a message with the selected players
                        players_mention = " ".join([player.mention for player in selected_players])
                        await message.channel.send(f"Here is the gaming squad: {players_mention}")
                        triggered = False
                        # Clear the gaming player list
                        gaming_players.clear()
                    else:
                        await message.channel.send("Not enough players for the gaming session!")

            if "show nuster list" in content_lower:
                # Check if the author has the "epic gamer (mod)" role
                if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                    # Send a message listing all the players in the gaming list
                    if gaming_players:
                        players_mention = "\n".join([player.mention for player in gaming_players])
                        await message.channel.send(f"Players in the gaming list:\n{players_mention}")
                    else:
                        await message.channel.send("No players in the gaming list.")

# Nixann mode

        if message.content.lower() == 'ascii':
            specialchars_active = True

        if message.content.lower() == 'noscii':
            specialchars_active = False

        if specialchars_active:
            # Check if the user has the 'epic gamer (mod)' role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Allow messages from users with the 'epic gamer (mod)' role
                pass
            else:
                if not all(char.isascii() or char in allowed_characters or emoji.is_emoji(char) for char in message.content.lower()):
                # If the message contains non-Latin characters
                    try:
                        # Remove the message that triggered the non-Latin characters
                        await message.delete()
                    except discord.errors.NotFound:
                        pass  # Ignore NotFound error if the message is already deleted

                    # Respond to the user
                    await message.channel.send(f"{message.author.mention} inglish plis!")
        else:
            pass

        if 'fuck you beebo' in message.content.lower():
            await message.channel.send("no u")

# Reminder 1/2

        if 'remind me' in message.content.lower():
            await handle_reminder(message)

# Remindus 1/2

        if 'remind us' in message.content.lower():
            await handle_remindus(message)

# Most perfect pasta recipe ever to exist :)

        if 'most perfect pasta recipe ever to exist' in message.content.lower():
            await message.channel.send(f"You need:\nHam\nLike a dozen shrimp\nPasta\n1 tablespoon peanutbutter\nSome milk to make it creamy\nBuldak hot sauce\n2 tablespoon oyster sauce\n1 egg\n\nNow... you have to cook the pasta, fry the ham and prepare the shrimps. You need to mix all the stuff for the sauce then mix everything and finally add the egg like you'd make carbonara. Enjoy!")

# French Revolution

        if last_triggered_time_fr is None or current_time - last_triggered_time_fr >= timedelta(seconds=cooldown_time_fr):
            # Check for the "fr" trigger
            if re.search(r'\bfr\b', message.content, re.IGNORECASE):
                # Execute the French Revolution command
                response_message = f"French Revolution"
                await message.channel.send(response_message)

                # Update the last triggered time
                last_triggered_time_fr = current_time

# Flip a coin

        if message.content.lower() == 'flip a coin':
            coin = random.choice(['Heads <:happi:1202300923460980756>', 'Tails <:catDespair:1204871470023442512>']) # oh yea these are some custom server emojis so you might wanna change it
            await message.channel.send("The coin landed on...")
            await asyncio.sleep(2)
            await message.channel.send(coin)

# Maybe check heaven? (de_nuke callout, real gamers know)

        if 'heaven' in message.content.lower():
            heaven_mode_active = True
            while heaven_mode_active:
                # Generate a random time interval
                interval = generate_random_interval()

                # Wait for the random time interval
                await asyncio.sleep(interval)

                # Send the message
                maybe_messages = ["maybe",
                                "m-maybe",
                                "maybe... maybe",
                                "mmmmmm... maybe",
                                "maybe... m-maybe",
                                "mabe",
                                "m-mabe",
                                "mabe... mabe",
                                "mmmmmm... mabe",
                                "mabe... m-mabe"]
                random_maybe = random.choice(maybe_messages)

                check_messages = ["check",
                                "shek",
                                "checc",
                                "sheck",
                                "shecc"]
                random_check = random.choice(check_messages)

                heaven_messages = ["heaven",
                                "heeven",
                                "heven",
                                "hevan",
                                "hevon",
                                "heevan",
                                "heevon",
                                "heeven"]
                random_heaven = random.choice(heaven_messages)

                await message.channel.send(f'{random_maybe} {random_check} {random_heaven}?')

        if 'hell' in message.content.lower():
            if heaven_mode_active:
                heaven_mode_active = False
                await message.channel.send("oke")

# Welcome
        
        # Check for the "thank you" 
        if 'thank you' in message.content.lower():
            # Execute the kebab
            response_message = "welcome <:happi:1202300923460980756>"
            await message.channel.send(response_message)

# Kebab
   
        # Check for the "kebab" 
        if re.search(r'\bkebab\b', message.content, re.IGNORECASE):
            # Execute the kebab
            response_message = "<:stuffed_flatbread:1219338686622072882>"
            await message.channel.send(response_message)

# Ohnepickel und anderen reaktionen
            
        # Check for the "was" 
        if message.content.lower() == 'was':
            regular_was_gifs = ["https://tenor.com/view/ohnepixel-lambda-hee-vas-is-that-even-allowed-gif-25355973"]

            rare_was_gif = "https://tenor.com/view/ohnepixel-ohnepixel-sussy-ohnepixel-boobs-boobs-booba-gif-26421594"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_was_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_was_gif)

        # Check for the "drive" 
        if message.content.lower() == 'i drive':
            regular_drive_gifs = ["https://tenor.com/view/i-drive-drive-my-car-gif-7675608"]

            rare_drive_gif = "https://tenor.com/view/drive-ryan-gosling-ryan-gosling-drive-literally-me-ryan-gosling-ken-gif-4477899586321581902"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_drive_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_drive_gif)

        # Check for the "sheesh" 
        if message.content.lower() == 'sheesh':
            regular_sheesh_gifs = ["https://tenor.com/view/sheeesh-sheesh-gif-22353817",
                                   "https://tenor.com/view/sheesh-sheesh-meme-gif-23678188",
                                   "https://tenor.com/view/sheesh-sheeesh-hype-cat-gif-25828278",
                                   "https://tenor.com/view/sheesh-geez-gif-22199581",
                                   "https://tenor.com/view/sheesh-sheeesh-tiktok-tiktok-meme-the-boys-gif-21070829"
                                   ]

            rare_sheesh_gif = "https://tenor.com/view/sheesh-sheeesh-sheeeesh-bro-bruh-gif-22818626"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_sheesh_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_sheesh_gif)

        # Check for the "drive" 
        if message.content.lower() == 'max verstappen':
            regular_verstappen_gifs = ["https://tenor.com/view/max-verstappen-f1-formule-1-gif-15087359750872636720"]

            rare_verstappen_gif = ["https://tenor.com/view/max-verstappen-formula1-dutch-max-verstappen-gif-26539525",
                                   "https://tenor.com/view/verstappen-max-verstappen-f1-racing-jos-verstappen-gif-14899758",
                                   "https://tenor.com/view/max-verstappen-gif-9973613431036796750"]
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_verstappen_gif = random.choice(regular_verstappen_gifs)
                await message.channel.send(random_verstappen_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                random_rareverstappen_gif = random.choice(rare_verstappen_gif)
                await message.channel.send(random_rareverstappen_gif)

        # Check for the "💀" 
        if '💀' in message.content.lower():
            regular_skull_gifs = ["https://tenor.com/view/cod-mw2-cod-mw2ghost-cod-ghost-ghost-stare-stare-gif-27067874"]
            
            rare_skull_gif = "https://tenor.com/view/skull-explode-gif-25528415"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_skull_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_skull_gif)

        # Check for the "🤔" 
        if '🤔' in message.content.lower():
            regular_think_gifs = ["https://tenor.com/view/think-emoji-thinking-in-thought-rotate-gif-8083088",
                        "https://tenor.com/view/thinking-questioning-wondering-emoji-gif-8208624",
                        "https://tenor.com/view/thinking-thinking-emoji-infinite-infinite-zoom-droste-gif-26468372",
                        "https://tenor.com/view/thinking-emoji-confused-emoji-infinity-confused-thinking-emoji-gif-12911356",
                        "https://tenor.com/view/think-emoji-thonk-meme-gif-11987860",
                        "https://tenor.com/view/hmmm-think-emoji-flex-gif-17060789",
                        "https://tenor.com/view/thinking-face-thinking-emoji-meme-gif-19818182",
                        "https://tenor.com/view/think-emoji-thinking-in-thought-rotate-gif-8083088",
                        "https://tenor.com/view/thinking-questioning-wondering-emoji-gif-8208624",
                        "https://tenor.com/view/thinking-thinking-emoji-infinite-infinite-zoom-droste-gif-26468372",
                        "https://tenor.com/view/thinking-emoji-confused-emoji-infinity-confused-thinking-emoji-gif-12911356",
                        "https://tenor.com/view/think-emoji-thonk-meme-gif-11987860",
                        "https://tenor.com/view/hmmm-think-emoji-flex-gif-17060789",
                        "https://tenor.com/view/thinking-face-thinking-emoji-meme-gif-19818182"]
            
            rare_think_gif = "https://tenor.com/view/hmm-sun-hmm-sun-gif-25321101"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_think_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_think_gif)


        # Check for the "drilla" 
        if re.search(r'\bdrilla\b', message.content, re.IGNORECASE):
            regular_drilla_gifs = ["https://tenor.com/view/ohnepixel-drilla-csgo-gif-13485077269813264205"]
            
            rare_drilla_gif = "https://tenor.com/view/rip-bozo-ohnepixel-gif-26295704"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_drilla_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_drilla_gif) 

        # Check for the "report" 
        if re.search(r'\breport\w*\b', message.content, re.IGNORECASE):
            regular_report_gifs = ["https://tenor.com/view/star-trek-trek-report-status-damage-gif-21869277"]
            
            rare_report_gif = "https://tenor.com/view/toji-megumi-toji-fushiguro-megumi-fushiguro-discord-gif-2805240552671542658"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_report_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_report_gif)

 
        # Check for the "no way" 
        noway_stuff = ['no wa', 'noway', 'ainnowae', 'ainnoway', "ain't no way", "ain't noway"]
        if any(noway in message.content.lower() for noway in noway_stuff):
            regular_noway_gifs = ["https://tenor.com/view/noway-no-way-ain't-no-way-ainnowaemahboa-gif-6541435503460309133"]
            
            rare_noway_gif = "https://tenor.com/view/boy-aint-no-way-wow-gif-22526930"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_noway_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_noway_gif)

        # Check for the "GG" 
        if message.content.lower() == 'gg':
            regular_gg_gifs = ["https://tenor.com/view/gg-gif-24670718",
                               "https://tenor.com/view/gg-meme-dank-cursed-khat-gif-21280690",
                               "https://tenor.com/view/alien-gg-gif-27684675",
                               "https://tenor.com/view/pewdiepie-brofist-gg-gif-27128168",
                               "https://tenor.com/view/gg-gif-20863608",
                               "https://tenor.com/view/vegeta-gg-funny-gif-27616929",
                               "https://tenor.com/view/henya-vshojo-gg-gif-5775450130544379213",
                               "https://tenor.com/view/gautam-gambhir-gg-good-game-gif-25445097",
                               ]
            
            rare_gg_gif = "https://tenor.com/view/morgan-freeman-freeman-goodgame-gg-good-gif-14900806"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_gg_gif = random.choice(regular_gg_gifs)
                await message.channel.send(random_gg_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_gg_gif)

        # Check for the "dik" 
        if message.content.lower() == 'dik':
            regular_dik_gifs = ["https://tenor.com/view/dik-excuse-me-well-ex-dik-az-diiik-gif-6919552955213007891"]
            
            rare_dik_gif = "https://tenor.com/view/dikszoszi-gif-20320611"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_dik_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_dik_gif)

        # Check for the "F" 
        if message.content.lower() == 'f':
            regular_f_gifs = ["https://tenor.com/view/press-f-f-discord-discord-gif-19730487",
                      "https://tenor.com/view/%D0%B0-gif-5603829086996314084",
                      "https://tenor.com/view/press-f-respect-pay-respects-keyboard-egirl-gif-12490772931175630258",
                      "https://tenor.com/view/press-f-f-discord-discord-gif-19730487",
                      "https://tenor.com/view/%D0%B0-gif-5603829086996314084",
                      "https://tenor.com/view/press-f-respect-pay-respects-keyboard-egirl-gif-12490772931175630258",
                      "https://tenor.com/view/press-f-f-discord-discord-gif-19730487",
                      "https://tenor.com/view/%D0%B0-gif-5603829086996314084",
                      "https://tenor.com/view/press-f-respect-pay-respects-keyboard-egirl-gif-12490772931175630258"]
            
            rare_f_gif = "https://tenor.com/view/top-gun-icemav-top-gun-maverick-top-gun-maverick-funeral-funeral-gif-26848803"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_f_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_f_gif)

        # Check for the "duit" 
        if message.content.lower() == 'duit':
            regular_duit_gifs = ["https://tenor.com/view/doit-starwars-kill-gif-5023949"]

            rare_duit_gif = "https://tenor.com/view/palpatine-do-it-gif-26306996"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_duit_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_duit_gif)

        # Check for the "W" 
        if message.content.lower() == 'w':
            regular_w_gifs = ["https://tenor.com/view/ee-gif-25984691",
                      "https://tenor.com/view/giga-chad-chad-meme-dub-gif-25628266",
                      "https://tenor.com/view/cablethanos-seahawkstwitter-seahawks-hawks-win-gif-13081932",
                      "https://tenor.com/view/ee-gif-25984691",
                      "https://tenor.com/view/giga-chad-chad-meme-dub-gif-25628266",
                      "https://tenor.com/view/cablethanos-seahawkstwitter-seahawks-hawks-win-gif-13081932",
                      "https://tenor.com/view/ee-gif-25984691",
                      "https://tenor.com/view/giga-chad-chad-meme-dub-gif-25628266",
                      "https://tenor.com/view/cablethanos-seahawkstwitter-seahawks-hawks-win-gif-13081932"]
            
            rare_w_gif = "https://tenor.com/view/look-at-the-size-of-this-w-spongebob-patrick-star-blinking-cant-say-anything-gif-17814649"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_w_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_w_gif)

        # Check for the "L" 
        if message.content.lower() == 'l':
            regular_l_gifs = ["https://tenor.com/view/mayweather-for-you-throw-gif-8082067",
                      "https://tenor.com/view/faizal-khamisa-faizal-khamisa-sportsnet-take-this-l-gif-27534119",
                      "https://tenor.com/view/take-this-l-hold-this-l-linus-linus-tech-tips-hold-this-gif-26138312",
                      "https://tenor.com/view/mayweather-for-you-throw-gif-8082067",
                      "https://tenor.com/view/faizal-khamisa-faizal-khamisa-sportsnet-take-this-l-gif-27534119",
                      "https://tenor.com/view/take-this-l-hold-this-l-linus-linus-tech-tips-hold-this-gif-26138312",
                      "https://tenor.com/view/mayweather-for-you-throw-gif-8082067",
                      "https://tenor.com/view/faizal-khamisa-faizal-khamisa-sportsnet-take-this-l-gif-27534119",
                      "https://tenor.com/view/take-this-l-hold-this-l-linus-linus-tech-tips-hold-this-gif-26138312"]
            
            rare_l_gif = "https://tenor.com/view/higgs-death-stranding-l-gif-2271667657248183530"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_l_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_l_gif)

        # Check for the "plink" 
        if message.content.lower() == 'plink':
            regular_plink_gifs = ["https://tenor.com/view/plink-cat-plink-cat-gif-1794292671885121408"]

            rare_plink_gif = "https://tenor.com/view/plink-plinkvibe-cat-gif-3291306745104440128"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_plink_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_plink_gif)         

        # Check for the "wo" 
        if message.content.lower() == 'wo':
            regular_wo_gifs = ["https://tenor.com/view/mouth-drop-woah-sparkly-eyes-sparkle-blush-gif-8681516",
                                "https://tenor.com/view/pikachu-shocked-face-stunned-pokemon-shocked-not-shocked-omg-gif-24112152",
                                "https://tenor.com/view/shocked-surprised-gasp-what-cat-shock-gif-635629308990545194",
                                "https://tenor.com/view/surprised-sorprendido-shaquille-oneal-gif-23222312",
                                "https://tenor.com/view/anime-frieren-anime-shocked-drop-book-frieren-beyond-journeys-end-gif-4911429611178279007",
                                "https://tenor.com/view/oh-no-gif-24189318",
                                "https://tenor.com/view/anime-konosuba-shocked-shocked-face-surprise-gif-13893147",
                                "https://tenor.com/view/eh-shomin-sample-wtf-animecute-gif-21035027",
                                ]

            rare_wo_gif = "https://tenor.com/view/shock-shocker-shocked-black-guy-gif-27526370"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_wo_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_wo_gif)         


        # Check for the "misinput" 
        misinput_stuff = ['misinput', 'misclick', 'missclick']
        if any(misinput in message.content.lower() for misinput in misinput_stuff):
            regular_misinput_gifs = ["https://tenor.com/view/moistcritikal-penguinz0-charlie-misinput-it-was-a-misinput-gif-23090919"]
            
            rare_misinput_gif = "https://tenor.com/view/misclick-misinput-oops-whoopsie-gif-6912570317298118585"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_misinput_gif = random.choice(regular_misinput_gifs)
                await message.channel.send(random_misinput_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_misinput_gif)


        # Check for the "restarted" 
        if re.search(r'\brestarted\b', message.content, re.IGNORECASE):
            await message.channel.send("https://tenor.com/view/dragon-ball-z-goku-clapping-happy-gif-19981641")


        # Check for the "haram" 
        if re.search(r'\bharam\b', message.content, re.IGNORECASE):
            regular_haram_gifs = ["https://tenor.com/view/haram-gif-26607190",
                        "https://tenor.com/view/haram-heisenberg-gif-20680378",
                        "https://tenor.com/view/haram-gif-18566347",
                        "https://tenor.com/view/haram-anomaly-lock-sussy-haram-gif-21477600",
                        "https://tenor.com/view/haram-gif-26607190",
                        "https://tenor.com/view/haram-heisenberg-gif-20680378",
                        "https://tenor.com/view/haram-gif-18566347",
                        "https://tenor.com/view/haram-anomaly-lock-sussy-haram-gif-21477600"]
            
            rare_haram_gif = "https://tenor.com/view/king-hassan-first-hassan-fgo-fate-grand-order-haram-gif-26104872"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_haram_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_haram_gif)


        # Check for the "bruh" 
        if re.search(r'\bbruh\b', message.content, re.IGNORECASE):
            regular_bruh_gifs = ["https://tenor.com/view/bruh-gif-19257317"]
            
            rare_bruh_gif = "https://tenor.com/view/tsukasa-tenma-tsukasa-angry-tsukasa-shock-tsukasa-reaction-gif-9249615244307729236"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_bruh_gif = random.choice(regular_bruh_gifs)
                await message.channel.send(random_bruh_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_bruh_gif)

        # Check for the "69" 
        if re.search(r'\b69\b', message.content, re.IGNORECASE):
            regular_nice_gifs = ["https://tenor.com/view/nice-gif-8044179",
                        "https://tenor.com/view/thumbs-up-double-thumbs-up-like-agreed-yup-gif-16109683157885754862",
                        "https://tenor.com/view/noice-gif-21882904",
                        "https://tenor.com/view/nice-gif-21458880",
                        "https://tenor.com/view/beavis-butthead-laugh-laughing-gif-15287783896027437373",
                        "https://tenor.com/view/nice-the-rock-sus-the-rock-sus-meme-louis-thrane-gif-25854498",
                        "https://tenor.com/view/nice-gif-8044179",
                        "https://tenor.com/view/thumbs-up-double-thumbs-up-like-agreed-yup-gif-16109683157885754862",
                        "https://tenor.com/view/noice-gif-21882904",
                        "https://tenor.com/view/nice-gif-21458880",
                        "https://tenor.com/view/beavis-butthead-laugh-laughing-gif-15287783896027437373",
                        "https://tenor.com/view/nice-the-rock-sus-the-rock-sus-meme-louis-thrane-gif-25854498"]
            
            rare_nice_gif = "https://tenor.com/view/oh-yeah-nice-gif-14153667"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_nice_gifs)
                await message.channel.send(random_regular_gif)
                await message.channel.send("69")
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_nice_gif)
                await message.channel.send("69")

        # Check for the "simple" 
        simple_stuff = ['s1mple', 'simple', 'simpel', 'simpol', 'pimpol', 'zaza', '420']
        if any(simple in message.content.lower() for simple in simple_stuff):
            await message.channel.send("https://tenor.com/view/simple-s1mple-simpol-zaza-simple-zaza-gif-9972159044225534389")

        # Check for the "MLG" 
        if re.search(r'\bmlg\b', message.content, re.IGNORECASE):
            mlg_gifs = ["https://tenor.com/view/rekt-gif-25016725",
                        "https://tenor.com/view/ddf-mlg-wink-gif-15688443",
                        "https://tenor.com/view/litty-mlg-wow-gif-22702489",
                        "https://tenor.com/view/gabbiehanna-thegabbieshow-swag-dab-dabbing-gif-22156041",
                        "https://tenor.com/view/mlg-penguinz-penguinz-meme-penguinz-meme-penguinz-gif-gif-20516054",
                        "https://tenor.com/view/mlg-snoop-dogg-doritos-mountaun-dew-yolo-gif-14326298",
                        "https://tenor.com/view/wow-cat-thug-life-doritos-mountain-dew-gif-14737452",
                        "https://tenor.com/view/jalal-halak-jalal-halak-math-teacher-sst-gif-12463444",
                        "https://tenor.com/view/transformice-transformice-emote-transformice-kiss-yrdmax-leeply-gif-25416323",
                        ]
            random_mlg_gif = random.choice(mlg_gifs)
            await message.channel.send(random_mlg_gif)            

        # Check for the "green" 
        if message.content.lower() == 'green':
            regular_tense_gifs = ["https://tenor.com/view/tense1983-tense-csgo-gif-15600543",
                          "https://tenor.com/view/tense-gif-19013622",
                          "https://tenor.com/view/tense1983-tense-spain-epic-csongo-gif-15101114",
                          "https://tenor.com/view/tense1983-csgo-rage-angry-slam-gif-14690595",
                          "https://tenor.com/view/tense1983-rage-csgo-best-troll-eu-gif-14590429",
                          "https://tenor.com/view/tense1983-rage-computer-keyboard-mad-gif-17503472",
                          "https://tenor.com/view/green-gif-19259031",
                          "https://tenor.com/view/tense1983-green-whats-your-problem-gif-2264510229100353237",
                          "https://tenor.com/view/rage-gif-23450148",
                          "https://tenor.com/view/tense1983-gif-14151875",
                          "https://tenor.com/view/tense1983-gif-24718683"]
            
            rare_tense_gif = "https://tenor.com/view/tense-tense1983-csgo-counter-strike-excited-gif-17524674"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_tense_gifs)
                await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_tense_gif)

# Magic 8 ball

        # Check for the "magic8" 
        magic8_stuff = ['magic8', 'magic 8', 'magic8ball', 'magic 8ball', 'magic8 ball' 'magic 8 ball']
        if message.content.lower() in magic8_stuff:
            await message.channel.send(f"Please use the format 'magic8 [your question]'")

        elif any(magic8_word in message.content.lower() for magic8_word in magic8_stuff):
            magic8_responses = ["It is certain",
                                "It is decidedly so",
                                "Without a doubt",
                                "Yes definitely",
                                "You may rely on it",
                                "As I see it, yes",
                                "Most likely",
                                "Outlook good",
                                "Yes",
                                "Signs point to yes",
                                "Reply hazy, try again",
                                "Ask again later",
                                "Better not tell you now",
                                "Cannot predict now",
                                "Concentrate and ask again",
                                "Don't count on it",
                                "My reply is no",
                                "My sources say no",
                                "Outlook not so good",
                                "Very doubtful"]
            random_magic8 = random.choice(magic8_responses)
            await message.channel.send("Hmmm let's see... 🔮")
            await asyncio.sleep(2)
            await message.channel.send("https://tenor.com/view/8ball-bart-simpson-shaking-shake-magic-ball-gif-17725278")
            await asyncio.sleep(1)
            await message.channel.send(f"**{random_magic8}**")

# What's yappening

        # Check if the user id is already in the dictionary
        if message.author.id in user_message_counts:
            # Get the last message time for the user
            last_message_time = user_message_counts[message.author.id]["last_message_time"]
            
            # Check if the last message was sent within
            if current_time - last_message_time < timedelta(seconds=30):
                # Increment the message count for the user
                user_message_counts[message.author.id]["message_count"] += 1
            else:
                # Reset the message count when the last message was sent
                user_message_counts[message.author.id]["message_count"] = 1

            # Update the last message time for the user
            user_message_counts[message.author.id]["last_message_time"] = current_time
        else:
            # Add the user to the dictionary if not already present
            user_message_counts[message.author.id] = {
                "message_count": 1,
                "last_message_time": current_time
            }
            
        # Add the user ID to the history
        user_id_history.append(message.author.id)

        # Check if all user IDs in the history are the same (spam))
        if len(set(user_id_history)) == 1 and len(user_id_history) == 10:
            # Check if the user has the 'epic gamer (mod)' role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Allow messages from users with the 'epic gamer (mod)' role
                pass
            else:
                if user_message_counts[message.author.id]["message_count"] % 10 == 0 and user_message_counts[message.author.id]["message_count"] <= 10:
                    # Tag the user and send a message
                    await message.channel.send(f"{message.author.mention} stop spamming")

        # Check if the user has sent more than 21 messages (mute)
        if user_message_counts[message.author.id]["message_count"] > 50:
            # Check if the user has the 'epic gamer (mod)' role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Allow messages from users with the 'epic gamer (mod)' role
                pass
            else:
                # Give the user the "naughty gamer" role
                naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer")
                await message.author.add_roles(naughty_gamer_role)
                # Send a message to notify the user
                await message.channel.send(f"{message.author.mention} MUTED!")

                # Wait for one minute
                await asyncio.sleep(60)

                # Remove the "naughty gamer" role from the user
                await message.author.remove_roles(naughty_gamer_role)
                # Send a message to notify the user
                await message.channel.send(f"{message.author.mention} Your mute has been lifted but STOP YAPPING")
            
        # Check if the user has sent more than 20 messages (GIF)
        if user_message_counts[message.author.id]["message_count"] > 20:
            # Check if the user has the 'epic gamer (mod)' role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Allow messages from users with the 'epic gamer (mod)' role
                pass
            else:
                yapping_gifs = ["https://tenor.com/view/yapping-yapping-level-today-catastrophic-yapanese-gif-13513208407930173397",
                                "https://tenor.com/view/the-rock-rock-me-explaining-yapping-what-is-bro-yapping-about-gif-4331156902044955863",
                                "https://tenor.com/view/super-mario-bros-wonder-talking-flower-template-mario-wonder-meme-gif-7964213445666430726",
                                "https://tenor.com/view/saving-skylands-savingskylands-you%27ve-been-giffed-gif-7051846494767136386",
                                "https://tenor.com/view/party-smile-yapping-gif-16342222781629643311",
                                "https://tenor.com/view/yapping-gif-3664239514826816233"
                                ]
                random_yapping_gif = random.choice(yapping_gifs)
                await message.channel.send(random_yapping_gif)

        # Check if the user has sent more than 15 messages (yap)
        if user_message_counts[message.author.id]["message_count"] % 15 == 0 and user_message_counts[message.author.id]["message_count"] <= 15:
            # Check if the user has the 'epic gamer (mod)' role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Allow messages from users with the 'epic gamer (mod)' role
                pass
            else:
                # Tag the user and send a message
                await message.channel.send(f"{message.author.mention} stop yapping")

# Basic capabilities

        if message.content.lower() == 'basic stuff':
            await message.channel.send(f"ON/OFF switch\n------------\nInfo\n------------\nGPT personas\n------------\nWord replacers\n------------\nPrison\n------------\nModerator\n------------\nReminders\n------------\nStream alert\n------------\nRehab\n------------\nNixann mode\n------------\nGaming queue\n------------\nBlackjack\n------------\nRock Paper Scissors\n------------\nMagic 8 ball\n------------\nKebab\n------------\nWish me luck\n------------\nFlip a coin\n------------\nChangelog\n------------\nThank you\n------------")

# Info

        if message.content.lower().startswith('update battery'): # Because I'm running the script on my old phone lol
            # Check if the user has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Extract the new battery percentage from the message
                new_battery_percentage = int(message.content.lower().split(' ')[-1])

                if not battery_updated:
                    # Calculate the initial remaining battery percentage
                    battery_lifetime = timedelta(hours=21)
                    uptime = datetime.now() - start_time
                    remaining_lifetime = battery_lifetime - uptime
                    original_battery_percentage = (remaining_lifetime / battery_lifetime) * 100

                # Calculate the difference between the new battery percentage and the calculated one
                difference = original_battery_percentage - new_battery_percentage

                # Update the battery status
                battery_updated = True

                # Notify that the battery percentage is updated
                await message.channel.send(f"Battery percentage updated to {new_battery_percentage}%")

        if message.content.lower() == 'info':
            # Check if the user has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Calculate uptime
                uptime = datetime.now() - start_time

                battery_lifetime = timedelta(hours=21)
                remaining_lifetime = battery_lifetime - uptime
                remaining_percentage = (remaining_lifetime / battery_lifetime) * 100 -5

                adjusted_remaining_percentage = remaining_percentage - difference
                battery_info = max(0, adjusted_remaining_percentage) if battery_updated else remaining_percentage

                if battery_info <= 10:
                    warning_message = "⚠️ Battery level is critically low! ⚠️"
                    await message.channel.send(warning_message)

                # Format uptime
                uptime_str = str(uptime).split('.')[0]  # Remove milliseconds

                # Calculate approximate operating time
                approximate_operating_time = battery_lifetime - uptime / 21 

                # Format approximate operating time
                operating_time = approximate_operating_time * battery_info / 100

                # Calculate the approximate time when the next charge will be needed
                next_charge_time = datetime.now() + operating_time

                # Format next charge time
                next_charge_time_str = next_charge_time.strftime("%I:%M %p")

                # Get active modes
                active_modes = [mode.replace('_mode', '').replace('_active', '') for mode, value in globals().items() if value and (mode.endswith("_mode") or mode.endswith("_active"))]

                # Get naughty gamers
                naught_gamers_list = ", ".join([member.name for member in message.guild.members if discord.utils.get(member.roles, name="Naughty Gamer")])

                # Compose info message
                info_message = f"**Uptime:** {uptime_str}\n\n**Next charge at:** {next_charge_time_str}\n\n**Active Modes:** {', '.join(active_modes)}\n\n**Naughty Gamers:** {naught_gamers_list}\n\n**Battery:** {battery_info}"

                # Send info message
                await message.channel.send(info_message)

# Changelog

        # Changelog feature
        changelog = {
            "v2": "Chatbot",
            "v2.5": "text-curie-001 to gpt-3.5-turbo-instruct",
            "v3": "moderator\nadded on/off switch\nadded wish me luck\nadded parrot mode\nadded reminder\nadded blackjack",
            "v3.1": "added Nixann mode\nFrench revolution\nincreased max token from 128 to 512\nimproved reminder",
            "v3.5": "added Kebab\nadded Rehab\nadded Prison\nadded gaming queue\nhotfixes",
            "v3.8": "added bomboclat mode\nadded DM limiter\nadded repetitive response limited",
            "v3.9": "added uwu mode\nadded borken mode\nadded word replacers\nadded GIF reactions",
            "v4": "added uptime info\nadded flip a coin\nadded a lot more GIF reactions and word replacers\nadded russian mide\nimproved gpt prompts",
            "v5": "added casual mode\nimproved GIF reaction logic\nadded low battery warning\nadded rock paper scissors\nadded magic 8 ball",
            "v6": "maybe check heaven?\nadded yapping and spamming protection\nadded changelog",
            "v6.1": "added #FREETAYK\nadded 'Next charge' to 'info'\nadded AUTOMATED stream alert\nGG\nadded out on bail GIFs\nadded Saul Goodman mode\n",
            "v6.9": "currently in development",
            "hotfix": "\nv6.2.1\nadded timestamp for stream stuff in console\n"
        }

        # Handle version details request
        if message.content.lower() == 'changelog':
            # Prompt user to choose a version
            await message.channel.send("v2, v2.5, v3, v3.1, v3.5, v3.8, v3.9, v4, v5, v6, v6.1, v6.9, hotfix\n\nWhich version would you like to know more about?\nPlease use 'version [version number]' format.")
            
            def check(m):
                return m.author == message.author and m.content.lower().startswith('v') and m.content.lower()[1:] in changelog
            
            try:
                # Wait for user response
                response = await bot.wait_for('message', check=check, timeout=30)
                version_number = response.content.lower()[1:]  # Get the version number from the user's response
                version_details = changelog[version_number]
                await message.channel.send(f"Version {version_number}:\n{version_details}")
            except asyncio.TimeoutError:
                await message.channel.send("DM P_P if you have any suggestions")
            except KeyError:
                await message.channel.send("Version not found in the changelog. Please use 'v[version number]' format.")
        elif message.content.lower().startswith('version'):
            version_number = message.content.split()[1]  # Get the version number from the message
            if version_number in changelog:
                version_details = changelog[version_number]
                await message.channel.send(f"Version {version_number}:\n{version_details}")
            else:
                await message.channel.send("Version not found in the changelog.")

# Battery warning

        if not battery_warning:

            uptime = datetime.now() - start_time

            battery_lifetime = timedelta(hours=21)
            remaining_lifetime = battery_lifetime - uptime
            remaining_percentage = (remaining_lifetime / battery_lifetime) * 100 -5

            adjusted_remaining_percentage = remaining_percentage - difference
            battery_info = max(0, adjusted_remaining_percentage) if battery_updated else remaining_percentage

            if battery_info <= 10:
                warning_message = "⚠️ Battery level is critically low! ⚠️"
                await message.channel.send(warning_message)
                battery_warning = True

# Rehab, for the casino text channel

        # Check for "rehab" command
        if message.content.lower() == 'rehab':
            member = message.author
            rehab_role = discord.utils.get(message.guild.roles, name="gambling addict rehabilitation program")
            if rehab_role:
                # Add the role to the member
                await member.add_roles(rehab_role)

                # Funny messages wishing well for rehab
                funny_messages = [
                    "Remember, chips are for eating, not for betting!",
                    "Rehab is just a long break from winning!",
                    "You're one step closer to becoming a billionaire... by not gambling!",
                    "Don't worry, your bank account will thank you later!",
                    "You're now officially in the 'No Bets' club!",
                    "Life is a gamble, but rehab is a sure bet!",
                    "Just think of it as a vacation from the casino!",
                    "Welcome to the world of financial stability!",
                    "It's not goodbye to gambling, it's see you later!"
                ]

                # Send a message announcing rehab with a random funny message
                await message.channel.send(random.choice(funny_messages).format(member=member))

                # Wait for 1 hour
                await asyncio.sleep(3600)

                # Remove the role after 1 hour
                await member.remove_roles(rehab_role)

                # Funny messages announcing the end of rehab
                funny_messages_end = [
                    "Welcome back from rehab, {member.mention}! Hope you've enjoyed your time away from the tables!",
                    "Rehab time's over, {member.mention}! It's time to roll the dice again!",
                    "Congratulations, {member.mention}! You've successfully completed your rehab journey!",
                    "You're out of rehab, {member.mention}! Time to make some responsible financial decisions!",
                    "Rehabilitation complete, {member.mention}! Remember, life is the ultimate game!",
                    "The chips are down, {member.mention}! You're back in action!",
                    "Back from rehab, {member.mention}! Let's hope you're not feeling too lucky!",
                    "Time to leave the rehab nest, {member.mention}! Fly high and gamble responsibly!",
                    "Rehab no more, {member.mention}! Your future bank account thanks you!",
                    "You've graduated from rehab, {member.mention}! Now go and conquer the world!"
                ]

                # Send a message announcing the end of rehab
                await message.channel.send(random.choice(funny_messages_end).format(member=member))
            else:
                await message.channel.send("The 'Gambling Addict Rehabilitation Program' role is not set up.")               

# FREETAY-K

        # Check if the user wants to free someone
        if message.content.lower().startswith('free <@'):
            # Check if the author has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Check if the user wants to free a specific user
                user_matches = re.finditer(r'<@!?(\d+)>', message.content)
                for user_match in user_matches:
                    user_id = int(user_match.group(1))
                    member = message.guild.get_member(user_id)
                    if member:
                        # Remove the "Naughty Gamer" role from the user
                        naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer")
                        if naughty_gamer_role in member.roles:
                            await member.remove_roles(naughty_gamer_role)
                            await message.channel.send(f"{member.mention} enjoy freedom!")
                        else:
                            await message.channel.send(f"{member.mention} is already free!")
            # Check if the user wants to free all sentenced users
            elif message.content == 'free all':
                for member in message.guild.members:
                    naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer")
                    if naughty_gamer_role in member.roles:
                        await member.remove_roles(naughty_gamer_role)
                        await message.channel.send(f"{member.mention} enjoy freedom!")
            else:
                await message.channel.send("Nuh uh")

# Stream nightmare stuff, for Twitch streamer notifications

        if message.content.lower() == 'stream stop':
            # Check if the author has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                await message.channel.send("❌Stream announcement won't be sent❌")
                stream_stop_active = True

        if message.content.lower() == 'stream go':
            # Check if the author has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                await message.channel.send("✅Stream announcement will be sent✅")
                stream_stop_active = False

# Prison 1/2

        # Check for "sentence to prison" command
        if "sentence" in message.content.lower() and "to prison" in message.content.lower():
            # Check if the author has the "epic gamer (mod)" role
            if any(role.name == 'epic gamer (mod)' for role in message.author.roles):
                # Extract the duration from the message
                duration_match = re.search(r'for (\d+|life)?\s*(year|years|month|months|life)', message.content.lower())
                if duration_match:
                    duration = int(duration_match.group(1)) if duration_match.group(1) else 1  # Default to 1 if no number provided
                    time_unit = duration_match.group(2)
                    if time_unit == 'month' or time_unit == 'months':
                        timer_seconds = duration * 60  # Convert months to minutes
                    elif time_unit == 'year' or time_unit == 'years':
                        timer_seconds = duration * 600  # Convert years to minutes
                    else:
                        timer_seconds = 36000  # Default to 10 hour for life sentence

                    # Find and sentence the mentioned users to prison
                    user_matches = re.finditer(r'<@!?(\d+)>', message.content)
                    for user_match in user_matches:
                        user_id = int(user_match.group(1))
                        member = message.guild.get_member(user_id)
                        if member:
                            # Give the "Naughty Gamer" role to the user
                            naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer")
                            if naughty_gamer_role:
                                await member.add_roles(naughty_gamer_role)
                                
                                # Add user to the sentenced list
                                release_time = datetime.now() + timedelta(seconds=timer_seconds)
                                sentenced_users.append((member, release_time))

                                # Send a message announcing the sentence
                                await message.channel.send(f"{member.mention} has been sentenced to prison!")

                    # Start timer for the specified duration
                    await asyncio.sleep(timer_seconds)

                    # Check if any users need to be released from prison (in case multiple users were sentenced)
                    now = datetime.now()
                    for sentenced_user_info in sentenced_users[:]:  # Copy the list to iterate over
                        user, release_time = sentenced_user_info
                        if now >= release_time:
                            # Remove the "Naughty Gamer" role
                            naughty_gamer_role = discord.utils.get(user.guild.roles, name="Naughty Gamer")
                            if naughty_gamer_role in user.roles:
                                await user.remove_roles(naughty_gamer_role)
                                await message.channel.send(f"{user.mention} has served their time and is back in society!")
                            else:
                                await message.channel.send(f"{user.mention} is out on bail.")
                                regular_bail_gifs = ["https://tenor.com/view/dancing-yg-out-on-bail-song-groovy-jamming-gif-18810970"
                                                     "https://tenor.com/view/fuck-you-yg-out-on-bail-song-middle-finger-fuck-gif-18810893",
                                                     "https://tenor.com/view/money-rain-yg-out-on-bail-song-throwing-money-rich-gif-18810971",
                                                     "https://tenor.com/view/gang-sign-yg-out-on-bail-song-yeah-swag-gif-18810936",
                                                     "https://tenor.com/view/lifting-weights-yg-out-on-bail-song-exercise-workout-gif-18810954"
                                                     "https://tenor.com/view/money-fan-yg-out-on-bail-song-rich-money-gif-18811093",
                                                     "https://tenor.com/view/throwing-cash-yg-out-on-bail-song-throwing-money-money-rain-gif-18810887",
                                                     "https://tenor.com/view/dancing-yg-out-on-bail-song-jamming-joyful-gif-18810891"
                                                     ]

                                rare_bail_gif = "https://tenor.com/view/im-out-on-bail-yg-out-on-bail-song-released-dancing-gif-18810929"
                                # Probability of regular gifs
                                regular_probability = 0.9

                                # Decide which gif to send based on probabilities
                                if random.random() < regular_probability:
                                    # Send a regular gif
                                    random_regular_gif = random.choice(regular_bail_gifs)
                                    await message.channel.send(random_regular_gif)
                                else:
                                    # Send the rare gif
                                    await message.channel.send("✨RARE ANIMATION✨")
                                    await message.channel.send(rare_bail_gif)


                            # Remove the user from the sentenced list
                            sentenced_users.remove(sentenced_user_info)

                    # Send a message if the user is still in the sentenced users list

                else:
                    await message.channel.send("Please specify the duration for the sentence.")
            else:
                await message.channel.send("Nuh uh")

# RPS 1/2

        if message.content.lower() == 'rps' or message.content.lower() == 'rock paper scissors':
            rps_player_id = message.author.id
            await message.channel.send("Starting a game of Rock Paper Scissors!")
            await play_rps(message.channel)

# Moderator

        # Check if the message contains a GIF (starts with "https://tenor.com")
        if message.content.startswith("https://tenor.com"):
            return

        # Check for filtered words
        if any(word in message.content.lower() for word in word_filter):
            # Check if the triggered word is whitelisted
            if any(word in message.content.lower() for word in whitelisted_words):
                return 
        
            current_time = datetime.now()
            user_id = str(message.author.id)

            # Check if the user has triggered the word within the cooldown time
            if user_id in user_last_triggered and current_time - user_last_triggered[user_id] < cooldown_time:
                timeout_duration = timeout_durations[1]  # Use 10 minutes timeout for repeated triggers
            else:
                timeout_duration = timeout_durations[0]

            # Update the last triggered timestamp for the user
            user_last_triggered[user_id] = current_time

            try:
                # Remove the message that triggered the word
                await message.delete()
            except discord.errors.NotFound:
                pass  # Ignore NotFound error if the message is already deleted

            # Get the member to timeout
            member = message.guild.get_member(int(user_id))

            if member:
                # Give "Naughty Gamer" role
                naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer")
                if naughty_gamer_role:
                    await member.add_roles(naughty_gamer_role)

                # Ping the user and send a message in the same channel
                timeout_message = timeout_messages[timeout_durations.index(timeout_duration)]
                await message.channel.send(
                    f"{member.mention}, It appears that you have triggered one of the big no-no words with your message. Stop being naughty, please :)")

                # Timeout the user
                try:
                    await member.send(timeout_message)
                except discord.errors.Forbidden:
                    await message.channel.send(
                        f"Unable to send a timeout message to {member.mention}. They may have DMs disabled. Anyways... {timeout_message}")

                # Wait for the specified timeout duration
                await asyncio.sleep(timeout_duration)

                # Remove the "Naughty Gamer" role after the timeout duration
                await member.remove_roles(naughty_gamer_role)

                await message.channel.send(f"User {member.mention} has gained back their right to talker <:happi:1202300923460980756>")

            else:
                await message.channel.send("Unable to find the user to timeout.")
            return

# OpenAI API funny custom prompts 

        if message.content.lower() == 'disability':
            disability_mode = True
            bomboclat_mode = False
            weeb_mode = False
            haix_mode = False
            brokey_mode = False
            casual_mode = False
            saul_mode = False
            await message.channel.send("HUEAHUEHAUHE")

        if message.content.lower() == 'bigbrain':
            disability_mode = False

        if message.content.lower() == 'bomboclat':
            bomboclat_mode = True
            disability_mode = False
            weeb_mode = False
            haix_mode = False
            brokey_mode = False
            casual_mode = False
            saul_mode = False
            await message.channel.send("BOMBOCLATT!!!")

        if message.content.lower() == 'huihui':
            bomboclat_mode = False    

        if message.content.lower() == 'uwu':
            weeb_mode = True
            disability_mode = False
            bomboclat_mode = False
            haix_mode = False
            brokey_mode = False
            casual_mode = False
            saul_mode = False
            await message.channel.send("UwU")

        if message.content.lower() == 'owo':
            weeb_mode = False   

        if message.content.lower() == 'priviet':
            haix_mode = True
            disability_mode = False
            bomboclat_mode = False
            weeb_mode = False
            brokey_mode = False
            casual_mode = False
            saul_mode = False
            await message.channel.send("Zdravstuite!")

        if message.content.lower() == 'spasibo':
            haix_mode = False 

        if message.content.lower() == 'broki':
            brokey_mode = True
            disability_mode = False
            bomboclat_mode = False
            weeb_mode = False
            haix_mode = False
            casual_mode = False
            saul_mode = False
            await message.channel.send("Henlo!")

        if message.content.lower() == 'fixi':
            brokey_mode = False 

        if message.content.lower() == 'chad':
            casual_mode = True
            disability_mode = False
            bomboclat_mode = False
            weeb_mode = False
            haix_mode = False
            brokey_mode = False
            saul_mode = False
            await message.channel.send("Suh")

        if message.content.lower() == 'yapping':
            casual_mode = False 
            await message.channel.send("What's yappening?")

        if message.content.lower() == 'better call saul':
            saul_mode = True
            casual_mode = False
            disability_mode = False
            bomboclat_mode = False
            weeb_mode = False
            haix_mode = False
            brokey_mode = False
            await message.channel.send("S'all Good, Man.")
            regular_saul_gifs = ["https://tenor.com/view/saul-goodman-saul-goodman-better-call-saul-jimmy-gif-23761375",
                                 "https://tenor.com/view/better-call-saul-bob-odenkirk-saul-goodman-usa-united-states-of-america-gif-5322556",
                                 "https://tenor.com/view/saul-goodman-better-call-saul-breaking-bead-walter-white-gif-6174761702766811539",
                                 "https://tenor.com/view/better-call-saul-saul-goodman-jmm-hands-together-tongue-slip-gif-18582500",
                                 "https://tenor.com/view/better-call-saul-remember-the-winner-takes-it-all-bob-odenkirk-saul-goodman-jimmy-mcgill-gif-26579149",
                                 "https://tenor.com/view/better-call-saul-saul-goodman-episode5-gif-25985868",
                                 "https://tenor.com/view/better-call-saul-saul-goodman-intro-theme-bob-odenkirk-gif-18610528"
                                 ]
                
            rare_saul_gif = "https://tenor.com/view/afham-saul-goodman-better-call-saul-bob-odenkirk-jimmy-mcgill-gif-25559831"
            # Probability of regular gifs
            regular_probability = 0.9

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_saul_gif = random.choice(regular_saul_gifs)
                await message.channel.send(random_saul_gif)
            else:
                # Send the rare gif
                await message.channel.send("✨RARE ANIMATION✨")
                await message.channel.send(rare_saul_gif)

        if message.content.lower() == 'saul goodman':
            saul_mode = False 
            await message.channel.send("Say Nothing, You Understand? Get A Lawyer!")

        # Check for Beebo or B-b0
        if 'B-b0' in message.content or 'Beebo' in message.content:
            user_input = message.content.replace('B-b0', '').replace('Beebo', '').strip()

            # Check if disability mode is enabled
            if disability_mode:
                user_input += "- answer in hungarian please"

            # Check if bomboclat mode is enabled
            if bomboclat_mode:
                user_input += "- answer to this if you were roleplaying a jamaican rastaman"

            # Check if weeb mode is enabled
            if weeb_mode:
                user_input += "" # Trust me you don't want to know this one lol

            # Check if russian mode is enabled
            if haix_mode:
                user_input += "- answer to this if you were roleplaying funny stereotipical russian accent"

            # Check if broken mode is enabled
            if brokey_mode:
                user_input += "- answer to this if you were roleplaying that you are a robot and your chip and circuits have funny malfunctions causing you to glitch and give crazy and weird completely unrelated answers without letting us know that you detected the glitch"     

            # Check if casual mode is enabled
            if casual_mode:
                user_input += "- answer to this short and casual, use emojis instead of doing physical activity, no hashtags"

            # Check if saul mode is enabled
            if saul_mode:
                user_input += "- answer to this if you were roleplaying Saul Goodman, a lawyer who's actually a criminal but gives you professional opinion and advice, focusing on lawsuits and everything money related. His main focus is getting money and he can also help with some loopholes and shortcuts in the law. If there's something illegal he will always warn you about the potential punishments and dangers" # I hope I won't get in trouble for this one lmfao

            # Use the default prompt without the project context
            prompt = f'{user_input}\nB-b0: '
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                stop=None,
                temperature=0.21,
            )

            await message.channel.send(response['choices'][0]['message']['content'])

# Parrot mode

        # Define the keywords to trigger the response
        keywords = ["szia", "real", "gaming", "yippie", "<:happi:1202300923460980756>", ":3", "xd"]

        # Check if any of the keywords are present in the message
        keyword_present = any(keyword in message.content.lower() for keyword in keywords)

        # If no keyword is found, return without processing
        if not keyword_present:
            return
        # Continue with parrot mode or other processing here
        for keyword in keywords:
            if keyword in message.content.lower():
                response_message = f"{keyword}"
                await message.channel.send(response_message)

# Define a function to generate a random time interval between 1 minute and 10 hours
def generate_random_interval():
    return random.randint(1 * 60, 10 * 60 * 60)

# Uptime charge reminder

async def check_uptime():
    start_time = datetime.now()
    while True:
        # Calculate uptime
        uptime = datetime.now() - start_time

        # Check if uptime is 19 hours
        if uptime >= timedelta(hours=19):
            # Send a warning message
            warning_message = "Warning: System uptime has reached 19 hours. Please consider charging the battery or risk imminent system failure! Thenk <:happi:1202300923460980756>"
            await bot.get_channel().send(warning_message) # Battery Warning message channel ID goes in that bracket
            # Reset the start_time to avoid sending multiple messages
            start_time = datetime.now()
        
        # Check every hour
        await asyncio.sleep(360)  # 3600 seconds = 1 hour

# Stream announcement, brought to you by Tintin

async def check_stream():  # Az hogy async szard le, annyi hogy több dolog mehet egyszerre
    global streaming_yes, stream_checked, stream_stop_active
    channel_id = 123 # A discord csatorna id ahova akarsz iratni, gondolom tudod hogy kell - Channel ID for announcement
    twitch_username = "nustercs"  # ezt pontosan nem tom hogy kell, milyen capitalizációval - Twitch user

    while True:
        try:
            await asyncio.sleep(5)
            contents = requests.get('https://www.twitch.tv/' +twitch_username).content.decode('utf-8')
            # Extract the description using regular expressions
            description_pattern = r'description" content="(.*?)"\/>'
            description_match = re.search(description_pattern, contents)
            if description_match:
                stream_title = description_match.group(1)

            # LIVE
            if 'isLiveBroadcast' in contents:
                stream_checked = True

                stream_url = f"https://twitch.tv/{twitch_username}"

                # Construct the message to send
                stream_emoji = ["<:happi:1202300923460980756>", "<:catDespair:1204871470023442512>", "<:alright:1213523880694513774>", 
                                "<:YOOO:1204875222243610624>" ,"💀" ,"<:edgebug:1222332990886121502>" ,"<:LETSGO:1204109646835617802>" 
                                ,"<:nusterSmile:1207842531556196402>" ,"<:ducky:1204875325884858419>" ,"<:uwupink:1207757406507896852>" 
                                ,"<:actually:1217798394441896016>" ,"<:4k:1204107083343994930>" ,"<:ducc:1224368291884044419>" 
                                ,"<:HOOO:1204078103278649436>" ,"<:catsit:1204875394789023765>" ,"<:huhhh:1204871428458025022>" 
                                ,"<:holyskull:1205495916950327296>"
                                ,"<:rizz2:1204614534673866872>" ,"<:prayge:1204625161559744522>" ,"<:gigachad:1204625346423689298>" 
                                ,"<:catCute:1204624941001998346>" ,"<:catHuh:1204625456184299521>" ,"<:Clueless:1204110114781528084>" 
                                ,"<:NAHHH:1204614480601022464>" ,"<:Jojo:1204898145146769509>" ,"<:HUH:1204109317888934000>" 
                                ,"<:heart:1204626406601007155>" ]
                random_stream_emoji = random.choice(stream_emoji)
                announcement_message = f"@everyone <:twitch:1237004331014688849> LIVE! <:twitch:1237004331014688849>\n\n{stream_title} {random_stream_emoji}\n\n{stream_url}"
                channel = bot.get_channel(channel_id)

                if not streaming_yes:
                    print(f"{datetime.now()} 🔴 Stream started: {stream_title}")
                    # 10 perces delay, másodperc, valszeg nem pont 10 perc lesz a wait miatt de az mindegy
                    await asyncio.sleep(600)
                    if not stream_stop_active:
                        print(f"Stream anouncement sent: {stream_title}")
                        await channel.send(announcement_message)

                        stream_stop_active = True
                        streaming_yes = True
                        stream_checked = False

            else:
                streaming_yes = False

                if not stream_checked:
                    print("Stream is offline")
                    stream_checked = True
                    await bot.get_channel(1200515971878752257).send(f"https://twitch.tv/nustercs")
                    await bot.get_channel(1200515971878752257).send("Don't forget to 'stream go' after stream is offline")
                    

        except Exception as e:
            print("Error:", e)

        # Milyen időközönként nézze meg hogy live-e a stream
        await asyncio.sleep(30)  # Másodperc

# Reminder 2/2

# Updated handle_reminder function
async def handle_reminder(message):
    # Use regular expression to find "remind me" followed by a number and unit
    match = re.search(r'remind me (\d+) ?([mMhH]) ?(.+)?', message.content.lower())

    if match:
        duration = int(match.group(1))
        unit = match.group(2).lower()
        context = match.group(3).strip() if match.group(3) else None

        # Convert to minutes if the unit is 'm' or 'min'
        if unit == 'm':
            duration *= 60

        if unit == 'h':
            duration *= 3600

        # Send a confirmation message quoting the entire "remind me" message
        confirmation_message = f"{message.author.mention}, Gotchu, I'll remind you! Here's your reminder:\n\n> {context}"
        await message.channel.send(confirmation_message)

        # Set timer for the user without waiting in the text channel
        asyncio.create_task(set_timer(str(message.author.id), duration, context))
    else:
        # If the "remind me" pattern is not found, notify the user
        await message.channel.send("Please use the format 'remind me [duration] [m/h] [message]'.")

# Function to set timer for the reminder
async def set_timer(user_id, duration, context):
    # Sleep for the specified duration
    await asyncio.sleep(duration)

    # Get the user based on user_id
    user = bot.get_user(int(user_id))

    if user:
        # Send a DM to the user when the timer is up
        dm_channel = await user.create_dm()
        await dm_channel.send(f"Reminder: {context}")
    else:
        print(f"Unable to find user with ID: {user_id}")

# Remindus 2/2

# Updated handle_reminder function
async def handle_remindus(message):
    # Use regular expression to find "remind me" followed by a number and unit
    match = re.search(r'remind us (\d+) ?([mMhH]) ?(.+)?', message.content.lower())

    if match:
        duration = int(match.group(1))
        unit = match.group(2).lower()
        context = match.group(3).strip() if match.group(3) else None

        # Convert to minutes if the unit is 'm' or 'min'
        if unit == 'm':
            duration *= 60

        if unit == 'h':
            duration *= 3600

        # Send a confirmation message quoting the entire "remind me" message
        confirmation_message = f"{message.author.mention}, Gotchu, I'll remind yall! Here's the reminder:\n\n> {context}"
        await message.channel.send(confirmation_message)

        # Set timer for the user without waiting in the text channel
        asyncio.create_task(set_timerus(message.channel, duration, context))
    else:
        # If the "remind me" pattern is not found, notify the user
        await message.channel.send("Please use the format 'remind us [duration] [m/h] [message]'.")

# Function to set timer for the reminder
async def set_timerus(channel, duration, context):
    # Sleep for the specified duration
    await asyncio.sleep(duration)

    await channel.send(f"Reminder: {context}")

        # Continue with other processing or commands
    
# Prison 2/2
    
async def check_sentences():
    while True:
        # Check if any users need to be released from prison
        now = datetime.now()
        for sentenced_user_info in sentenced_users[:]:  # Copy the list to iterate over
            user, release_time = sentenced_user_info
            if now >= release_time:
                # Remove the "Naughty Gamer" role
                naughty_gamer_role = discord.utils.get(user.guild.roles, name="Naughty Gamer")
                if naughty_gamer_role:
                    await user.remove_roles(naughty_gamer_role)

                # Remove the user from the sentenced list
                sentenced_users.remove(sentenced_user_info)

                print(f"{user} has been released from prison.")

        await asyncio.sleep(60)  # Check every 60 seconds

# RPS 2/2 - Rock-paper-scissors game logic
async def play_rps(channel):
    global rps_player_id
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)
    await asyncio.sleep(1)
    await channel.send("🪨 Rock...")
    await asyncio.sleep(1)
    await channel.send("📄 Paper...")
    await asyncio.sleep(1)
    await channel.send("✂️ Scissors...")
    await asyncio.sleep(1)
    await channel.send("SHOOT!\n\n(type your choice)")

    def check(message):
        return message.author.id == rps_player_id and message.content.lower() in choices

    try:
        user_choice_message = await bot.wait_for('message', timeout=20.0, check=check)
        user_choice = user_choice_message.content.lower()

        # Determine which emoji corresponds to the bot's choice
        bot_choice_emoji = ""
        if bot_choice == "rock":
            bot_choice_emoji = "🪨"
        elif bot_choice == "paper":
            bot_choice_emoji = "📄"
        elif bot_choice == "scissors":
            bot_choice_emoji = "✂️"

        if bot_choice == user_choice:
            await channel.send("It's a tie!")
        elif (bot_choice == "rock" and user_choice == "scissors") or \
             (bot_choice == "paper" and user_choice == "rock") or \
             (bot_choice == "scissors" and user_choice == "paper"):
            await channel.send(f"I won hehe! I chose {bot_choice} {bot_choice_emoji}")
        else:
            await channel.send(f"{user_choice_message.author.mention} won GG! I chose {bot_choice} {bot_choice_emoji}")
    except asyncio.TimeoutError:
        await channel.send("You took too long to respond. Game over!")
    finally:
        # Reset the player ID after the game is over
        rps_player_id = None

# Blackjack 2/2

# Blackjack Command
@bot.command(name="blackjack")
async def blackjack(ctx):
    global blackjack_active, blackjack_games
    if not blackjack_active:
        blackjack_games[ctx.author.id] = {"user_cards": [], "dealer_cards": [], "reveal_dealer": False}
        await ctx.send("Blackjack is now active! Type 'play' to start a game.")
        blackjack_active = True
    else:
        await ctx.send("Blackjack is already active! Type 'play' to start a new game.")

async def play_blackjack(message):
    global blackjack_games
    user_id = message.author.id

    def deal_card():
        return random.randint(2, 11)

    def deal_initial_cards():
        return [deal_card(), deal_card()]

    def sum_cards(cards):
        total = sum(cards)
        if 11 in cards and total > 21:
            cards.remove(11)
            cards.append(1)
        return sum(cards)

    async def display_cards():
        user_sum = sum_cards(blackjack_games[user_id]["user_cards"])
        dealer_sum = sum_cards(blackjack_games[user_id]["dealer_cards"])

        user_cards_str = f"{message.author.mention}'s cards:\n{blackjack_games[user_id]['user_cards']} ({user_sum})"

        if blackjack_games[user_id]["reveal_dealer"]:
            dealer_cards_str = f"Dealer's cards:\n{blackjack_games[user_id]['dealer_cards']} ({dealer_sum})"
        else:
            dealer_cards_str = f"Dealer's cards:\n[{blackjack_games[user_id]['dealer_cards'][0]}, '???'] ({blackjack_games[user_id]['dealer_cards'][0]})"

        message_str = f"{user_cards_str}\n{dealer_cards_str}\n----------------------"

        await message.channel.send(message_str)

    async def get_user_choice():
        await message.channel.send("Do you want to hit or stay? Type 'hit' or 'stay'.")

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.lower() in ["hit", "stay"]

        try:
            user_choice = await bot.wait_for("message", check=check, timeout=30)
            return user_choice.content.lower()
        except asyncio.TimeoutError:
            await message.channel.send("Time's up! The game is over.")
            return "stay"

    # Check if the user already has a game in progress
    if user_id not in blackjack_games:
        blackjack_games[user_id] = {"user_cards": deal_initial_cards(), "dealer_cards": [deal_card(), deal_card()], "reveal_dealer": False}

    await display_cards()

    if sum_cards(blackjack_games[user_id]["user_cards"]) == 21:
        await message.channel.send("You win! You got blackjack!")
        del blackjack_games[user_id]
        return

    while sum_cards(blackjack_games[user_id]["user_cards"]) < 21:
        choice = await get_user_choice()
        if choice == "hit":
            new_card = deal_card()
            blackjack_games[user_id]["user_cards"].append(new_card)
            await display_cards()

            # Check if user busted after the hit
            if sum_cards(blackjack_games[user_id]["user_cards"]) > 21:
                await message.channel.send("Bust! Dealer wins!")
                del blackjack_games[user_id]
                return
        else:
            break

    # Reveal the dealer's hidden card after the player stays
    blackjack_games[user_id]["reveal_dealer"] = True
    await display_cards()

    # Dealer draws until reaching at least 17 but not exceeding 21
    while sum_cards(blackjack_games[user_id]["dealer_cards"]) < 17:
        await asyncio.sleep(1)
        new_dealer_card = deal_card()

        if sum_cards(blackjack_games[user_id]["dealer_cards"] + [new_dealer_card]) > 21:
            new_dealer_card = 21 - sum_cards(blackjack_games[user_id]["dealer_cards"])

        blackjack_games[user_id]["dealer_cards"].append(new_dealer_card)
        await display_cards()

    # Check for user win/loss conditions
    user_sum = sum_cards(blackjack_games[user_id]["user_cards"])
    dealer_sum = sum_cards(blackjack_games[user_id]["dealer_cards"])

    if user_sum > 21:
        await message.channel.send("Dealer wins!")
    elif dealer_sum > 21:
        await message.channel.send("You win! Dealer busted!")
    elif user_sum == dealer_sum:
        await message.channel.send("It's a draw!")
    elif user_sum > dealer_sum:
        await message.channel.send("You win!")
    else:
        await message.channel.send("Dealer wins!")

    # Remove the game from the dictionary after completion
    del blackjack_games[user_id]

# Run the bot
bot.run('Discord API')
