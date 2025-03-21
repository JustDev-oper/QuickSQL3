import aiosqlite
from typing import List, Dict, Any, Optional, Union


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

    async def command(self, command: str) -> None:
        """
        Executes a custom SQL command on the SQLite database.

        Args:
            command (str): The SQL command to be executed.

        Raises:
            ValueError: If the command is invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not command or not isinstance(command, str):
            raise ValueError("Command must be a non-empty string.")

        try:
            await self.connection.execute(command)
            await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error | Method - command: {str(e)}")

    async def read_tables(self) -> List[str]:
        """
        Retrieves a list of all tables in the current SQLite database.

        Returns:
            List[str]: A list of table names in the database. If no tables exist, an empty list is returned.
        """
        cursor = await self.connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def read_columns(self, table_name: str) -> Union[List[tuple], str]:
        """
        Retrieves metadata about the columns of a specified table.

        Args:
            table_name (str): The name of the table for which to retrieve column information.

        Returns:
            List[tuple] | str: A list of tuples containing column information or an error message.
        """
        try:
            cursor = await self.connection.execute(f"PRAGMA table_info({table_name})")
            return await cursor.fetchall()
        except aiosqlite.Error as e:
            return f"Error | Method - read_columns: {str(e)}"

    async def read_table_records(self, table_name: str) -> Union[List[tuple], str]:
        """
        Retrieves all records from a specified table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List[tuple] | str: A list of tuples containing the records or an error message.
        """
        try:
            cursor = await self.connection.execute(f"SELECT * FROM {table_name}")
            return await cursor.fetchall()
        except aiosqlite.Error as e:
            return f"Error | Method - read_table_records: {str(e)}"

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
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error creating table: {e}")

    async def add_column(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Adds one or more columns to an existing table.

        Args:
            table_name (str): The name of the table to which the columns will be added.
            columns (Dict[str, str]): A dictionary where keys are column names and values are column types.

        Raises:
            ValueError: If the table name or columns are invalid.
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not columns or not isinstance(columns, dict):
            raise ValueError("Columns must be a non-empty dictionary.")

        cursor = await self.connection.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in await cursor.fetchall()]

        if not existing_columns:
            raise ValueError(f"Table '{table_name}' does not exist.")

        for column_name, column_type in columns.items():
            if column_name in existing_columns:
                print(f"Column '{column_name}' already exists in table '{table_name}'. Skipping.")
                continue

            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            try:
                await self.connection.execute(query)
                await self.connection.commit()
            except aiosqlite.Error as e:
                raise aiosqlite.Error(f"Error adding column '{column_name}': {e}")

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
        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Error deleting records: {e}")

    async def edit_table_name(self, table_name: str, new_table_name: str) -> None:
        """
        Renames an existing table in the SQLite database.

        Args:
            table_name (str): The current name of the table to be renamed.
            new_table_name (str): The new name for the table.

        Raises:
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        try:
            await self.connection.execute(f"ALTER TABLE {table_name} RENAME TO {new_table_name}")
            await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error | Method - edit_table_name: {str(e)}")

    async def edit_column_name(self, table_name: str, column_name: str, new_column_name: str) -> None:
        """
        Renames a column in an existing table in the SQLite database.

        Args:
            table_name (str): The name of the table containing the column to be renamed.
            column_name (str): The current name of the column.
            new_column_name (str): The new name for the column.

        Raises:
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        try:
            await self.connection.execute(f"ALTER TABLE {table_name} RENAME COLUMN {column_name} TO {new_column_name}")
            await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error | Method - edit_column_name: {str(e)}")

    async def delete_table(self, table_name: str) -> None:
        """
        Deletes a table from the SQLite database.

        Args:
            table_name (str): The name of the table to be deleted.

        Raises:
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        try:
            await self.connection.execute(f"DROP TABLE {table_name}")
            await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error | Method - delete_table: {str(e)}")

    async def delete_column(self, table_name: str, column_name: str) -> None:
        """
        Deletes a column from an existing table in the SQLite database.

        Args:
            table_name (str): The name of the table from which the column will be deleted.
            column_name (str): The name of the column to be deleted.

        Raises:
            aiosqlite.Error: If an error occurs while executing the SQL command.
        """
        try:
            await self.connection.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
            await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error | Method - delete_column: {str(e)}")
