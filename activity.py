import discord
from discord.ext import commands
from tinydb import Query, TinyDB


class Activity(commands.Cog):
    def __init__(self, bot):
        self.version = "1.0.0"
        self.bot = bot
        self.db = TinyDB('./modules/databases/activity')
        self.blacklist = self.db.table('blacklist')

    @staticmethod
    async def determine_last_message(channel, table):
        for item in reversed(table):
            try:
                i = channel.fetch_message(item['id'])
                return i
            except discord.NotFound:
                continue

    async def sync_channel(self, channel):
        channel_table = self.db.table(channel.id)
        last_scraped_messaged = self.determine_last_message(channel, channel_table)
        async for message in channel.history(limit=None, after=last_scraped_messaged):
            channel_table.add({
                'id': message.id,
                'timestamp': message.created_at.timestamp(),
                'author_id': message.author.id,
                'content': message.content
            })

    @commands.group(invoke_without_commands=False)
    async def activity(self, ctx):
        pass

    @activity.command(name="update")
    async def update(self, ctx, *, channel: discord.TextChannel = None):
        target = Query()
        update_list = []
        if not channel:
            update_list = ctx.guild.text_channels
        else:
            update_list = update_list.append(channel)

        for c in update_list:
            if self.blacklist.get(target.id == c.id) is not None:
                continue
            await self.sync_channel(c)

    @commands.has_any_role('moderators', 'admin', 'devs')
    @activity.command(name="blacklist")
    async def blacklist(self, ctx, *, channel: discord.TextChannel):
        target = Query()
        if self.blacklist.get(target.id == channel.id) is None:
            self.blacklist.insert({'id': channel.id})

    @activity.command(name="channel")
    async def channel_stat(self, ctx):
        pass

    @activity.command(name="user")
    async def user_stat(self, ctx):
        pass