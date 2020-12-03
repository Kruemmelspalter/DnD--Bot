import json
import enum
import os.path

import discord.ext.commands
from dnd5eapi import api

API = api.DnD5eApi()


class PartyInv(discord.ext.commands.Cog):
    def __init__(self, bot, file='/etc/dndtools-discord/pi.json', conf='/etc/dndtools-discord/conf.json'):

        self.bot = bot
        self.file = file
        self.syntax = {'partyinv': """
        ^pi list
        ^pi add item <item name>
        ^pi add currency <amount>
        ^pi remove item <item name>
        ^pi register
        """}
        self.conf = conf

    @discord.ext.commands.command(name='partyinv', aliases=['pi'])
    async def partyinv_command(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(embed=self.error_embed('partyinv', self.ErrorReasons.SYNTAX))
            return

        if args[0] == 'add':
            if len(args) == 1:
                await ctx.send(embed=self.error_embed('partyinv', self.ErrorReasons.SYNTAX))
                return

            if args[1] == 'item':
                item = await API.get_item(args[2])
                if isinstance(item, list):
                    if len(item) == 0:
                        await ctx.send(embed=self.error_embed('partyinv', self.ErrorReasons.NONEFOUND))
                        return
                    await ctx.send(embed=self.multiple_items_found_embed(item))
                else:
                    item['meta'] = ""
                    if len(args) >= 4:
                        self.add_item(item, int(args[3]))
                    else:
                        self.add_item(item, 1)
                    await self.update_lists(ctx)
            elif args[1] == 'currency':
                self.add_currency(float(args[2]))
                await self.update_lists(ctx)

            elif args[1] == 'custom':
                item = {'index': args[2].lower().replace(' ', '-'), 'name': args[2], 'meta': ""}
                if len(args) >= 5:
                    item['meta'] = " ".join(args[4:])
                if len(args) >= 4:
                    self.add_item(item, int(args[3]))
                else:
                    self.add_item(item, 1)
                await self.update_lists(ctx)
            else:
                await ctx.send(embed=self.error_embed('partyinv', self.ErrorReasons.SYNTAX))
                return

        elif args[0] == 'remove':
            if args[1] == 'item':
                item = await API.get_item(args[1])
                if isinstance(item, list):
                    if len(item) == 0:
                        await ctx.send(embed=self.error_embed('partyinv', self.ErrorReasons.NONEFOUND))
                        return
                    await ctx.send(embed=self.multiple_items_found_embed(item))
                else:
                    if len(args) >= 4:
                        self.remove_item(item, int(args[3]))
                    else:
                        self.remove_item(item, 1)
                await self.update_lists(ctx)
            elif args[1] == 'custom':
                item = {'index': args[2].lower().replace(' ', '-'), 'name': args[2]}
                if len(args) >= 4:
                    self.remove_item(item, int(args[3]))
                else:
                    self.remove_item(item, 1)
                await self.update_lists(ctx)

        elif args[0] == 'list':
            await ctx.send(embed=self.inv_to_embed(self.get_inv()))

        elif args[0] == 'register':
            with open(self.conf) as f:
                conf = json.load(f)
                f.close()
            conf['continuous'] += [(await ctx.send(embed=self.inv_to_embed(self.get_inv()))).id]
            with open(self.conf, 'w+') as f:
                json.dump(conf, f)
                f.close()

        else:
            await ctx.send(embed=self.error_embed('partyinv', self.ErrorReasons.SYNTAX))
            return

        await ctx.message.delete()

    async def update_lists(self, ctx):
        with open(self.conf) as f:
            conf = json.load(f)
            f.close()
        for c in conf['continuous']:
            await self.update_list(c, ctx)

    async def update_list(self, msg, ctx):
        msg = await ctx.fetch_message(msg)
        await msg.edit(embed=self.inv_to_embed(self.get_inv()))

    def get_inv(self):
        with open(self.file) as f:
            inv = json.load(f)
            f.close()
        return inv

    def get_items(self):
        return self.get_inv()['items']

    def remove_item(self, item, count):
        with open(self.file) as f:
            inv = json.load(f)
            f.close()
        if item['index'] in inv['items'].keys():
            if inv['items'][item['index']]['count'] - count <= 0:
                del inv['items'][item['index']]
            else:
                inv['items'][item['index']]['count'] -= count
        with open(self.file, "w+") as f:
            json.dump(inv, f)
            f.close()

    def add_item(self, item, count):
        with open(self.file) as f:
            inv = json.load(f)
            f.close()
        if item['index'] in inv['items'].keys():
            inv['items'][item['index']]['count'] += count
        else:
            inv['items'][item['index']] = {**{n: item[n] for n in item if n != 'index'}, **{'count': count}}
        with open(self.file, "w+") as f:
            json.dump(inv, f)
            f.close()

    def get_gold(self):
        return self.get_inv()['gold']

    def add_currency(self, gold):
        with open(self.file) as f:
            inv = json.load(f)
            f.close()
        inv["gold"] += gold
        with open(self.file, "w+") as f:
            json.dump(inv, f)
            f.close()

    def inv_to_embed(self, inv):
        embed = discord.Embed(title="Inventory", color=discord.Color.green())
        embed.add_field(name="Currency", value=str(inv['gold']) + " GP")
        item_list = "\n".join([str(inv['items'][i]['count']) + "x " + inv['items'][i]['name'] + " (" +
                               inv['items'][i]['meta'] + ")" for i in inv['items']]) or "No items"
        embed.add_field(name="Items", value=item_list)
        return embed

    def error_embed(self, command, reason):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="Reason", value=reason.value)
        embed.add_field(name="Command Syntax", value=self.syntax[command])
        return embed

    def multiple_items_found_embed(self, items):
        embed = discord.Embed(title="Multiple Items found! Please use one of the following item names",
                              color=discord.Color.gold())
        embed.add_field(name="Found items", value="\n".join([i['name'] for i in items]))
        return embed

    class ErrorReasons(enum.Enum):
        SYNTAX = "Syntax Error"
        JSON = "JSON Error"
        NONEFOUND = "No items found"


def setup(bot):
    bot.add_cog(PartyInv(bot))
