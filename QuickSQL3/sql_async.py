import aiosqlite
from typing import List, Dict, Any, Optional


class AsyncDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    async def connect(self) -> None:
        """
        Establishes a connection to the SQLite database.
        """
        self.connection = await aiosqlite.connect(self.db_path)

    async def close(self) -> None:
        """
        Closes the connection to the database.
        """
        if self.connection:
            await self.connection.close()
            print("Database connection closed.")

    async def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Creates a new table in the database.

        Args:
            table_name (str): The name of the table to be created.
            columns (Dict[str, str]): A dictionary where keys are column names and values are column types.

        Raises:
            ValueError: If the table name or columns are invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not columns or not isinstance(columns, dict):
            raise ValueError("Columns must be a non-empty dictionary.")

        columns_with_types = ", ".join([f"{name} {type}" for name, type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"

        try:
            await self.connection.execute(query)
            await self.connection.commit()
            print(f"Table '{table_name}' created successfully.")
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error creating table: {e}")

    async def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Inserts a new record into the specified table.

        Args:
            table_name (str): The name of the table.
            data (Dict[str, Any]): A dictionary where keys are column names and values are the data to insert.

        Raises:
            ValueError: If the table name or data is invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not data or not isinstance(data, dict):
            raise ValueError("Data must be a non-empty dictionary.")

        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            await self.connection.execute(query, tuple(data.values()))
            await self.connection.commit()
            print(f"Record inserted into table '{table_name}' successfully.")
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error inserting record: {e}")

    async def select(self, table_name: str, where: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Selects records from the specified table.

        Args:
            table_name (str): The name of the table.
            where (Optional[str]): The WHERE clause to filter records (e.g., "age > 20").

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the selected records.

        Raises:
            ValueError: If the table name is invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        query = f"SELECT * FROM {table_name}"
        if where:
            query += f" WHERE {where}"

        try:
            cursor = await self.connection.execute(query)
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error selecting records: {e}")

    async def update(self, table_name: str, data: Dict[str, Any], where: str) -> None:
        """
        Updates records in the specified table.

        Args:
            table_name (str): The name of the table.
            data (Dict[str, Any]): A dictionary where keys are column names and values are the new data.
            where (str): The WHERE clause to specify which records to update (e.g., "name = 'Alice'").

        Raises:
            ValueError: If the table name, data, or WHERE clause is invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not data or not isinstance(data, dict):
            raise ValueError("Data must be a non-empty dictionary.")

        if not where or not isinstance(where, str):
            raise ValueError("WHERE clause must be a non-empty string.")

        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"

        try:
            await self.connection.execute(query, tuple(data.values()))
            await self.connection.commit()
            print(f"Records in table '{table_name}' updated successfully.")
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error updating records: {e}")

    async def delete(self, table_name: str, where: str) -> None:
        """
        Deletes records from the specified table.

        Args:
            table_name (str): The name of the table.
            where (str): The WHERE clause to specify which records to delete (e.g., "age < 18").

        Raises:
            ValueError: If the table name or WHERE clause is invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not where or not isinstance(where, str):
            raise ValueError("WHERE clause must be a non-empty string.")

        query = f"DELETE FROM {table_name} WHERE {where}"

        try:
            await self.connection.execute(query)
            await self.connection.commit()
            print(f"Records from table '{table_name}' deleted successfully.")
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error deleting records: {e}")
