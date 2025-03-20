from QuickSQL3 import Database

# Создаем базу данных (файл "app.db" будет создан автоматически)
db = Database("app.db")

# Создаем таблицу "users"
db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "age": "INTEGER"
})

# Вставляем данные в таблицу "users"
db.insert("users", {"name": "Алиса", "age": 25})
db.insert("users", {"name": "Боб", "age": 30})
db.insert("users", {"name": "Чарли", "age": 35})

# Выбираем всех пользователей старше 20 лет
users = db.select("users", where="age > 20")
print("Пользователи старше 20 лет:")
for user in users:
    print(user)

# Обновляем возраст пользователя с именем "Алиса"
db.update("users", {"age": 26}, where="name = 'Алиса'")

# Проверяем обновленные данные
updated_users = db.select("users", where="name = 'Алиса'")
print("\nОбновленные данные Алисы:")
for user in updated_users:
    print(user)

# Удаляем пользователей младше 18 лет (в данном случае никого не удалит)
db.delete("users", where="age < 18")

# Закрываем соединение с базой данных
db.close()
