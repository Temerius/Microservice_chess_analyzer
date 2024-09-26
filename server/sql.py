import sqlite3

DATABASE = 'users.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            figure_style TEXT NOT NULL,
            board_style TEXT NOT NULL,
            bg_style TEXT NOT NULL
        )
        ''')
    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect(DATABASE)
    try:

        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password, figure_style, board_style, bg_style) VALUES (?, ?, ?, ?, ?)',
            (username, password, 'bases', 'green', 'marble'))
        conn.commit()
        return "User registered successfully!", ['bases', 'green', 'marble']
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return "Username already taken!", []
        else:
            return "Database integrity error!", []
    except sqlite3.OperationalError as e:
        return f"Operational error: {e}", []
    except Exception as e:
        return f"An error occurred: {e}", []
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect(DATABASE)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT password, figure_style, board_style, bg_style FROM users WHERE username = ?',
                       (username,))
        record = cursor.fetchone()
        if record is None:
            return "User does not exist!", []
        if record[0] == password:
            return "Login successful!", record[1:]
        else:
            return "Wrong password!", []
    except sqlite3.OperationalError as e:
        return f"Operational error: {e}", []

    except Exception as e:
        return f"An error occurred: {e}", []
    finally:
        conn.close()


def change_username(new_username, old_username):
    conn = sqlite3.connect(DATABASE)

    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET username = ? WHERE username = ?',
            (new_username, old_username)
        )
        conn.commit()

        return True, "Username successfully changed!"
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return False, "Username already taken!"
        else:
            return False, "Database integrity error!"
    except sqlite3.OperationalError as e:
        return False, f"Operational error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()


def change_password(new_password, username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:

        cursor.execute(
            'UPDATE users SET password = ? WHERE username = ?',
            ((new_password), username)
        )
        conn.commit()

        return True, "Password successfully changed!"
    except sqlite3.IntegrityError as e:
        return False, "Database integrity error!"
    except sqlite3.OperationalError as e:
        return False, f"Operational error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()


def change_figure_style(new_style, username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:

        cursor.execute(
            'UPDATE users SET figure_style = ? WHERE username = ?',
            (new_style, username)
        )
        conn.commit()

        return True, "Figure style successfully changed!"
    except sqlite3.IntegrityError as e:
        return False, "Database integrity error!"
    except sqlite3.OperationalError as e:
        return False, f"Operational error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()


def change_board_style(new_style, username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:

        cursor.execute(
            'UPDATE users SET board_style = ? WHERE username = ?',
            (new_style, username)
        )
        conn.commit()

        return True, "Board style successfully changed!"
    except sqlite3.IntegrityError as e:
        return False, "Database integrity error!"
    except sqlite3.OperationalError as e:
        return False, f"Operational error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()


def change_bg_style(new_style, username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:

        cursor.execute(
            'UPDATE users SET bg_style = ? WHERE username = ?',
            (new_style, username)
        )
        conn.commit()

        return True, "Background style successfully changed!"
    except sqlite3.IntegrityError as e:
        return False, "Database integrity error!"
    except sqlite3.OperationalError as e:
        return False, f"Operational error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()
