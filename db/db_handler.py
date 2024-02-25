# Import the ezcord module
import ezcord

# Create a new class that inherits from ezcord.DBHandler
class WelcomeDB(ezcord.DBHandler):
    # Create a constructor for the class
    def __init__(self):
        super().__init__("welcome.db")
    
    # Create a setup method to create the table
    async def setup(self):
        await self.exec(
            """
            CREATE TABLE IF NOT EXISTS welcome (
                guild_id BIGINT PRIMARY KEY,
                role_id BIGINT
            )"""
        )

    # Create a method to get all welcome roles
    async def get_welcome_role(self, guild_id: int):
        return await self.fetchall(
            "SELECT role_id FROM welcome WHERE guild_id = ?", (guild_id,)
        )
    
    # Create a method to add a welcome role
    async def add_welcome_role(self, guild_id: int, role_id: int):
        await self.exec(
            "INSERT INTO welcome (guild_id, role_id) VALUES (?, ?)", (guild_id, role_id)
        )
    
    # Create a method to remove a welcome role
    async def remove_welcome_role(self, guild_id: int, role_id: int):
        await self.exec(
            "DELETE FROM welcome WHERE guild_id = ? AND role_id = ?", (guild_id, role_id)
        )