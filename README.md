# QuickSQL3

[English](#english) | [Русский](#русский)

---

## English <a name="english"></a>

QuickSQL3 is a Python library designed to simplify working with SQLite databases. It provides an intuitive API for
performing common database operations such as creating tables, inserting data, querying, updating, and deleting records.
The library is ideal for beginners or those who want to avoid writing raw SQL queries.

## Features

- **Simple API**: Easily create tables, insert data, and query records without writing SQL.
- **Error Handling**: Built-in error handling to help you debug issues.
- **Flexible**: Supports both synchronous and asynchronous operations.
- **Type Annotations**: Fully typed for better code clarity and IDE support.

## Installation

You can install the library using pip:

```bash
pip install QuickSQL3
```

## Documentation

### Synchronous Methods

```python
from QuickSQL3 import Database

create_table(table_name: str, columns: Dict[str, str]) -> None

insert(table_name: str, data: Dict[str, Any]) -> None

select(table_name: str, where: Optional[str] = None) -> List[Dict[str, Any]]

update(table_name: str, data: Dict[str, Any], where: str) -> None

delete(table_name: str, where: str) -> None

close() -> None
```

### Asynchronous Methods

```python
from QuickSQL3 import AsyncDatabase

create_table(table_name: str, columns: Dict[str, str]) -> None

insert(table_name: str, data: Dict[str, Any]) -> None

select(table_name: str, where: Optional[str] = None) -> List[Dict[str, Any]]

update(table_name: str, data: Dict[str, Any], where: str) -> None

delete(table_name: str, where: str) -> None

close() -> None
```

## Example

```python
from QuickSQL3 import Database

db = Database("app.db")

db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "age": "INTEGER"
})

db.insert("users", {"name": "Алиса", "age": 25})
db.insert("users", {"name": "Боб", "age": 30})
db.insert("users", {"name": "Чарли", "age": 35})

users = db.select("users", where="age > 20")
print("Пользователи старше 20 лет:")
for user in users:
    print(user)

db.update("users", {"age": 26}, where="name = 'Алиса'")

updated_users = db.select("users", where="name = 'Алиса'")
print("\nОбновленные данные Алисы:")
for user in updated_users:
    print(user)

db.delete("users", where="age < 18")

db.close()
```

## Contributing

### Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

### This project is licensed under the MIT License.

---

## Русский <a name="русский"></a>

QuickSQL3 — это библиотека на Python, предназначенная для упрощения работы с базами данных SQLite. Она предоставляет
интуитивно понятный API для выполнения таких операций, как создание таблиц, вставка данных, запросы, обновление и
удаление записей. Библиотека идеально подходит для новичков или тех, кто хочет избежать написания сырых SQL-запросов.

## Возможности

- **Простой API**: Легко создавайте таблицы, вставляйте данные и выполняйте запросы без написания SQL.
- **Обработка ошибок**: Встроенная обработка ошибок для упрощения отладки.
- **Гибкость**: Поддержка как синхронных, так и асинхронных операций.
- **Типизация**: Полная поддержка аннотаций типов для улучшения читаемости кода и поддержки IDE.

## Установка

Установите библиотеку с помощью pip:

```bash
pip install QuickSQL3
```

## Документация

### Синхронные методы

```python
from QuickSQL3 import Database

create_table(table_name: str, columns: Dict[str, str]) -> None

insert(table_name: str, data: Dict[str, Any]) -> None

select(table_name: str, where: Optional[str] = None) -> List[Dict[str, Any]]

update(table_name: str, data: Dict[str, Any], where: str) -> None

delete(table_name: str, where: str) -> None

close() -> None
```

### Асинхронные методы

```python
from QuickSQL3 import AsyncDatabase

create_table(table_name: str, columns: Dict[str, str]) -> None

insert(table_name: str, data: Dict[str, Any]) -> None

select(table_name: str, where: Optional[str] = None) -> List[Dict[str, Any]]

update(table_name: str, data: Dict[str, Any], where: str) -> None

delete(table_name: str, where: str) -> None

close() -> None
```

## Пример

```python
from QuickSQL3 import Database

db = Database("app.db")

db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "age": "INTEGER"
})

db.insert("users", {"name": "Алиса", "age": 25})
db.insert("users", {"name": "Боб", "age": 30})
db.insert("users", {"name": "Чарли", "age": 35})

users = db.select("users", where="age > 20")
print("Пользователи старше 20 лет:")
for user in users:
    print(user)

db.update("users", {"age": 26}, where="name = 'Алиса'")

updated_users = db.select("users", where="name = 'Алиса'")
print("\nОбновленные данные Алисы:")
for user in updated_users:
    print(user)

db.delete("users", where="age < 18")

db.close()
```

## Участие

### Мы приветствуем ваши contributions! Пожалуйста, создайте issue или отправьте pull request на GitHub.

## Лицензия

### Этот проект лицензирован под MIT License.