# Database Abstraction Object for storing messages
import sqlite3


class Database:
    def __init__(self, path):
        self.database = sqlite3.connect(path)

    # Set-up the database for use or something.
    def setup(self):
        c = self.database.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Blacklist_Channel
        (channel_id INTEGER NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Blacklist_User
        (user_id INTEGER NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Messages (
        channel_id INT NOT NULL, message_id INT NOT NULL, timestamp INT NOT NULL, author_id INT NOT NULL, 
        content TEXT)''')

        self.database.commit()

    def is_in_blacklist_channel(self, channel):
        return False
        pass

    def is_in_blacklist_user(self, user):
        return False
        pass

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
        self.database.commit()

    def insert_blacklist_user(self, user):
        c = self.database.cursor()
        c.execute('''INSERT OR IGNORE INTO Blacklist_User VALUES (?)''', user.id)
        self.database.commit()

    def message_insert(self, message):
        c = self.database.cursor()
        c.execute('''INSERT INTO Messages VALUES (?, ?, ?, ?, ?)''', (
            message.channel.id, message.id, message.created_at.timestamp(), message.author.id, message.content
        ))
        self.database.commit()

    def buffered_message_insert(self, messages):
        c = self.database.cursor()
        c.executemany('INSERT INTO Messages VALUES (?, ?, ?, ?, ?)', [(message.channel.id, message.id,
                                                                       message.created_at.timestamp(),
                                                                       message.author.id, message.content)
                                                                      for message in messages])
        self.database.commit()

    def get_message(self, message_id):
        pass

    def get_all_messages_from_channel(self, channel_id):
        pass