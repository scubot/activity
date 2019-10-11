import os
import time

import discord
from discord.ext import commands
import database as database
import tqdm


class Activity(commands.Cog):
    def __init__(self, bot):
        self.version = "1.0.0"
        self.bot = bot
        self.dao = database.Database('./modules/databases/activity.db')
        self.dao.setup()

    async def determine_last_message(self, channel):
        for item in self.dao.get_last_messages(channel):
            try:
                i = await channel.fetch_message(item[0])
                return i
            except discord.NotFound:
                continue

    async def sync_channel(self, channel, pbar, pbar_message):
        last_scraped_message = await self.determine_last_message(channel)
        time_last = time.time()
        buffer = []
        async for message in channel.history(limit=None, after=last_scraped_message, oldest_first=True):
            buffer.append(message)
            if len(buffer) >= 10000:
                self.dao.buffered_message_insert(buffer)
                buffer = []
            time_now = time.time()
            pbar.update(1)
            if time_now - time_last >= 5:
                await pbar_message.edit(content=pbar)
                time_last = time.time()

        self.dao.buffered_message_insert(buffer)
        await pbar_message.edit(content=pbar)
        pbar.close()

    @commands.group(invoke_without_commands=False)
    async def activity(self, ctx):
        pass

    @activity.command(name="update")
    async def update(self, ctx, channel: discord.TextChannel = None):
        update_list = []
        if not channel:
            update_list = ctx.guild.text_channels
        else:
            update_list.append(channel)

        for c in update_list:
            if self.dao.is_in_blacklist_channel(c):
                continue
            n = await ctx.send("Now scraping " + str(c) + "...")
            bar = tqdm.tqdm(total=0, unit=' messages', mininterval=3, file=open(os.devnull, 'w'))
            m = await ctx.send(bar)
            await self.sync_channel(c, bar, m)
            await n.edit(content="Now scraping " + str(c) + "... done.")

    @commands.has_any_role('moderators', 'admin', 'devs')
    @activity.command(name="ignorechannel")
    async def blacklist(self, ctx, *, channel: discord.TextChannel):
        self.dao.insert_blacklist_channel(channel)

    @activity.command(name="channel")
    async def channel_stat(self, ctx):
        pass

    @activity.command(name="user")
    async def user_stat(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Activity(bot))
