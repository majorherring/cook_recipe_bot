import sqlite3


DB_NAME = "recipes.db"


def create_db():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            cooking_steps TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    connect.commit()
    connect.close()


def add_user(telegram_id, username):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, username)
        VALUES (?, ?)
    """, (telegram_id, username))

    connect.commit()
    connect.close()


def get_user_id(telegram_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id FROM users
        WHERE telegram_id = ?
    """, (telegram_id,))

    result = cursor.fetchone()
    connect.close()

    if result:
        return result[0]

    return None


def add_recipe(user_id, title, category, ingredients, cooking_steps):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        INSERT INTO recipes (user_id, title, category, ingredients, cooking_steps)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, title, category, ingredients, cooking_steps))

    connect.commit()
    connect.close()


def get_all_recipes():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, title, category
        FROM recipes
        ORDER BY id DESC
    """)

    recipes = cursor.fetchall()
    connect.close()

    return recipes


def get_recipe_by_id(recipe_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT title, category, ingredients, cooking_steps
        FROM recipes
        WHERE id = ?
    """, (recipe_id,))

    recipe = cursor.fetchone()
    connect.close()

    return recipe


def search_recipes_by_title(search_text):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, title, category
        FROM recipes
        WHERE title LIKE ?
        ORDER BY id DESC
    """, (f"%{search_text}%",))

    recipes = cursor.fetchall()
    connect.close()

    return recipes


def get_recipes_by_category(category):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, title, category
        FROM recipes
        WHERE category = ?
        ORDER BY id DESC
    """, (category,))

    recipes = cursor.fetchall()
    connect.close()

    return recipes


def delete_recipe(recipe_id, user_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        DELETE FROM recipes
        WHERE id = ? AND user_id = ?
    """, (recipe_id, user_id))

    connect.commit()
    deleted_count = cursor.rowcount
    connect.close()

    return deleted_count