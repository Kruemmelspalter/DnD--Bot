import discord.ext.commands

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
    bot.run('NzgzNDE1NTczMTQwODY1MDY2.X8aamw.9T87j8_1kREL2ckLLNpJW37VvCU')
