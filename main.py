import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import (
    create_db,
    add_user,
    get_user_id,
    add_recipe,
    get_all_recipes,
    get_recipe_by_id,
    search_recipes_by_title,
    get_recipes_by_category,
    delete_recipe
)

from keyboards import (
    main_keyboard,
    category_keyboard,
    recipes_inline_keyboard,
    delete_inline_keyboard
)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class AddRecipe(StatesGroup):
    title = State()
    category = State()
    ingredients = State()
    cooking_steps = State()


class SearchRecipe(StatesGroup):
    search_text = State()


class CategorySearch(StatesGroup):
    category = State()


@dp.message(CommandStart())
async def start_handler(message: Message):
    add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    await message.answer(
        "Здравствуйте! Я бот «Книга рецептов».\n\n"
        "С моей помощью можно:\n"
        "➕ добавлять рецепты;\n"
        "📖 просматривать книгу рецептов;\n"
        "🔍 искать рецепты по названию;\n"
        "🍲 фильтровать рецепты по категории;\n"
        "❌ удалять свои рецепты.",
        reply_markup=main_keyboard
    )


@dp.message(F.text == "➕ Добавить рецепт")
async def add_recipe_start(message: Message, state: FSMContext):
    await state.set_state(AddRecipe.title)
    await message.answer("Введите название рецепта:")


@dp.message(AddRecipe.title)
async def add_recipe_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddRecipe.category)

    await message.answer(
        "Выберите категорию рецепта:",
        reply_markup=category_keyboard
    )


@dp.message(AddRecipe.category)
async def add_recipe_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddRecipe.ingredients)

    await message.answer(
        "Введите ингредиенты рецепта.\n\n"
        "Например:\n"
        "Картофель — 500 г\n"
        "Мясо — 300 г\n"
        "Соль — по вкусу"
    )


@dp.message(AddRecipe.ingredients)
async def add_recipe_ingredients(message: Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await state.set_state(AddRecipe.cooking_steps)

    await message.answer(
        "Введите способ приготовления рецепта:"
    )


@dp.message(AddRecipe.cooking_steps)
async def add_recipe_steps(message: Message, state: FSMContext):
    data = await state.get_data()

    user_id = get_user_id(message.from_user.id)

    add_recipe(
        user_id=user_id,
        title=data["title"],
        category=data["category"],
        ingredients=data["ingredients"],
        cooking_steps=message.text
    )

    await state.clear()

    await message.answer(
        "Рецепт успешно добавлен в книгу рецептов!",
        reply_markup=main_keyboard
    )


@dp.message(F.text == "📖 Все рецепты")
async def show_all_recipes(message: Message):
    recipes = get_all_recipes()

    if not recipes:
        await message.answer("В книге рецептов пока нет записей.")
        return

    await message.answer(
        "Выберите рецепт для просмотра:",
        reply_markup=recipes_inline_keyboard(recipes)
    )


@dp.callback_query(F.data.startswith("recipe_"))
async def show_recipe(callback: CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        await callback.message.answer("Рецепт не найден.")
        await callback.answer()
        return

    title, category, ingredients, cooking_steps = recipe

    text = (
        f"🍽 <b>{title}</b>\n\n"
        f"Категория: {category}\n\n"
        f"🧂 <b>Ингредиенты:</b>\n"
        f"{ingredients}\n\n"
        f"👨‍🍳 <b>Способ приготовления:</b>\n"
        f"{cooking_steps}"
    )

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.message(F.text == "🔍 Поиск рецепта")
async def search_recipe_start(message: Message, state: FSMContext):
    await state.set_state(SearchRecipe.search_text)
    await message.answer("Введите название или часть названия рецепта:")


@dp.message(SearchRecipe.search_text)
async def search_recipe_result(message: Message, state: FSMContext):
    recipes = search_recipes_by_title(message.text)

    await state.clear()

    if not recipes:
        await message.answer(
            "По вашему запросу рецепты не найдены.",
            reply_markup=main_keyboard
        )
        return

    await message.answer(
        "Найденные рецепты:",
        reply_markup=recipes_inline_keyboard(recipes)
    )


@dp.message(F.text == "🍲 Рецепты по категории")
async def category_search_start(message: Message, state: FSMContext):
    await state.set_state(CategorySearch.category)

    await message.answer(
        "Выберите категорию:",
        reply_markup=category_keyboard
    )


@dp.message(CategorySearch.category)
async def category_search_result(message: Message, state: FSMContext):
    recipes = get_recipes_by_category(message.text)

    await state.clear()

    if not recipes:
        await message.answer(
            "В выбранной категории рецептов нет.",
            reply_markup=main_keyboard
        )
        return

    await message.answer(
        f"Рецепты в категории «{message.text}»:",
        reply_markup=recipes_inline_keyboard(recipes)
    )


@dp.message(F.text == "❌ Удалить рецепт")
async def delete_recipe_start(message: Message):
    recipes = get_all_recipes()

    if not recipes:
        await message.answer("Удалять нечего. В книге рецептов пока нет записей.")
        return

    await message.answer(
        "Выберите рецепт для удаления:",
        reply_markup=delete_inline_keyboard(recipes)
    )


@dp.callback_query(F.data.startswith("delete_"))
async def delete_recipe_callback(callback: CallbackQuery):
    recipe_id = int(callback.data.split("_")[1])
    user_id = get_user_id(callback.from_user.id)

    result = delete_recipe(recipe_id, user_id)

    if result > 0:
        await callback.message.answer("Рецепт успешно удалён.")
    else:
        await callback.message.answer(
            "Вы не можете удалить этот рецепт, так как он был добавлен другим пользователем."
        )

    await callback.answer()


@dp.message()
async def unknown_message(message: Message):
    await message.answer(
        "Я не понял команду. Используйте кнопки меню.",
        reply_markup=main_keyboard
    )


async def main():
    create_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())