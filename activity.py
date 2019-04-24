import os
import time

import discord
from discord.ext import commands
from tinydb import Query, TinyDB
import tqdm


class Activity(commands.Cog):
    def __init__(self, bot):
        self.version = "1.0.0"
        self.bot = bot
        self.db = TinyDB('./modules/databases/activity')
        self.blacklist = self.db.table('blacklist')

    @staticmethod
    async def determine_last_message(channel, table):
        if not len(table):
            return None
        for item in reversed(table.all()):
            try:
                i = await channel.fetch_message(item['id'])
                return i
            except discord.NotFound:
                continue

    async def sync_channel(self, channel, pbar, pbar_message):
        channel_id = str(channel.id)
        channel_table = self.db.table(channel_id)
        last_scraped_message = await self.determine_last_message(channel, channel_table)
        time_last = time.time()
        async for message in channel.history(limit=None, after=last_scraped_message, oldest_first=True):
            time_now = time.time()
            print(message.content)
            channel_table.insert({
                'id': message.id,
                'timestamp': message.created_at.timestamp(),
                'author_id': message.author.id,
                'content': message.content
            })
            pbar.update(1)
            if time_now - time_last >= 5:
                await pbar_message.edit(content=pbar)
                time_last = time.time()

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     target = Query()
    #     if self.blacklist.get(target.id == str(message.channel.id)):
    #         return
    #     self.db.table(str(message.channel.id)).insert({
    #         'id': message.id,
    #         'timestamp': message.created_at.timestamp(),
    #         'author_id': message.author.id,
    #         'content': message.content
    #     })
    #
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("[INFO] Now scraping missed messages for defined servers")

    @commands.group(invoke_without_commands=False)
    async def activity(self, ctx):
        pass

    @activity.command(name="update")
    async def update(self, ctx, channel: discord.TextChannel = None):
        target = Query()
        update_list = []
        if not channel:
            update_list = ctx.guild.text_channels
        else:
            update_list.append(channel)

        for c in update_list:
            if self.blacklist.get(target.id == c.id) is not None:
                continue
            await ctx.send("Now scraping " + str(c))
            bar = tqdm.tqdm(total=0, unit=' messages', mininterval=3, file=open(os.devnull, 'w'))
            m = await ctx.send(bar)
            await self.sync_channel(c, bar, m)

    @commands.has_any_role('moderators', 'admin', 'devs')
    @activity.command(name="blacklist")
    async def blacklist(self, ctx, *, channel: discord.TextChannel):
        target = Query()
        if self.blacklist.get(target.id == channel.id) is None:
            self.blacklist.insert({'id': str(channel.id)})

    @activity.command(name="channel")
    async def channel_stat(self, ctx):
        pass

    @activity.command(name="user")
    async def user_stat(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Activity(bot))
