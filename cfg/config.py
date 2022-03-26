import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def get_blacklist(self):
        with self.connection:
            result = [str(i[0]) for i in self.cursor.execute("SELECT id FROM blacklist").fetchall()]
            return result

    def show_blacklist(self):
        with self.connection:
            result = [f"@{str(i[0])}" for i in self.cursor.execute("SELECT username FROM blacklist").fetchall()]
            return result

    def get_coupons(self):
        with self.connection:
            result = [i[0] for i in self.cursor.execute("SELECT coupon FROM coupons").fetchall()]
            return result

    def add_blacklist(self, username, user_id):
        with self.connection:
            result = self.cursor.execute("INSERT INTO blacklist ('username', 'id') VALUES (?, ?)", (username, user_id,)).fetchall()
            return result

    def del_blacklist(self, user_id):
        with self.connection:
            result = self.cursor.execute("DELETE FROM blacklist WHERE id = ?", (user_id,)).fetchall()
            return result

    def add_coupon(self, coupon):
        with self.connection:
            result = self.cursor.execute("INSERT INTO coupons ('coupon') VALUES (?)", (coupon,)).fetchall()
            return result

    def check_coupon(self, coupon):
        with self.connection:
            result = self.cursor.execute("SELECT coupon FROM coupons WHERE coupon = ?", (coupon,)).fetchall()
            return bool(len(result))

    def del_coupon(self, coupon):
        with self.connection:
            result = self.cursor.execute("DELETE FROM coupons WHERE coupon = ?", (coupon,)).fetchall()
            return result

    def get_start_message(self):
        with self.connection:
            result = self.cursor.execute("SELECT text FROM panel WHERE name = ?", ('start_message',)).fetchall()[0][0]
            return result

    def get_group_text(self):
        with self.connection:
            result = self.cursor.execute("SELECT text FROM panel WHERE name = ?", ('group_link',)).fetchall()[0][0]
            return result

    def get_group_link(self):
        with self.connection:
            result = self.cursor.execute("SELECT url FROM panel WHERE name = ?", ('group_link',)).fetchall()[0][0]
            return result

    def get_chat_text(self):
        with self.connection:
            result = self.cursor.execute("SELECT text FROM panel WHERE name = ?", ('chat_link',)).fetchall()[0][0]
            return result

    def get_chat_link(self):
        with self.connection:
            result = self.cursor.execute("SELECT url FROM panel WHERE name = ?", ('chat_link',)).fetchall()[0][0]
            return result

    def get_reviews_text(self):
        with self.connection:
            result = self.cursor.execute("SELECT text FROM panel WHERE name = ?", ('reviews_link',)).fetchall()[0][0]
            return result

    def get_reviews_link(self):
        with self.connection:
            result = self.cursor.execute("SELECT url FROM panel WHERE name = ?", ('reviews_link',)).fetchall()[0][0]
            return result

    def get_admin_text(self):
        with self.connection:
            result = self.cursor.execute("SELECT text FROM panel WHERE name = ?", ('admin_link',)).fetchall()[0][0]
            return result

    def get_admin_link(self):
        with self.connection:
            result = self.cursor.execute("SELECT url FROM panel WHERE name = ?", ('admin_link',)).fetchall()[0][0]
            return result

    def edit_start_message(self, text):
        with self.connection:
            self.cursor.execute("UPDATE panel SET text = ? WHERE name = ?", (text, 'start_message',))

    def edit_group_text(self, text):
        with self.connection:
            self.cursor.execute("UPDATE panel SET text = ? WHERE name = ?", (text, 'group_link',))

    def edit_group_link(self, link):
        with self.connection:
            self.cursor.execute("UPDATE panel SET url = ? WHERE name = ?", (link, 'group_link',))

    def edit_chat_text(self, text):
        with self.connection:
            self.cursor.execute("UPDATE panel SET text = ? WHERE name = ?", (text, 'chat_link',))

    def edit_chat_link(self, link):
        with self.connection:
            self.cursor.execute("UPDATE panel SET url = ? WHERE name = ?", (link, 'chat_link',))

    def edit_reviews_text(self, text):
        with self.connection:
            self.cursor.execute("UPDATE panel SET text = ? WHERE name = ?", (text, 'reviews_link',))

    def edit_reviews_link(self, link):
        with self.connection:
            self.cursor.execute("UPDATE panel SET url = ? WHERE name = ?", (link, 'reviews_link',))

    def edit_admin_text(self, text):
        with self.connection:
            self.cursor.execute("UPDATE panel SET text = ? WHERE name = ?", (text, 'admin_link',))

    def edit_admin_link(self, link):
        with self.connection:
            self.cursor.execute("UPDATE panel SET url = ? WHERE name = ?", (link, 'admin_link',))

    def add_mass_message(self, user_id, message_id):
        with self.connection:
            self.cursor.execute("INSERT INTO mass_message ('user_id', 'message_id') VALUES (?, ?)", (user_id, message_id)).fetchall()

    def del_mass_message(self, user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM mass_message WHERE user_id = ?", (user_id,)).fetchall()

    def get_mass_message(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id, message_id FROM mass_message").fetchall()

    def flush_messages(self):
        with self.connection:
            result = self.cursor.execute(
                "DELETE FROM mass_message")