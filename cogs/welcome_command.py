# Import required libraries
import ezcord
import discord
from discord.ext import commands
from db.db_handler import WelcomeDB


# Create the Welcome Command Ezcord Cog
class welcomeCommand(ezcord.Cog):
    # Create a constructor for the class
    def __init__(self, bot):
        self.bot = bot

    # Create a event to setup the database on ready event
    @commands.Cog.listener()
    async def on_ready(self):
        await WelcomeDB().setup()


# Add the cog to the bot
def setup(bot):
    bot.add_cog(welcomeCommand(bot))