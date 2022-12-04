import discord
from discord import app_commands
import asyncio

import envs


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        await self.tree.sync()


client = MyClient(intents=discord.Intents.all())


# Define the "sudo" command
@client.tree.command()
async def sudo(interaction: discord.Interaction):
    # Check if the user has the "sudoers" role
    if "sudoers" in [role.name for role in interaction.user.roles]:
        # Give the user the "sudo" role
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name="sudo"))
        await interaction.response.send_message("You have been granted sudo access. Valid for 3 min.", ephemeral=True)
        await asyncio.sleep(3*60)
        await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="sudo"))
    else:
        # The user does not have the "sudoers" role, so do nothing
        await interaction.response.send_message("You do not have the sudoers role!")

# Run the bot
client.run(envs.TOKEN)
