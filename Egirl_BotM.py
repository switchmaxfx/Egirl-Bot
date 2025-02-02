import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime
import json
from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO)

# Load .env file
if not load_dotenv():
    raise FileNotFoundError(".env file not found or couldn't be loaded")

# Get environment variables with validation
try:
    BOT_TOKEN = os.getenv('TOKEN')
    if not BOT_TOKEN:
        raise ValueError("Missing bot token in .env file")
except (TypeError, ValueError) as e:
    print(f"Error loading configuration: {e}")
    print("Please check your .env file")
    exit(1)

# Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
FRIENDS_FILE = "friends.json"

# Message lists
egirl_messages = [
    "Hewoo~",
    "UwU what's this?",
    "UwU notices you",  
    "*blushes*",
    "H-hi...",
    "*giggles*",
    "Anyone wanna p-play Valorant?",
    "I-I'm just a silly girl, don't mind me~",
    "OwO who's this?",
    "Nyaa~ what are you doing?",
    "Senpai noticed me? *blushes furiously*",
    "Do you like my new outfit? UwU",
    "Kyaaa~! You're so mean! >_<",
    "Pwease be gentle with me~",
    "I-I’m not cute, you are! *hides face*",
    "Do you wanna watch anime together? :3",
    "Eep! You scared me! >w<",
    "I-I’m not obsessed with you or anything, baka!",
    "Can we cuddle? *puppy eyes*",
    "I’m just a smol bean, don’t bully me!",
    "UwU *boops your nose*",
    "Do you like my hair? I did it just for you~",
    "Nani?! You’re so silly!",
    "I-I’m not blushing, you are!",
    "Let’s go on an adventure together! ^_^",
    "Pwease don’t leave me alone...",
    "You’re my favorite person, you know that? UwU",
    "I-I’m not crying, it’s just... allergies!",
    "Can we share a blanket? It’s cold! >_<",
    "You’re my senpai forever, okay? *hugs*"
]
rejection_messages = [  
    "Go away you creep! Try again in {remaining:.1f} seconds. UwU",  
    "Ew, no! Try again in {remaining:.1f} seconds. UwU",  
    "Not interested! Try again in {remaining:.1f} seconds. UwU",  
    "Maybe later... Try again in {remaining:.1f} seconds. UwU",  
    "I'm shy... Try again in {remaining:.1f} seconds. UwU",  
    "Blocked! Try again in {remaining:.1f} seconds. UwU",  
    "Disgusting. {remaining:.1f} seconds. Bye~",  
    "Nope. {remaining:.1f} seconds, loser. UwU",  
    "Cringe! Come back in {remaining:.1f} seconds. >:(",  
    "Yikes! {remaining:.1f} seconds, baka. UwU",  
    "Too desperate. {remaining:.1f} seconds. UwU",  
    "Begone, simp! {remaining:.1f} seconds. >_<",  
    "Ew, touch grass. {remaining:.1f} secs. UwU",  
    "Annoying. Cooldown: {remaining:.1f} secs. UwU",  
    "Nyah-ah! {remaining:.1f} seconds. Try harder~",  
    "Pathetic. {remaining:.1f} seconds. Bye~",  
    "Ugh, *blocks*. {remaining:.1f} secs. UwU",  
    "Not your day. {remaining:.1f} seconds. >w<",  
    "Desperate much? {remaining:.1f} secs. UwU",  
    "Weeb detected. {remaining:.1f} secs. UwU",  
    "Cringe overload! {remaining:.1f} secs. UwU",  
    "L + ratio. {remaining:.1f} seconds. UwU",  
    "Nope. Try {remaining:.1f} secs later. :P",  
    "NEXT! {remaining:.1f} seconds. UwU",  
    "Fumbled. {remaining:.1f} secs. Try again~"  
]  
success_messages = [  
    "Yay! You befriended an E-Girl! UwU",  
    "New friend acquired! UwU",  
    "E-Girl friendship level increased! UwU",  
    "You're now besties! UwU",  
    "Friendship request accepted! UwU",  
    "Mission success! E-Girl acquired~ UwU",  
    "Nyaa~ Friendship power overwhelming! *happy wiggle*",  
    "Achievement unlocked: E-Girl Companion! UwU",  
    "You’ve leveled up! Now cuddling permitted~ >w<",  
    "Poggers! You’re officially a cutie’s BFF! UwU",  
    "E-Girl bonded! *throws virtual confetti*",  
    "You’ve been adopted by an E-Girl! No escape~ UwU",  
    "Squad upgraded! *blushes and holds your arm*",  
    "Friendship XP maxed out! Time for anime marathons~",  
    "Connection secured! UwU *sends virtual headpats*",  
    "You’ve unlocked the ‘Bestie’ achievement! *confetti*",  
    "E-Girl heart +1! Careful, she’s clingy~ >_<",  
    "BFF status: Activated! *giggles and steals your hoodie*",  
    "Nyahaha~ You’re stuck with me forever now! UwU",  
    "Critical hit! Friendship at 100%! *blush*",  
    "Smol bean officially attached to you! No take-backsies~",  
    "E-Girl lootbox opened! You won a *hug*! UwU",  
    "Senpai~ You finally noticed me! *happy tears*",  
    "Bestie mode: ENGAGED! *hides face in excitement*",  
    "UwU *whispers* You’re my favorite human…"  
]

bot = commands.Bot(command_prefix='.', intents=intents)
active_egirl = False
cooldowns = {}

# Scoreboard functions
def load_friends():
    try:
        with open(FRIENDS_FILE, 'r') as f:
            data = json.load(f)
            # Convert all keys to strings (in case some were saved as numbers)
            return {str(k): v for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_friends(friends_data):
    with open(FRIENDS_FILE, 'w') as f:
        json.dump(validate_friends_data(friends_data), f)

def validate_friends_data(data):
    if not isinstance(data, dict):
        return {}
    
    cleaned = {}
    for user_id, count in data.items():
        try:
            # Ensure user_id is string and count is integer
            cleaned[str(user_id)] = int(count)
        except (ValueError, TypeError):
            continue
    
    return cleaned

@tasks.loop(seconds=1)
async def spawn_egirl():
    global active_egirl
    await bot.wait_until_ready()
    if not active_egirl:
        logging.info("Checking for E-Girl spawn...")
        await asyncio.sleep(random.randint(3600, 10800))  # 1-3 hours
        if not active_egirl:
            logging.info("Attempting to spawn in a random channel")
            channels = [channel for channel in bot.get_all_channels() 
                       if isinstance(channel, discord.TextChannel) 
                       and channel.permissions_for(channel.guild.me).send_messages]
            if channels:
                channel = random.choice(channels)
                logging.info(f"Found channel: {channel.name}")
                try:
                    active_egirl = True
                    msg = f"**E-Girl Appearance**\n{random.choice(egirl_messages)}"
                    logging.info(f"Sending message: {msg}")
                    await channel.send(msg)
                    await asyncio.sleep(30)  # 30-second window
                    active_egirl = False
                    logging.info("E-Girl disappeared")
                except Exception as e:
                    logging.error(f"Error in spawn_egirl: {repr(e)}")
                    active_egirl = False
            else:
                logging.error("No valid channels found!")

@bot.tree.command(name="bef", description="Befriend an E-Girl!")
async def bef(interaction: discord.Interaction):
    global active_egirl
    user_id = str(interaction.user.id)
    
    # Cooldown check
    if user_id in cooldowns:
        remaining = 5 - (datetime.now() - cooldowns[user_id]).total_seconds()
        if remaining > 0:
            await interaction.response.send_message(
                random.choice(rejection_messages).format(remaining=remaining),
                ephemeral=True
            )
            return
    
    # 50% rejection chance
    if random.random() < 0.5:
        await interaction.response.send_message(
            random.choice(rejection_messages).format(remaining=5),
            ephemeral=True
        )
        cooldowns[user_id] = datetime.now()
        return
    
    if active_egirl:
        active_egirl = False
        cooldowns[user_id] = datetime.now()
        
        # Update friend count
        friends = load_friends()
        user_id = str(interaction.user.id)
        friends[user_id] = friends.get(user_id, 0) + 1
        print(f"Updating score for {user_id}. New count: {friends[user_id]}")
        save_friends(friends)
        
        await interaction.response.send_message(
            random.choice(success_messages)
        )
    else:
        await interaction.response.send_message(
            "No E-Girls to befriend right now... owo",
            ephemeral=True
        )

@bot.tree.command(name="fren", description="Check your E-Girl friends!")
async def fren(interaction: discord.Interaction):
    friends = load_friends()
    count = friends.get(str(interaction.user.id), 0)
    await interaction.response.send_message(
        f"You've befriended {count} E-Girls! UwU",
        ephemeral=True
    )

@bot.tree.command(name="leaderboard", description="Global friendship leaderboard")
async def leaderboard(interaction: discord.Interaction):
    friends = load_friends()
    sorted_friends = sorted(friends.items(), key=lambda x: x[1], reverse=True)[:10]
    
    leaderboard = []
    for index, (user_id, count) in enumerate(sorted_friends, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            leaderboard.append(f"{index}. {user.display_name}: {count} friends")
        except:
            leaderboard.append(f"{index}. Unknown User: {count} friends")
    
    if not leaderboard:
        leaderboard = ["No friendships yet... owo"]
    
    await interaction.response.send_message(
        "**Global E-Girl Friendship Leaderboard**\n" + "\n".join(leaderboard)
    )

@bot.tree.command(name="debug_data")
async def debug_data(interaction: discord.Interaction):
    friends = load_friends()
    await interaction.response.send_message(
        f"Current data: {friends}",
        ephemeral=True
    )

@bot.tree.command(name="fix_data")
async def fix_data(interaction: discord.Interaction):
    if interaction.user.id != YOUR_USER_ID:  # Replace with your ID
        return await interaction.response.send_message(
            "Only the bot owner can use this!",
            ephemeral=True
        )
    
    friends = load_friends()
    fixed = {}
    for user_id, count in friends.items():
        fixed[str(user_id)] = fixed.get(str(user_id), 0) + count
    
    save_friends(fixed)
    await interaction.response.send_message(
        "Data has been fixed!",
        ephemeral=True
    )

@bot.event
async def on_connect():
    logging.info("Bot connected to Discord")

@bot.event
async def on_disconnect():
    logging.info("Bot disconnected from Discord")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()  # This syncs slash commands
    spawn_egirl.start()

bot.run(BOT_TOKEN)