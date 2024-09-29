import discord
from discord.ext import commands
from datetime import datetime, timedelta
import openai
import asyncio
import random
import re
import emoji
from collections import deque
from collections import defaultdict

openai.api_key = "OpenAI API goes here"

intents = discord.Intents.all()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="", intents=intents)

max_tokens = 512 # I found this number good enough

# Define a list of whitelisted words
whitelisted_words = ["whitelisted words go", "here"]

word_filter = ["banned words go", "here"]

allowed_characters = {'é', 'á', 'ö', 'ü', 'ó', 'ű', 'ú', 'ő', 'í'} #customize it for your needs, this is for the ascii chars 

# Add your list of filtered words here
cooldown_time = timedelta(minutes=30)  # Updated cooldown time to 30 minutes
timeout_durations = [60, 600, 3600]
timeout_messages = [
    "You triggered a forbidden word. Timeout: 1 minute.",
    "Repeatedly triggering forbidden words. Timeout: 10 minutes.",
    "Continued violation. Timeout: 1 hour."
]

# A dictionary to store spam counts per user
spam_tracker = defaultdict(list)  # {user_id: [(timestamp, spam_count)]}

user_last_triggered = {}  # Dictionary to store the timestamp of the last trigger for each user

dm_responses_count = {}

sentenced_users = []

# Dictionary to store user message counts
user_message_counts = {}

# Dictionary to store selected channels per user
user_channel_selection = {}

# Initialize a deque to store the user IDs
user_id_history = deque(maxlen=10)

# List to store users who want to join the gaming session
gaming_players = []
triggered = False

is_bot_active = True  # Flag to indicate whether the bot is active
blackjack_active = False  # Flag to indicate whether the blackjack feature is active

blackjack_games = {}

rps_player_id = None

cap_mode = False

specialchars_active = False

bomboclat_mode = False
casual_mode = True


# Set the cooldown time to 10 minutes (600 seconds)
cooldown_time_fr = 600
cooldown_time_crazy = 6000  

# Initialize last_triggered_time_fr as None initially
last_triggered_time_fr = None
last_triggered_time_crazy = None

# Bot's uptime
start_time = datetime.now()

battery_updated = False
original_battery_percentage = None  # Assume full battery at start
remaining_percentage = None  # Initialize to None
difference = 0

battery_warning = False

# Initialize a counter for deleted spam messages
spam_counter = 0

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}')

# Start the uptime check coroutine
    bot.loop.create_task(check_uptime())

@bot.event
async def on_message(message):
    global is_bot_active, start_time, battery_warning, battery_updated, original_battery_percentage, remaining_percentage, difference, blackjack_active, specialchars_active, last_triggered_time_fr, last_triggered_time_crazy, triggered, bomboclat_mode, casual_mode, rps_player_id, cap_mode, spam_counter

    if message.author.bot:
        return

    # Check if enough time has passed since the last trigger
    current_time = datetime.now()

    print(f'{message.author.name}#{message.author.discriminator}: {message.content}')

    await handle_message(message)

# On/Off
    
    # Check for shut down command
    if message.content.lower() == 'shut down':
        # Check if the user has the "epic gamer (mod)" role
        if message.author.guild_permissions.administrator: 
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
            await message.channel.send(f"{random_bye_phrase}") # I'm using a custom emoji here

            # Bot stops responding
            is_bot_active = False
            blackjack_active = False  # Deactivate blackjack when bot is shut down
        else:
            await message.channel.send("Nuh uh")

    # Check for wakey wakey command
    elif message.content.lower() == 'wakey wakey':
        # Check if the user has the "epic gamer (mod)" role
        if message.author.guild_permissions.administrator:
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
            await message.channel.send(f"{random_hai_phrase}") # custom emoji here too
            is_bot_active = True  # Set the flag to True to resume normal operations
            blackjack_active = False
        else:
            await message.channel.send("I sleep")

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
                if dm_responses_count[author_id] > 9:
                    await message.channel.send("You have reached the maximum limit for DM responses.")
                    return

# Naughty Gamer role stuff

        # Command to scan for 'Naughty Gamer' roles in the server where the message was sent
        if message.content.lower() == 'scan naughty gamer role':
            if message.author.guild_permissions.administrator:
                guild = message.guild  # Get the guild (server) where the message was sent
                naughty_gamer_role = discord.utils.get(guild.roles, name="Naughty Gamer")

                if naughty_gamer_role:
                    await message.channel.send(f"Found 'Naughty Gamer' role in server: {guild.name} (ID: {guild.id})")
                else:
                    await message.channel.send(f"No 'Naughty Gamer' role found in server: {guild.name} (ID: {guild.id})")
            else:
                await message.channel.send("Nuh uh")

        # Command to create the "Naughty Gamer" role in the server where the message was sent
        if message.content.lower() == "create naughty gamer role":
            if message.author.guild_permissions.administrator:
                guild = message.guild  # Get the guild (server) where the message was sent
                
                # Check if the role already exists in this guild
                existing_role = discord.utils.get(guild.roles, name="Naughty Gamer")
                if existing_role:
                    await message.channel.send(f"'Naughty Gamer' role already exists in {guild.name}.")
                    return

                # Create the "Naughty Gamer" role with black color (using RGB)
                black_color = discord.Color.from_rgb(0, 0, 0)
                naughty_gamer_role = await guild.create_role(
                    name="Naughty Gamer",
                    color=black_color,
                    reason="Create 'Naughty Gamer' role with restrictions."
                )

                # Loop through all text channels and deny the SEND_MESSAGES permission for the new role
                for channel in guild.text_channels:
                    await channel.set_permissions(naughty_gamer_role, send_messages=False)

                await message.channel.send(f"'Naughty Gamer' role has been created in {guild.name} and users with the role are now restricted from sending messages.")
            else:
                await message.channel.send("Nuh uh")

# Spam

        # List of spam message patterns
        spam_patterns = [
            re.compile(r"spore\s+has\s+officially\s+partnered\s+with\s+mode", re.IGNORECASE),
            re.compile(r"we\s+have\s+collaborated\s+with\s+juice\s+finance", re.IGNORECASE),
            re.compile(r"we\s+have\s+collaborated\s+with\s+opensea\s+on\s+a\s+new\s+free\s+mint", re.IGNORECASE),
            re.compile(r"we\s+are\s+thrilled\s+to\s+announce\s+that\s+we\s+have\s+collaborated\s+with\s+openseapro", re.IGNORECASE),
            re.compile(r"we\s+have\s+collaborated\s+with\s+bonk\s+network", re.IGNORECASE),
            re.compile(r"we\s+are\s+thrilled\s+to\s+announce\s+that\s+our\s+community\s+has\s+been\s+awarded\s+an\s+allocation\s+in\s+the\s+orderly\s+network", re.IGNORECASE),
            re.compile(r"get\s+your\s+free\s+tokens\s+at", re.IGNORECASE),
            re.compile(r"\+\s+nitro\s+giveaway", re.IGNORECASE),
            re.compile(r"\&\s+teen\s+content", re.IGNORECASE), 
            re.compile(r"you\s+still\s+think\s+polybot\s+is", re.IGNORECASE),
            re.compile(r"apps-juice\.com", re.IGNORECASE),
            re.compile(r"1juice-finance\.com", re.IGNORECASE),
            re.compile(r"\$order", re.IGNORECASE),
            re.compile(r"live\s+on\s+superform", re.IGNORECASE),
            re.compile(r"arbitruns\.net", re.IGNORECASE),
            re.compile(r"etherfi", re.IGNORECASE),
            
            
        ]

        # Check if the message contains any spam pattern
        for pattern in spam_patterns:
            if re.search(pattern, message.content.lower()):
                await message.delete()
                spam_counter += 1
                break

        if message.content.lower() == 'spam tracker':
            await message.channel.send(spam_tracker)

# No making bot say someting times fu - aka repetitive bot response prevention

        # Check for abusive message pattern
        content_lower = message.content.lower()

        if re.search(r"\b(?:say|spell|write|type)\b.*\b(?:time(?:s)?|backward(?:s)?)\b", content_lower):
            # Send a response to discourage abuse
            await message.channel.send("https://tenor.com/view/no-i-dont-think-i-will-captain-america-old-capt-gif-17162888")
            return
        
# Word replacer

        if message.content.lower() == 'capping':
            cap_mode = True

        if message.content.lower() == 'nocap':
            cap_mode = False

        if "cap" in content_lower:
            # Check if the message contains just "cap"
            if content_lower.strip() == "cap":
                await message.channel.send("🧢")

            # Check if the message has "no cap"
            if content_lower.strip() == "no cap":
                await message.channel.send("🚫🧢")
            else:
                if cap_mode:
                    match = re.search(r'\b(\w*cap\w*)\b', message.content.lower())
                    if match:
                        word = match.group(1)
                        # Replace "cap" with "C A P" and capitalize each letter
                        replaced_word = word.replace("cap", "C A P")
                        # Send the modified word with the cap emoji
                        await message.channel.send(replaced_word.strip() + " 🧢")
                        
        # Check for other specific messages
        if content_lower == "cool":
            
            await message.channel.send("😎")
        
        if content_lower == "ok":
           
            await message.channel.send("👌")

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
            await message.channel.send(random_wish_phrase)

# Gaming queue - for 5 player lobby

        content_lower = message.content.lower()
        
        if "who is ready for gaming" in content_lower:
            # Check if the author has the "epic gamer (mod)" role
            if message.author.guild_permissions.administrator: # custom role
                await message.channel.send("Please send 'me' in the chat")
                triggered = True

        if triggered:
            if re.search(r'\bme\b', content_lower, re.IGNORECASE):
                if message.author in gaming_players:
                    await message.channel.send("You're already on the gaming list!")
                else:
                    gaming_players.append(message.author)
                    await message.channel.send(f"{message.author.mention} gotchu gamer!")

            if "the gaming squad" in content_lower:
                # Check if the author has the "epic gamer (mod)" role
                if message.author.guild_permissions.administrator: # custom role
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

            if "show gaming list" in content_lower:
                # Check if the author has the "epic gamer (mod)" role
                if message.author.guild_permissions.administrator: # custom role
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
            if message.author.guild_permissions.administrator: # custom role
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
                    await message.channel.send(f"{message.author.mention} English please!")
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

# Flip a coin

        if message.content.lower() == 'flip a coin':
            coin = random.choice(['Heads!', 'Tails!']) # oh yea these are some custom server emojis so you might wanna change it
            await message.channel.send("The coin landed on...")
            await asyncio.sleep(2)
            await message.channel.send(coin)

# Welcome
        
        # Check for the "thank you" 
        if 'thank you' in message.content.lower() or 'thanks' in message.content.lower():
            # Execute the kebab
            response_message = "you are welcome" # custom emoji used here
            await message.channel.send(response_message)

# Kebab
   
        # Check for the "kebab" 
        if re.search(r'\bkebab\b', message.content, re.IGNORECASE):
            # Execute the kebab
            response_message = "<:stuffed_flatbread:1219338686622072882>"
            await message.channel.send(response_message)

# GIF reactions

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
            regular_probability = 0.99

            # Decide which gif to send based on probabilities
            if random.random() < regular_probability:
                # Send a regular gif
                random_regular_gif = random.choice(regular_sheesh_gifs)
                gif_probability = 0.3
                if random.random() < gif_probability:
                    await message.channel.send(random_regular_gif)
            else:
                # Send the rare gif
                gif_probability = 0.3
                if random.random() < gif_probability:
                    await message.channel.send("✨RARE ANIMATION✨")
                    await message.channel.send(rare_sheesh_gif)

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


        # Check for the "hilfe" 
        if message.content.lower() == 'hilfe':
            await message.channel.send("https://tenor.com/view/wolf-of-wallstreet-hilfe-leonardo-di-caprio-jonah-hill-brauche-hilfe-gif-12163807")

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

# List servers
        
        if message.content.lower() == 'list servers':
            if message.author.guild_permissions.administrator:
                guilds = bot.guilds
                response = "The bot is currently in the following servers:\n"
                for guild in guilds:
                    response += f"{guild.name} (ID: {guild.id})\n"
                await message.channel.send(response)
            else:
                await message.channel.send("Nuh uh")

        # List text channels in a specific server
        elif message.content.lower().endswith('channels'):
            if message.author.guild_permissions.administrator:
                try:
                    guild_id = int(message.content.split()[0])
                    guild = bot.get_guild(guild_id)
                    if guild:
                        response = f"Text channels in '{guild.name}':\n"
                        for idx, channel in enumerate(guild.text_channels, start=1):
                            response += f"{idx}. {channel.name} (ID: {channel.id})\n"
                        await message.channel.send(response)

                        # Store guild ID and text channels list for the user
                        user_channel_selection[message.author.id] = {
                            'guild_id': guild_id,
                            'channels': guild.text_channels
                        }
                    else:
                        await message.channel.send("Guild not found.")
                except ValueError:
                    await message.channel.send("Invalid guild ID.")
            else:
                await message.channel.send("Nuh uh")

        # Select a channel by number
        elif message.author.id in user_channel_selection and message.content.isdigit():
            if message.author.guild_permissions.administrator:
                channel_number = int(message.content) - 1
                user_data = user_channel_selection[message.author.id]
                if 0 <= channel_number < len(user_data['channels']):
                    selected_channel = user_data['channels'][channel_number]
                    await message.channel.send(f"Selected channel: {selected_channel.name}. Type your message to send.")

                    # Update user selection to store the selected channel ID
                    user_data['selected_channel_id'] = selected_channel.id
                else:
                    await message.channel.send("Invalid channel number.")
            else:
                await message.channel.send("Nuh uh")

        # Send the message to the selected channel
        elif message.author.id in user_channel_selection and 'selected_channel_id' in user_channel_selection[message.author.id]:
            if message.author.guild_permissions.administrator:
                user_data = user_channel_selection[message.author.id]
                selected_channel = bot.get_channel(user_data['selected_channel_id'])
                if selected_channel:
                    await selected_channel.send(message.content)
                    await message.channel.send(f"Message sent to {selected_channel.name}.")
                    # Clear the selection after sending the message
                    del user_channel_selection[message.author.id]
            else:
                await message.channel.send("Nuh uh")

        # Leave server
        if message.content.startswith('leave server'):
            if message.author.guild_permissions.administrator:
                # Split the message to get the server ID from the command
                parts = message.content.split()
                if len(parts) < 3:
                    await message.channel.send("Please provide the Server (Guild) ID.")
                    return

                try:
                    # Get the Guild ID from the command
                    guild_id = int(parts[2])
                    guild = bot.get_guild(guild_id)

                    if guild:
                        # Make the bot leave the server
                        await guild.leave()
                        await message.channel.send(f"Bot has left the server: {guild.name}")
                    else:
                        await message.channel.send("Bot is not part of this server or the ID is incorrect.")
                except ValueError:
                    await message.channel.send("Invalid Guild ID. Please enter a valid number.")
                except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")
            else:
                await message.channel.send("Nuh uh, you don't have permission to do that.")



# Basic capabilities

        if message.content.lower() == 'basic stuff':
            await message.channel.send(f"ON/OFF switch\n------------\nGPT personas\n------------\nPrison\n------------\nModerator\n------------\nReminders\n------------\nGaming queue\n------------\nBlackjack\n------------\nRock Paper Scissors\n------------\nMagic 8 ball\n------------\nKebab\n------------\nWish me luck\n------------\nFlip a coin\n------------\nChangelog\n------------\nThank you\n------------")

# Info

        if message.content.lower().startswith('update battery'): # Because I'm running the script on my old phone lol
            # Check if the user has the "epic gamer (mod)" role
            if message.author.guild_permissions.administrator: # custom role
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
            if message.author.guild_permissions.administrator: # custom role
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
                info_message = f"**Uptime:** {uptime_str}\n\n**Next charge at:** {next_charge_time_str}\n\n**Active Modes:** {', '.join(active_modes)}\n\n**Naughty Gamers:** {naught_gamers_list}\n\n**Battery:** {battery_info}\n\n**Spam deleted:** {spam_counter}"

                # Send info message
                await message.channel.send(info_message)

# Changelog, I removed some features from this open source version

        # Changelog feature
        changelog = {
            "v2": "Chatbot",
            "v2.5": "text-curie-001 to gpt-3.5-turbo-instruct",
            "v3": "moderator\nadded on/off switch\nadded wish me luck\nadded parrot mode\nadded reminder\nadded blackjack",
            "v3.1": "added Nixann mode\nFrench revolution\nincreased max token from 128 to 512\nimproved reminder",
            "v3.5": "added Kebab\nadded Prison\nadded gaming queue\nhotfixes",
            "v3.8": "added bomboclat mode\nadded DM limiter\nadded repetitive response limited",
            "v3.9": "added uwu mode\nadded word replacers\nadded GIF reactions",
            "v4": "added uptime info\nadded flip a coin\nadded a lot more GIF reactions and word replacers\nimproved gpt prompts",
            "v5": "added casual mode\nimproved GIF reaction logic\nadded low battery warning\nadded rock paper scissors\nadded magic 8 ball",
            "v6": "added yapping and spamming protection\nadded changelog",
            "v6.1": "added #FREETAYK\nadded 'Next charge' to 'info'\nadded AUTOMATED stream alert\nGG\nadded out on bail GIFs\nadded Saul Goodman mode",
            "v6.9": "currently in development",
            "hotfix": "\nv6.5\ntesting for global servers\nadded GPT based spam filter"
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

# Crazy

        loop_responses = [
            "**Infinite loop detected, initiating reboot sequence...**",
            "**System error: Infinite loop encountered. Resetting now...**",
            "**Oops! Looks like we're stuck in a loop. Restarting...**",
            "**System malfunction: Loop detected. Rebooting system...**",
            "**Infinite loop detected. Please stand by while I reset...**",
            "**System alert: Infinite loop found. Initiating reset...**",
            "**Error: Loop condition met. Rebooting...**",
            "**Infinite loop error. System reboot in progress...**",
            "**Warning: Loop detected. System reset initiated...**",
            "**System alert: Stuck in a loop. Restarting now...**",
            "**Error: Loop detected. Please wait while I reboot...**",
            "**Infinite loop condition met. Resetting the system...**",
            "**System error: Loop detected. Reboot in progress...**",
            "**Warning: Infinite loop detected. Resetting now...**",
            "**Error 500: Infinite loop. System reset initiated...**",
            "**Alert: Loop detected. Rebooting system...**",
            "**System error: Loop condition encountered. Restarting...**",
            "**Warning: Loop detected. Initiating system reboot...**"
        ]

        random_loop_response = random.choice(loop_responses)


        if last_triggered_time_crazy is None or current_time - last_triggered_time_crazy >= timedelta(seconds=cooldown_time_crazy):

            if re.search(r'\bcrazy\b', message.content, re.IGNORECASE):
                regular_probability = 0.1
                if random.random() < regular_probability:
                    # Update the last triggered time
                    last_triggered_time_crazy = current_time

                    # List of responses
                    responses = [
                        "Crazy?",
                        "I was crazy once.",
                        "They put me in a room.",
                        "A rubber room.",
                        "A rubber room with rats.",
                        "And rats make me crazy.",
                        "Crazy?",
                        "I was crazy once.",
                        "They put me in a room.",
                        "A rubber room.",
                        "A rubber room with rats.",
                        "And rats make me crazy.",
                        random_loop_response,
                        "Reboot complete"
                    ]

                    for response in responses:
                        await message.channel.send(response)
                        await asyncio.sleep(1)

                        def check(msg):
                            return msg.channel == message.channel and msg.id != message.id

                        try:
                            await bot.wait_for('message', timeout=1, check=check)
                            break
                        except asyncio.TimeoutError:
                            continue

# FREETAY-K

        # Check if the user wants to free someone or everyone
        if message.content.lower().startswith('free'):
            # Check if the author has the "epic gamer (mod)" role
            if message.author.guild_permissions.administrator:
                # Check if the user wants to free all sentenced users
                if message.content.lower() == 'free all':
                    naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer")
                    for member in message.guild.members:
                        if naughty_gamer_role in member.roles:
                            await member.remove_roles(naughty_gamer_role)
                            await message.channel.send(f"{member.mention} enjoy freedom!")
                else:
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
            else:
                await message.channel.send("Nuh uh")

# Prison 1/2

        # Check for "sentence to prison" command
        if "sentence" in message.content.lower() and "to prison" in message.content.lower():
            # Check if the author has the "epic gamer (mod)" role
            if message.author.guild_permissions.administrator: # custom role
                # Extract the duration from the message
                duration_match = re.search(r'for (\d+|life)?\s*(year|years|month|months|life)', message.content.lower())
                if duration_match:
                    duration = int(duration_match.group(1)) if duration_match.group(1) else 1  # Default to 1 if no number provided
                    time_unit = duration_match.group(2)
                    if time_unit == 'month' or time_unit == 'months':
                        timer_seconds = duration * 60  # Convert months to minutes
                    elif time_unit == 'year' or time_unit == 'years':
                        timer_seconds = duration * 600  # Convert years to hours
                    else:
                        timer_seconds = 36000  # Default to 10 hour for life sentence

                    # Find and sentence the mentioned users to prison
                    user_matches = re.finditer(r'<@!?(\d+)>', message.content)
                    for user_match in user_matches:
                        user_id = int(user_match.group(1))
                        member = message.guild.get_member(user_id)
                        if member:
                            # Give the "Naughty Gamer" role to the user
                            naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer") # custom role
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
                            naughty_gamer_role = discord.utils.get(user.guild.roles, name="Naughty Gamer") # custom role
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
                naughty_gamer_role = discord.utils.get(message.guild.roles, name="Naughty Gamer") # custom role
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

                await message.channel.send(f"User {member.mention} has gained back their right to talking")

            else:
                await message.channel.send("Unable to find the user to timeout.")
            return

# OpenAI API funny custom prompts 

        if message.content.lower() == 'bomboclat':
            bomboclat_mode = True
            casual_mode = False
            await message.channel.send("BOMBOCLATT!!!")

        if message.content.lower() == 'huihui':
            bomboclat_mode = False
            casual_mode = True    

        if message.content.lower() == 'casual':
            bomboclat_mode = False
            casual_mode = True
            await message.channel.send("Suh")

        if message.content.lower() == 'yapping':
            casual_mode = False 
            await message.channel.send("What's yappening?")

        # Check for Beebo or B-b0
        if re.search(r'\bB\b', message.content) or 'B-b0' in message.content or 'Beebo' in message.content:

            # Initialize context as blank
            context = ""

            # Check if the message is a reply to another message
            if message.reference and isinstance(message.reference.resolved, discord.Message):
                # Get the original message content being replied to
                replied_message = message.reference.resolved
                context = f"Context: {replied_message.author.name} said: \"{replied_message.content}\".\n"

            user_input = message.content.replace('B-b0', '').replace('Beebo', '').replace('B', '').strip()

            # Check if bomboclat mode is enabled
            if bomboclat_mode:
                user_input += "- answer to this if you were roleplaying a jamaican rastaman"

            # Check if casual mode is enabled
            if casual_mode:
                user_input += "- answer to this short and casual, use emojis instead of doing physical activity, no hashtags"

            # Add the context to the user input if available
            if context:
                user_input = context + user_input

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

# Parrot mode

        # Define the keywords to trigger the response
        keywords = ["szia", "real", "gaming", "yippie", ":3", "xd"]

        # Check if any of the keywords are present in the message
        keyword_present = any(keyword in message.content.lower() for keyword in keywords)

        # If no keyword is found, return without processing
        if not keyword_present:
            return
        # Continue with parrot mode or other processing here
        regular_probability = 0.3

        # Decide which gif to send based on probabilities
        if random.random() < regular_probability:
            # Continue with parrot mode or other processing here
            for keyword in keywords:
                if keyword in message.content.lower():
                    response_message = f"{keyword}"
                    await message.channel.send(response_message)

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
                naughty_gamer_role = discord.utils.get(user.guild.roles, name="Naughty Gamer") # custom role
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

# Spam GPT

async def is_spam_with_gpt(message_content):
    
    # Call the OpenAI API to determine if the message is spam (1) or not (0).
    
    # Prepare the prompt for the OpenAI API
    prompt = f"Is the following message spam? (Respond with 1 for yes, 0 for no)\nMessage: {message_content}"

    try:
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use your preferred model
            messages=[{"role": "system", "content": prompt}],
            max_tokens=10,  # Keep it short, we just need a 1 or 0
            temperature=0.0  # Ensure it's deterministic
        )
        
        # Extract the response (0 or 1)
        result = response['choices'][0]['message']['content'].strip()

        # Print the response from GPT to the console for debugging
        print(f"GPT Response: {result}")  # Log the GPT result for debugging
        
        return int(result) == 1  # Convert result to boolean (True if spam)
    except Exception as e:
        print(f"Error checking spam via GPT: {str(e)}")
        return False

async def handle_message(message):
    global spam_counter
    
    # Handle incoming messages to check for spam, delete spam, and ban repeat offenders.
    if isinstance(message.channel, discord.DMChannel):
        # This is a DM, so skip the guild permissions check
        print("-----Message received in DM------")
    else:
        if not message.author.guild_permissions.administrator:
        
            # List of spam-triggering keywords and emojis
            spam_triggers = [
                r"📢",
                r"👉",
                r"airdrop",
                r"giveaway",
                r"\$",
                r"nft",
                r"free\s+mint",
                
            ]
            
            # Check for any of the spam-triggering emojis or words
            is_spam = False
            for trigger in spam_triggers:
                if re.search(trigger, message.content.lower()):
                    #Spam detected
                    is_spam = True
                    print(f"Spam trigger detected in message: {message.content}")
                    break

            if is_spam:
                # Send the message content to OpenAI API for spam detection
                gpt_spam = await is_spam_with_gpt(message.content)

                if gpt_spam:
                    try:
                        await message.delete()
                        spam_counter += 1

                        await track_spam(message.author)
                    except Exception as e:
                        print(f"Error deleting message: {str(e)}")
                else:
                    print("GPT determined this message is NOT spam.")
            else:
                print("No spam triggers found in the message.")
        else:
            print("Message is from an admin user, skipping spam check.")

async def track_spam(user):
    global spam_tracker
    # Track the user's spam activity and ban them if they exceed the limit.
    
    now = datetime.now()
    user_id = user.id

    # Initialize spam tracking for the user if not already present
    if user_id not in spam_tracker:
        spam_tracker[user_id] = []

    # Remove old spam records (older than 1 minute)
    one_minute_ago = now - timedelta(minutes=1)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if t > one_minute_ago]

    # Add the current timestamp
    spam_tracker[user_id].append(now)

    # Check if they sent 3 spam messages within the last minute
    '''
    if len(spam_tracker[user_id]) >= 3:
        try:
            # Ban the user for spamming
            await user.guild.ban(user, reason="GPT caught you lackin")
            print(f"Banned user {user.name} for spamming.")
            del spam_tracker[user_id]  # Clear the user's spam record after banning  
        except Exception as e:
            print(f"Error banning user: {str(e)}")
    '''       

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
bot.run('Finally your Discord Bot API')
