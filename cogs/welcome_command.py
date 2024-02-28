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

    # Create a function to easily edit the overview message when a role is added or removed
    async def editOverviewMessage(guild, message):
        # Get the welcome roles for the server
        auto_roles = await WelcomeDB().get_welcome_roles(guild.id)
        # Check if there are any welcome roles
        if auto_roles and auto_roles != None:
            # Create a new embed
            menu_embed = discord.Embed(
                title="Welcome Role Menu",
                description="""
    There are currently the following Auto Roles set up (max. 3):\n
    """,
                color=discord.Color.dark_grey(),
            )
            # Loop through the welcome roles and add them to the embed
            for role in auto_roles:
                role = guild.get_role(int(role))
                menu_embed.description += f"- {role.mention}\n"

            # edit the overview message from the start
            await message.edit(embed=menu_embed, view=welcomeCommand.AddRemoveRoleButton())
        else:
            # Create a new embed
            menu_embed = discord.Embed(
                title="Welcome Role Menu",
                description="Select a Role in the Menu to add your first Auto Role",
                color=discord.Color.dark_grey()
            )
            # Add the Role Selector
            select1 = welcomeCommand.AddRoleMenuNoRoles()
            # Loop through the roles in the guild and add them to the select menu
            for role in guild.roles:
                select1.append_option(discord.SelectOption(label=role.name, value=str(role.id)))
            # Create a new discord view and add the select menu to it
            view = discord.ui.View()
            view.add_item(select1)
            # edit the overview message from the start
            await message.edit(embed=menu_embed, view=view)
    

     # Create a select menu to add a role (only for the embed when you dont have any welcome roles setup)
    class AddRoleMenuNoRoles(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Add a role", 
                custom_id="select_role", 
                options = []
                )
        # Create a callback for the select menu
        async def callback(self, interaction):
            # Add the selected server role to the database
            await WelcomeDB().add_welcome_role(interaction.guild.id, int(interaction.data['values'][0]))
            # Edit the overiew Message
            await welcomeCommand.editOverviewMessage(interaction.guild, await interaction.guild.get_channel(interaction.channel_id).fetch_message(interaction.message.id))
            # Send the success message
            await interaction.response.send_message(content=f"Role successfully added", embed=None, view=None)
   
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
            # Add the selected server role to the database
            await WelcomeDB().add_welcome_role(interaction.guild.id, int(interaction.data['values'][0]))
            # Edit the overiew Message
            await welcomeCommand.editOverviewMessage(interaction.guild, await interaction.guild.get_channel(interaction.channel_id).fetch_message(self.msg_id))
            # Send the success message
            await interaction.response.edit_message(content=f"Role successfully added", embed=None, view=None)    	    


    # Create a select menu to Remove a role
    class RemoveRoleMenu(discord.ui.Select):
        def __init__(self, msg_id):
            self.msg_id = msg_id
            super().__init__(
                placeholder="Remove a role", 
                custom_id="select_role2", 
                options = []
                )
        # Create a callback for the select menu
        async def callback(self, interaction):
            # Remove the selected welcome role from the database
            await WelcomeDB().remove_welcome_role(interaction.guild.id, int(interaction.data['values'][0]))
            # Edit the overview Message
            await welcomeCommand.editOverviewMessage(interaction.guild, await interaction.guild.get_channel(interaction.channel_id).fetch_message(self.msg_id))
            # Send the success message
            await interaction.response.edit_message(content=f"Role successfully removed", embed=None, view=None)    	    



    # Create a View class with a button to edit the welcome roles
    class AddRemoveRoleButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        
        # Create a button to edit the welcome roles
        @discord.ui.button(label="Edit Welcomeroles", style=discord.ButtonStyle.gray, custom_id="add_remove_role")
        async def add_remove_role(self, button, interaction):            
            # Create a new Embed
            add_remove_embed = discord.Embed(
                title="Add/Remove Role",
                description="Please select a role to add/remove when a user joins the server",
                color=discord.Color.dark_grey()
            )
            
            # Create an add role select menu
            select1 = welcomeCommand.AddRoleMenu(msg_id=interaction.message.id)
            # Get the current welcome roles (needed here to only display roles in the select menu that arent already on the welcome roles list)
            auto_roles = await WelcomeDB().get_welcome_roles(interaction.guild.id)
            # Loop through the roles in the guild and add them to the select menu
            for role in interaction.guild.roles:
                # Do not display the default everyone role
                if role != interaction.guild.default_role:
                    # Only display roles that arent already in the welcome role list
                    if role.id not in auto_roles:
                        # Add the role to the select menu
                        select1.append_option(discord.SelectOption(label=role.name, value=str(role.id)))

            # Create an remove role select menu
            select2 = welcomeCommand.RemoveRoleMenu(msg_id=interaction.message.id)
            # Get the current welcome roles
            roles = await WelcomeDB().get_welcome_roles(interaction.guild.id)
            # Loop through all welcome roles
            for role in roles:
                # Get the role object from its ID
                role = interaction.guild.get_role(int(role))
                # Add the role to the select menu
                select2.append_option(discord.SelectOption(label=role.name, value=str(role.id)))

            # Create a new Discord UI View
            view = discord.ui.View()
            # Only add the Add Role Select menu to the view if there arent already 3 welcome roles
            if select1.options != [] and len(auto_roles) < 3:
                view.add_item(select1)
            # Add the Remove select menu to the view
            view.add_item(select2)

            # Send the response with the select menu(s)
            await interaction.response.send_message(embed=add_remove_embed, view=view)
            
            
    
    # Create a command to display the welcome role menu
    @commands.slash_command(name="welcome", description="[ADMIN] Display the welcome role menu")
    # Only Administrators should run this command
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
There are currently the following Auto Roles set up (max. 3):\n
""",
                color=discord.Color.dark_grey(),
            )
            # Loop through the welcome roles and add them to the embed
            for role in auto_roles:
                role = ctx.guild.get_role(int(role))
                menu_embed.description += f"- {role.mention}\n"

            # Respond with the embed
            await ctx.respond(embed=menu_embed, view=welcomeCommand.AddRemoveRoleButton())
        # If there are no welcome roles currently setup
        else:
            # Create a new embed
            menu_embed = discord.Embed(
                title="Welcome Role Menu",
                description="Select a Role in the Menu to add your first Auto Role",
                color=discord.Color.dark_grey()
            )
            # Add the Add Role (only for no welcome roles setup) select menu 
            select1 = welcomeCommand.AddRoleMenuNoRoles()
            # Loop through the roles in the guild and add them to the select menu
            for role in ctx.guild.roles:
                select1.append_option(discord.SelectOption(label=role.name, value=str(role.id)))
            # Create a new discord ui View
            view = discord.ui.View()
            # Add the Select menu to the view
            view.add_item(select1)
            # Respond with the embed and with the select menu
            await ctx.respond(embed=menu_embed, view=view)

# Add the cog to the bot
def setup(bot):
    bot.add_cog(welcomeCommand(bot))