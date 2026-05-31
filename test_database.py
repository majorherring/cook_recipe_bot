import os
import unittest
import tempfile

import database


class TestRecipeDatabase(unittest.TestCase):

    def setUp(self):
        """
        Метод выполняется перед каждым тестом.
        Создаётся временная база данных, чтобы тесты
        не изменяли основную базу recipes.db.
        """
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()

        database.DB_NAME = self.test_db.name
        database.create_db()

    def tearDown(self):
        """
        Метод выполняется после каждого теста.
        Временная база данных удаляется.
        """
        os.remove(self.test_db.name)

    def test_add_user(self):
        """
        Проверка добавления пользователя в базу данных.
        """
        database.add_user(telegram_id=12345, username="test_user")

        user_id = database.get_user_id(telegram_id=12345)

        self.assertIsNotNone(user_id)
        self.assertIsInstance(user_id, int)

    def test_add_recipe(self):
        """
        Проверка добавления рецепта в базу данных.
        """
        database.add_user(telegram_id=12345, username="test_user")
        user_id = database.get_user_id(telegram_id=12345)

        database.add_recipe(
            user_id=user_id,
            title="Борщ",
            category="Обед",
            ingredients="Свёкла, капуста, картофель, мясо",
            cooking_steps="Сварить мясо, добавить овощи и варить до готовности."
        )

        recipes = database.get_all_recipes()

        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0][1], "Борщ")
        self.assertEqual(recipes[0][2], "Обед")

    def test_get_recipe_by_id(self):
        """
        Проверка получения рецепта по ID.
        """
        database.add_user(telegram_id=12345, username="test_user")
        user_id = database.get_user_id(telegram_id=12345)

        database.add_recipe(
            user_id=user_id,
            title="Сырники",
            category="Завтрак",
            ingredients="Творог, яйцо, мука, сахар",
            cooking_steps="Смешать ингредиенты и обжарить на сковороде."
        )

        recipes = database.get_all_recipes()
        recipe_id = recipes[0][0]

        recipe = database.get_recipe_by_id(recipe_id)

        self.assertIsNotNone(recipe)
        self.assertEqual(recipe[0], "Сырники")
        self.assertEqual(recipe[1], "Завтрак")

    def test_search_recipes_by_title(self):
        """
        Проверка поиска рецепта по названию.
        """
        database.add_user(telegram_id=12345, username="test_user")
        user_id = database.get_user_id(telegram_id=12345)

        database.add_recipe(
            user_id=user_id,
            title="Паста с курицей",
            category="Ужин",
            ingredients="Макароны, курица, сливки, сыр",
            cooking_steps="Отварить макароны, обжарить курицу и смешать со сливками."
        )

        result = database.search_recipes_by_title("Паста")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Паста с курицей")

    def test_get_recipes_by_category(self):
        """
        Проверка фильтрации рецептов по категории.
        """
        database.add_user(telegram_id=12345, username="test_user")
        user_id = database.get_user_id(telegram_id=12345)

        database.add_recipe(
            user_id=user_id,
            title="Шоколадный кекс",
            category="Десерт",
            ingredients="Мука, сахар, какао, яйца",
            cooking_steps="Смешать ингредиенты и выпекать в духовке."
        )

        result = database.get_recipes_by_category("Десерт")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Шоколадный кекс")
        self.assertEqual(result[0][2], "Десерт")

    def test_delete_recipe(self):
        """
        Проверка удаления рецепта пользователем, который его добавил.
        """
        database.add_user(telegram_id=12345, username="test_user")
        user_id = database.get_user_id(telegram_id=12345)

        database.add_recipe(
            user_id=user_id,
            title="Овощной салат",
            category="Обед",
            ingredients="Огурцы, помидоры, перец, зелень",
            cooking_steps="Нарезать овощи и перемешать."
        )

        recipes = database.get_all_recipes()
        recipe_id = recipes[0][0]

        deleted_count = database.delete_recipe(recipe_id, user_id)

        recipes_after_delete = database.get_all_recipes()

        self.assertEqual(deleted_count, 1)
        self.assertEqual(len(recipes_after_delete), 0)

    def test_user_cannot_delete_other_user_recipe(self):
        """
        Проверка запрета удаления чужого рецепта.
        """
        database.add_user(telegram_id=11111, username="first_user")
        database.add_user(telegram_id=22222, username="second_user")

        first_user_id = database.get_user_id(telegram_id=11111)
        second_user_id = database.get_user_id(telegram_id=22222)

        database.add_recipe(
            user_id=first_user_id,
            title="Борщ",
            category="Обед",
            ingredients="Свёкла, капуста, мясо",
            cooking_steps="Сварить бульон, добавить овощи."
        )

        recipes = database.get_all_recipes()
        recipe_id = recipes[0][0]

        deleted_count = database.delete_recipe(recipe_id, second_user_id)

        recipes_after_delete = database.get_all_recipes()

        self.assertEqual(deleted_count, 0)
        self.assertEqual(len(recipes_after_delete), 1)


if __name__ == "__main__":
    unittest.main()