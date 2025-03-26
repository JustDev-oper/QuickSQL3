from QuickSQL3 import Database


def main():
    # Используем контекстный менеджер для автоматического управления соединением
    with Database("app.db") as db:
        # Создаем таблицу "users" с улучшенным синтаксисом
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "age": "INTEGER DEFAULT 18",
            "email": "TEXT UNIQUE"
        })

        # Добавляем колонку "registration_date" после создания таблицы
        db.add_column("users", {
            "registration_date": "TEXT DEFAULT CURRENT_TIMESTAMP"
        })

        # Вставляем данные с использованием параметризованных запросов
        users_data = [
            {"name": "Алиса", "age": 25, "email": "alice@example.com"},
            {"name": "Боб", "age": 30, "email": "bob@example.com"},
            {"name": "Чарли", "age": 35, "email": "charlie@example.com"}
        ]

        # Пакетная вставка через executemany
        with db.connection:  # Транзакция
            for user in users_data:
                user_id = db.insert("users", user)
                print(f"Добавлен пользователь с ID: {user_id}")

        # Выбираем пользователей с параметризованным запросом
        adult_users = db.select(
            "users",
            where="age > ?",
            params=(20,),
            columns=["id", "name", "email", "age"],
            order_by="age DESC"
        )

        print("\nПользователи старше 20 лет:")
        for user in adult_users:
            print(f"ID: {user['id']}, Имя: {user['name']}, Email: {user['email']}, Возраст: {user['age']}")

        # Обновляем данные с параметрами
        update_count = db.update(
            "users",
            data={"age": 26},
            where="name = ?",
            params=("Алиса",)
        )
        print(f"\nОбновлено записей: {update_count}")

        # Проверяем обновленные данные
        alice_data = db.select(
            "users",
            where="name = ?",
            params=("Алиса",),
            fetch=True  # Получаем только одну запись
        )
        print("\nОбновленные данные Алисы:")
        print(alice_data)

        # Удаление с проверкой результата
        deleted_count = db.delete(
            "users",
            where="age < ?",
            params=(18,)
        )
        print(f"\nУдалено пользователей младше 18 лет: {deleted_count}")

        # Работа с произвольными SQL-запросами
        top_users = db.command(
            "SELECT name, age FROM users ORDER BY age DESC LIMIT ?",
            params=(2,),
            fetch_all=True
        )
        print("\nТоп-2 самых старших пользователя:")
        for user in top_users:
            print(f"{user['name']} ({user['age']} лет)")

        # Просмотр структуры таблицы
        print("\nСтруктура таблицы users:")
        for column in db.read_columns("users"):
            print(f"{column[1]}: {column[2]}{' NOT NULL' if column[3] else ''}")


if __name__ == "__main__":
    main()
