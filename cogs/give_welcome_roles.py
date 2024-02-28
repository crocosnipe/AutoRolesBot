# Import required libraries
import ezcord
import discord
from discord.ext import commands
from db.db_handler import WelcomeDB


class giveWelcomeRoles(ezcord.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event listener for when a member joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Get the welcome roles for the server
        auto_roles = await WelcomeDB().get_welcome_roles(member.guild.id)
        # Check if the server has welcome roles
        if auto_roles and auto_roles != None:
            # Loop through the roles and add them to the member
            for role in auto_roles:
                # Get the role object from its ID
                role_object = member.guild.get_role(int(role))
                # Check if the bot has the permission to add the role
                if member.guild.me.top_role > role_object:
                    # Add the role to the member
                    await member.add_roles(role_object)


def setup(bot):
    bot.add_cog(giveWelcomeRoles(bot))
