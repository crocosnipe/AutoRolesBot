# Import the required modules
import ezcord
import discord
from discord.ext import commands
from db.db_handler import WelcomeDB

# Define the Bot intents
intents = discord.Intents.all()
# Create a new instance of the Bot class
bot = ezcord.Bot(intents=intents, language="en")

# Create an event listener for when the bot is ready and print a message
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    # Load the cogs from the cogs folder
    bot.load_cogs("cogs")
    # Run the bot
    bot.run("YOUR_BOT_TOKEN") # Replace YOUR_BOT_TOKEN with your bot token from https://discord.com/developers/applications
