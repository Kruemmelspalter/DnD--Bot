import discord.ext.commands
import json

bot = discord.ext.commands.Bot(
    command_prefix="^",
    owner_id=371331470230290435,
    case_insensitive=True
)

cogs = ['cogs.partyinv']


@bot.event
async def on_ready():
    for cog in cogs:
        bot.load_extension(cog)
    print(f'Logged in as {bot.user} ({bot.user.id})')


if __name__ == "__main__":
    with open('/etc/dndtools-discord/conf.json') as f:
        conf = json.load(f)
        f.close()
    print(conf['token'])
    bot.run(conf['token'])
