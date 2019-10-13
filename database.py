# Database Abstraction Object for storing messages

# Database in use is SQLite3
import sqlite3
import discord


class Database:
    def __init__(self, path):
        self.database = sqlite3.connect(path)

    # Set-up the database for use or something.
    def setup(self):
        c = self.database.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Blacklist_Channel
        (channel_id INTEGER UNIQUE NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Blacklist_User
        (user_id INTEGER UNIQUE NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Messages (
        guild_id INT NOT NULL, channel_id INT NOT NULL, message_id INT NOT NULL PRIMARY KEY, timestamp INT NOT NULL,
        author_id INT NOT NULL, content TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Attachments (message_id INT NOT NULL, file_url TEXT DEFAULT NULL, 
        FOREIGN KEY (message_id) REFERENCES Messages (message_id))''')

        self.database.commit()

    def is_in_blacklist_channel(self, channel):
        c = self.database.cursor()
        c.execute('''SELECT channel_id FROM Blacklist_Channel WHERE channel_id=?''', (channel.id,))
        return c.fetchone() is not None

    def is_in_blacklist_user(self, user):
        c = self.database.cursor()
        c.execute('''SELECT user_id FROM Blacklist_User WHERE user_id=?''', (user.id,))
        return c.fetchone() is not None

    def get_last_messages(self, channel):
        # Return None if query is empty
        c = self.database.cursor()
        c.execute('''SELECT message_id FROM Messages WHERE channel_id=? ORDER BY timestamp DESC LIMIT 100''',
                  (channel.id,))
        results = c.fetchall()
        return results

    def insert_blacklist_channel(self, channel):
        c = self.database.cursor()
        c.execute('''INSERT OR IGNORE INTO Blacklist_Channel VALUES (?)''', channel.id)
        c.execute('''DELETE FROM Messages WHERE channel_id=?''', (channel.id,))
        self.database.commit()

    def insert_blacklist_user(self, user):
        c = self.database.cursor()
        c.execute('''INSERT OR IGNORE INTO Blacklist_User VALUES (?)''', user.id)
        self.database.commit()

    def message_insert(self, message):
        c = self.database.cursor()
        c.execute('''INSERT INTO Messages VALUES (?, ?, ?, ?, ?, ?)''', (
            message.guild.id, message.channel.id, message.id, message.created_at.timestamp(), message.author.id,
            message.content))
        self.database.commit()

    def make_attachment_tuple(self, message, attachment):
        try:
            return message.id, attachment.url
        except discord.HTTPException:
            return None

    def buffered_message_insert(self, messages):
        c = self.database.cursor()
        c.executemany('INSERT INTO Messages VALUES (?, ?, ?, ?, ?, ?)', [(message.guild.id, message.channel.id,
                                                                          message.id, message.created_at.timestamp(),
                                                                          message.author.id, message.content)
                                                                         for message in messages])

        c.executemany('INSERT INTO Attachments VALUES (?, ?)', filter(lambda x: x[1] is not None,
                                                                      [self.make_attachment_tuple(message, attachment)
                                                                       for message in messages
                                                                       for attachment in message.attachments]))
        self.database.commit()

    def get_message(self, message_id):
        pass

    def get_all_messages_from_channel(self, channel_id):
        pass
