import sqlite3

from config import db_name


class Databaser:

    def __init__(self):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
    
    def try_add_user(self, uid, first_name, last_name, lang):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET lang=?, state=0 WHERE uid=?', (lang, uid))
        if cursor.rowcount == 0:
            cursor.execute('INSERT OR IGNORE INTO users (uid, first_name, last_name, lang) VALUES (?, ?, ?, ?)', (uid, first_name, last_name, lang))
        cursor.close()
        self.conn.commit()

    def get_user_lang(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT lang FROM users WHERE uid=?', (uid,))
        return cursor.fetchone()[0]

    def set_user_state(self, uid, state):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET state=? WHERE uid=?', (state, uid))
        self.conn.commit()
        cursor.close()

    def get_user_state(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT state FROM users WHERE uid=?', (uid,))
        try:
            return cursor.fetchone()[0]
        except IndexError:
            return 0

    def is_user_admin(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE uid=?', (uid,))
        try:
            if cursor.fetchone()[0] == 1:
                return True
        except IndexError:
            pass
        return False

    def set_promo(self, text, media_type, media):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE promo SET caption=?, media_type=?, media=?', (text, media_type, media))
        self.conn.commit()
        cursor.close()

    def get_promo(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM promo LIMIT 1')
        return cursor.fetchone()

    def add_to_cart(self, uid, item):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE cart SET count=count+1 WHERE uid=? AND item=?', (uid, item))
        cursor.execute('INSERT OR IGNORE INTO cart (uid, item, count) VALUES (?, ?, 1)', (uid, item))
        self.conn.commit()
        cursor.execute('SELECT count FROM cart WHERE uid=? AND item=?', (uid, item))
        ans = cursor.fetchone()[0]
        cursor.close()
        return ans

    def del_from_cart(self, uid, item):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM cart WHERE uid=? AND item=?', (uid, item))
        self.conn.commit()
        cursor.close()
    
    def decrease_from_cart(self, uid, item):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE cart SET count=count-1 WHERE uid=? AND item=?', (uid, item))
        self.conn.commit()
        cursor.execute('SELECT count FROM cart WHERE uid=? AND item=?', (uid, item))
        ans = cursor.fetchone()[0]
        cursor.close()
        return ans

    def get_user_cart(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT item, count FROM cart WHERE uid=?', (uid,))
        return cursor.fetchall()
    
    def get_user_cart_item(self, uid, item):
        cursor = self.conn.cursor()
        cursor.execute('SELECT count FROM cart WHERE uid=? AND item=?', (uid, item))
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return 0
    
    def clear_cart(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM cart WHERE uid=?', (uid,))
        self.conn.commit()
        cursor.close()

    def set_user_address_text(self, uid, address):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE locales_phones SET address=?, provided=? WHERE uid=?', (address, 'address', uid))
        cursor.execute('INSERT OR IGNORE INTO locales_phones (uid, address, provided) VALUES (?, ?, ?)', (uid, address, 'address'))
        self.conn.commit()
        cursor.close()
    
    def set_user_address_location(self, uid, lat, lon):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE locales_phones SET lat=?, lon=?, provided=? WHERE uid=?', (lat, lon, 'location', uid))
        cursor.execute('INSERT OR IGNORE INTO locales_phones (uid, lat, lon, provided) VALUES (?, ?, ?, ?)', (uid, lat, lon, 'location'))
        self.conn.commit()
        cursor.close()
    
    def set_user_phone(self, uid, phone):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE locales_phones SET phone=? WHERE uid=?', (phone, uid))
        self.conn.commit()
        cursor.close()
    
    def what_is_provided(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT provided FROM locales_phones WHERE uid=?', (uid,))
        return cursor.fetchone()[0]
    
    def get_address(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT address FROM locales_phones WHERE uid=?', (uid,))
        return cursor.fetchone()[0]
    
    def get_location(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT lat, lon FROM locales_phones WHERE uid=?', (uid,))
        return cursor.fetchone()
    
    def set_way(self, uid, way):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE locales_phones SET way=? WHERE uid=?', (way, uid))
        self.conn.commit()
        cursor.close()
    
    def get_way(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT way FROM locales_phones WHERE uid=?', (uid,))
        return cursor.fetchone()[0]
    
    def get_phone(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT phone FROM locales_phones WHERE uid=?', (uid,))
        return cursor.fetchone()
    
    def get_admin_ids(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT uid FROM users WHERE is_admin=1')
        return cursor.fetchall()
    
    # def add_order(self, uid, desc, total_price, phone, address, lat, lon, provided):
    #     cursor = self.conn.cursor()
    #     cursor.execute(
    #         'INSERT INTO orders (uid, desc, total_price, phone, address, lat, lon, provided) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    #         (uid, desc, total_price, phone, address, lat, lon, provided)
    #     )
    #     self.conn.commit()
    #     cursor.close()
