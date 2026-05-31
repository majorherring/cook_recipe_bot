from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить рецепт")],
        [KeyboardButton(text="📖 Все рецепты"), KeyboardButton(text="🔍 Поиск рецепта")],
        [KeyboardButton(text="🍲 Рецепты по категории"), KeyboardButton(text="❌ Удалить рецепт")]
    ],
    resize_keyboard=True
)


category_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Завтрак"), KeyboardButton(text="Обед")],
        [KeyboardButton(text="Ужин"), KeyboardButton(text="Десерт")],
        [KeyboardButton(text="Напиток"), KeyboardButton(text="Другое")]
    ],
    resize_keyboard=True
)


def recipes_inline_keyboard(recipes):
    buttons = []

    for recipe in recipes:
        recipe_id, title, category = recipe
        buttons.append([
            InlineKeyboardButton(
                text=f"{title} ({category})",
                callback_data=f"recipe_{recipe_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def delete_inline_keyboard(recipes):
    buttons = []

    for recipe in recipes:
        recipe_id, title, category = recipe
        buttons.append([
            InlineKeyboardButton(
                text=f"Удалить: {title}",
                callback_data=f"delete_{recipe_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)