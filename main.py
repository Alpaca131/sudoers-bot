import discord
from discord import app_commands
import asyncio, json, time

import envs

file_loaded = False
sudo_users = {}


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


@client.event
async def on_ready():
    global file_loaded
    print("logged in")
    if file_loaded:
        return
    with open("sudo_users.json", "r") as f:
        stored_sudo_users = json.load(f)
        sudo_users.update(stored_sudo_users)
    async_tasks = []
    for guild_id in stored_sudo_users:
        for user_id in stored_sudo_users[guild_id]:
            expiry_time = stored_sudo_users[guild_id][user_id]
            async_tasks.append(asyncio.create_task(await_sudo_expiry(expiry_time, guild_id, user_id)))
    if async_tasks:
        await asyncio.wait(async_tasks)
        write_sudo_users()
    file_loaded = True


# Define the "sudo" command
@client.tree.command()
async def sudo(interaction: discord.Interaction):
    # Check if the user has the "sudoers" role
    if "sudoers" in [role.name for role in interaction.user.roles]:
        # Give the user the "sudo" role
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name="sudo"))
        await interaction.response.send_message("You have been granted sudo access. Valid for 3 min.", ephemeral=True)
        add_sudo_users(interaction.guild.id, interaction.user.id)
        await asyncio.sleep(3 * 60)
        await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="sudo"))
    else:
        # The user does not have the "sudoers" role, so do nothing
        await interaction.response.send_message("You do not have the sudoers role!")


def add_sudo_users(guild_id, user_id):
    if guild_id not in sudo_users:
        sudo_users[guild_id] = {}
    # Record expiry time
    sudo_users[guild_id][user_id] = time.time() + 60*3
    write_sudo_users()


def write_sudo_users():
    with open("sudo_users.json", "w") as f:
        json.dump(sudo_users, f)


async def await_sudo_expiry(expiry: int, guild_id: int, user_id: int):
    seconds_to_wait = expiry - time.time()
    if seconds_to_wait > 0:
        await asyncio.sleep(seconds_to_wait)
    guild = client.get_guild(int(guild_id))
    member = guild.get_member(int(user_id))
    await member.remove_roles(discord.utils.get(guild.roles, name="sudo"))
    sudo_users[guild_id].pop(user_id)
    print(f"Removed sudo from {member}")

# Run the bot
client.run(envs.TOKEN)
