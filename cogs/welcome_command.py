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

    # Create a select menu to add a role
    class AddRoleMenu(discord.ui.Select):
        def __init__(self, msg_id):
            self.msg_id = msg_id
            super().__init__(
                placeholder="Add a role", 
                custom_id="select_role", 
                options = []
                )
        # Create a callback for the select menu
        async def callback(self, interaction):
            print("3")
            print(self.msg_id)
            await WelcomeDB().add_welcome_role(interaction.guild.id, int(interaction.data['values'][0]))
            message = await interaction.guild.get_channel(interaction.channel_id).fetch_message(self.msg_id)
            await message.edit(content="Role successfully added", embed=None, view=None)
            await interaction.response.edit_message(content=f"Role successfully added", embed=None, view=None)    	    


    # Create a select menu to Remove a role
    class RemoveRoleMenu(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Remove a role", 
                custom_id="select_role2", 
                options = []
                )
        # Create a callback for the select menu
        async def callback(self, interaction):
            await WelcomeDB().remove_welcome_role(interaction.guild.id, int(interaction.data['values'][0]))
            await interaction.response.edit_message(content=f"Role successfully removed", embed=None, view=None)    	    



    # Create a button to add or remove a role
    class AddRemoveRoleButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        
        # Create a button to add or remove a role
        @discord.ui.button(label="Add/Remove Role", style=discord.ButtonStyle.gray, custom_id="add_remove_role")
        async def add_remove_role(self, button, interaction):            

            # Create a select menu to add or remove a role
            select1 = welcomeCommand.AddRoleMenu(msg_id=interaction.message.id)
            # Loop through the roles in the guild and add them to the select menu
            for role in interaction.guild.roles:
                select1.append_option(discord.SelectOption(label=role.name, value=str(role.id)))
            # Create an action row and add the select menu

            add_remove_embed = discord.Embed(
                title="Add/Remove Role",
                description="Please select a role to add/remove when a user joins the server",
                color=discord.Color.dark_grey()
            )

            select2 = welcomeCommand.RemoveRoleMenu()

            view = discord.ui.View()
            view.add_item(select1)
            view.add_item(select2)
            roles = await WelcomeDB().get_welcome_roles(interaction.guild.id)
            for role in roles:
                role = interaction.guild.get_role(int(role))
                select2.append_option(discord.SelectOption(label=role.name, value=str(role.id)))

            await interaction.response.send_message(embed=add_remove_embed, view=view)
            
            
    
    # Create a command to display the welcome role menu
    @commands.slash_command(name="welcome", description="[ADMIN] Display the welcome role menu")
    @discord.default_permissions(administrator=True)
    async def welcome(self, ctx):
        # Get the welcome roles from the database
        auto_roles = await WelcomeDB().get_welcome_roles(ctx.guild.id)
        # Check if there are any welcome roles
        if auto_roles and auto_roles != None:
            # Create a new embed
            menu_embed = discord.Embed(
                title="Welcome Role Menu",
                description="""
There are currently the following Auto Roles set up:\n
""",
                color=discord.Color.dark_grey(),
            )
            # Loop through the welcome roles and add them to the embed
            for role in auto_roles:
                role = ctx.guild.get_role(int(role))
                menu_embed.description += f"- {role.mention}\n"

            # Respond with the embed
            message = await ctx.respond(content=".", embed=menu_embed, view=welcomeCommand.AddRemoveRoleButton())
        else:
            menu_embed = discord.Embed(
                title="Welcome Role Menu",
                description="Select a Role in the Menu to add your first Auto Role",
                color=discord.Color.dark_grey()
            )
            select1 = welcomeCommand.AddRoleMenu()
            # Loop through the roles in the guild and add them to the select menu
            for role in ctx.guild.roles:
                select1.append_option(discord.SelectOption(label=role.name, value=str(role.id)))
            view = discord.ui.View()
            view.add_item(select1)
            await ctx.respond(embed=menu_embed, view=view)

# Add the cog to the bot
def setup(bot):
    bot.add_cog(welcomeCommand(bot))