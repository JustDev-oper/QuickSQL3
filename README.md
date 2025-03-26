# QuickSQL3

[English](#english) | [Русский](#русский)

---

## English <a name="english"></a>

QuickSQL3 is a Python library designed to simplify working with SQLite databases. It provides both synchronous and asynchronous APIs for performing common database operations with SQLite. The library is ideal for developers who want an intuitive interface for database operations without writing raw SQL queries.

## Features

- **Dual APIs**: Choose between synchronous (`Database`) and asynchronous (`AsyncDatabase`) interfaces
- **Comprehensive CRUD**: Create, Read, Update, Delete operations with simple method calls
- **Schema Management**: Create tables, alter columns, rename tables, and more
- **Type Safety**: Full type annotations for better code clarity and IDE support
- **Error Handling**: Built-in error handling with detailed logging
- **Flexible Querying**: Support for WHERE clauses, parameterized queries, sorting, and pagination

## Installation

Install using pip:

```bash
pip install QuickSQL3
```

## Documentation

### Synchronous API (`Database`)

```python
from QuickSQL3 import Database

# Initialize database
db = Database("app.db")

# Table operations
db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
db.edit_table_name("users", "customers")
db.add_column("customers", {"email": "TEXT UNIQUE"})

# Data operations
row_id = db.insert("customers", {"name": "Alice", "email": "alice@example.com"})
results = db.select("customers", where="name LIKE ?", params=("A%",))
db.update("customers", {"email": "new@example.com"}, where="id = ?", params=(row_id,))
db.delete("customers", where="id = ?", params=(row_id,))

# Close connection
db.close()
```

### Asynchronous API (`AsyncDatabase`)

```python
from QuickSQL3 import AsyncDatabase

async def main():
    # Initialize database
    db = AsyncDatabase("app.db")
    await db.connect()
    
    # Table operations
    await db.create_table("products", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
    await db.edit_column_name("products", "name", "product_name")
    
    # Data operations
    await db.insert("products", {"product_name": "Laptop"})
    results = await db.select("products")
    
    # Close connection
    await db.close()
```

## Examples

### Basic Usage

```python
from QuickSQL3 import Database

with Database("example.db") as db:
    # Create table
    db.create_table("employees", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "salary": "REAL"
    })
    
    # Insert data
    db.insert("employees", {"name": "John Doe", "salary": 75000.50})
    
    # Query data
    employees = db.select("employees", where="salary > ?", params=(50000,))
    print(employees)
```

### Advanced Querying

```python
# Complex query with sorting and pagination
results = db.select(
    "orders",
    where="customer_id = ? AND date > ?",
    params=(123, "2023-01-01"),
    columns=["id", "total", "status"],
    order_by="total DESC",
    limit=10,
    offset=5
)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

MIT License

---

## Русский <a name="русский"></a>

QuickSQL3 — это Python-библиотека для удобной работы с базами данных SQLite. Она предоставляет как синхронный, так и асинхронный API для выполнения стандартных операций с базой данных без необходимости писать сырые SQL-запросы.

## Возможности

- **Двойной API**: На выбор синхронный (`Database`) и асинхронный (`AsyncDatabase`) интерфейсы
- **Полный CRUD**: Создание, чтение, обновление и удаление данных простыми методами
- **Управление схемой**: Создание таблиц, изменение столбцов, переименование таблиц
- **Типизация**: Полная поддержка аннотаций типов для удобства разработки
- **Обработка ошибок**: Встроенная система обработки ошибок с детальным логированием
- **Гибкие запросы**: Поддержка условий WHERE, параметризованных запросов, сортировки и пагинации

## Установка

Установка через pip:

```bash
pip install QuickSQL3
```

## Документация

### Синхронный API (`Database`)

```python
from QuickSQL3 import Database

# Инициализация базы данных
db = Database("app.db")

# Операции с таблицами
db.create_table("пользователи", {"id": "INTEGER PRIMARY KEY", "имя": "TEXT"})
db.edit_table_name("пользователи", "клиенты")
db.add_column("клиенты", {"email": "TEXT UNIQUE"})

# Операции с данными
row_id = db.insert("клиенты", {"имя": "Алиса", "email": "alice@example.com"})
results = db.select("клиенты", where="имя LIKE ?", params=("А%",))
db.update("клиенты", {"email": "new@example.com"}, where="id = ?", params=(row_id,))
db.delete("клиенты", where="id = ?", params=(row_id,))

# Закрытие соединения
db.close()
```

### Асинхронный API (`AsyncDatabase`)

```python
from QuickSQL3 import AsyncDatabase

async def main():
    # Инициализация базы данных
    db = AsyncDatabase("app.db")
    await db.connect()
    
    # Операции с таблицами
    await db.create_table("товары", {"id": "INTEGER PRIMARY KEY", "название": "TEXT"})
    await db.edit_column_name("товары", "название", "имя_товара")
    
    # Операции с данными
    await db.insert("товары", {"имя_товара": "Ноутбук"})
    results = await db.select("товары")
    
    # Закрытие соединения
    await db.close()
```

## Примеры

### Базовое использование

```python
from QuickSQL3 import Database

with Database("example.db") as db:
    # Создание таблицы
    db.create_table("сотрудники", {
        "id": "INTEGER PRIMARY KEY",
        "имя": "TEXT NOT NULL",
        "зарплата": "REAL"
    })
    
    # Вставка данных
    db.insert("сотрудники", {"имя": "Иван Иванов", "зарплата": 75000.50})

    # Запрос данных
    employees = db.select("сотрудники", where="зарплата > ?", params=(50000,))
    print(employees)
```

## Участие

Приветствуются contributions! Создавайте issue или отправляйте pull request на GitHub.

## Лицензия

MIT License