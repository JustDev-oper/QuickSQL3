import sqlite3
from typing import List, Any, Dict, Optional


class Database:
    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    ### Misc - Start ###
    def command(self, command: str) -> None:
        """
        Executes a custom SQL command on the SQLite database.

        This method allows you to execute any valid SQL command (e.g., CREATE, INSERT, UPDATE, DELETE, etc.).
        Use it for advanced operations that are not covered by other methods in the class.

        Args:
            command (str): The SQL command to be executed.

        Returns:
            None

        Raises:
            sqlite3.Error: If an error occurs while executing the SQL command (e.g., syntax error, table does not exist).
        """
        try:
            self.cursor.execute(command)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error | Method - command: {str(e)}")

    def close(self) -> None:
        """
        Closes the connection to the database.
        """
        self.connection.close()
        print("Database connection closed.")

    ### Misc - End ####

    def read_tables(self) -> List[str]:
        """
            Retrieves a list of all tables in the current SQLite database.

            This method queries the `sqlite_master` system table, which contains metadata about all
            database objects (tables, indexes, etc.). It filters the results to return only the names
            of tables (excluding views, indexes, etc.).

            Returns:
                List[str]: A list of table names in the database. If no tables exist, an empty list is returned.

            Example:
                --> db = DataBase("example.db")
                --> db.read_tables()
                ['users', 'products', 'orders']

                --> db.read_tables()  # No tables in the database
                []
            """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return list(map(lambda row: row[0], list(self.cursor.fetchall())))

    def read_columns(self, table_name: str) -> List[tuple] | str:
        """
    Retrieves metadata about the columns of a specified table.

    This method executes the SQLite `PRAGMA table_info(table_name)` command, which returns
    a list of tuples containing information about each column in the table, such as its name,
    data type, whether it can be NULL, and whether it is part of the primary key.

    Args:
        table_name (str): The name of the table for which to retrieve column information.

    Returns:
        List[tuple] | str:
            - If successful, returns a list of tuples, where each tuple represents a column.
              Each tuple contains the following elements:
                - 0: Column index (starting from 0).
                - 1: Column name.
                - 2: Column data type.
                - 3: Whether the column can be NULL (0 = no, 1 = yes).
                - 4: Default value of the column (or None if not specified).
                - 5: Whether the column is part of the primary key (0 = no, 1 = yes).
            - If an error occurs (e.g., the table does not exist), returns an error message as a string.

    Example:
        --> db = DataBase("example.db")
        --> db.read_columns("users")
        [(0, 'id', 'INTEGER', 1, None, 1), (1, 'name', 'TEXT', 1, None, 0)]

        --> db.read_columns("non_existent_table")
        "Error! Check your table name."
    """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.cursor.fetchall()

        except sqlite3.Error as e:
            print(f"Error | Method - read_columns: {str(e)}")

    def read_table_records(self, table_name: str) -> List[tuple] | str:
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error | Method - read_table_records: {str(e)}")

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Creates a new table in the database.

        Args:
            table_name (str): The name of the table to be created.
            columns (Dict[str, str]): A dictionary where keys are column names and values are column types.

        Raises:
            ValueError: If the table name or columns are invalid.
            sqlite3.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not columns or not isinstance(columns, dict):
            raise ValueError("Columns must be a non-empty dictionary.")

        columns_with_types = ", ".join([f"{name} {type}" for name, type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Error creating table: {e}")

    def add_column(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Adds one or more columns to an existing table.

        Args:
            table_name (str): The name of the table to which the columns will be added.
            columns (Dict[str, str]): A dictionary where keys are column names and values are column types.

        Raises:
            ValueError: If the table name or columns are invalid.
            sqlite3.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not columns or not isinstance(columns, dict):
            raise ValueError("Columns must be a non-empty dictionary.")

        self.cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in self.cursor.fetchall()]

        if not existing_columns:
            raise ValueError(f"Table '{table_name}' does not exist.")

        for column_name, column_type in columns.items():
            if column_name in existing_columns:
                print(f"Column '{column_name}' already exists in table '{table_name}'. Skipping.")
                continue

            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            try:
                self.cursor.execute(query)
                self.connection.commit()
                print(f"Column '{column_name}' added to table '{table_name}' successfully.")
            except sqlite3.Error as e:
                raise sqlite3.Error(f"Error adding column '{column_name}': {e}")

    def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        """
    Inserts a new record into the specified table.

    Args:
        table_name (str): The name of the table.
        data (Dict[str, Any]): A dictionary where keys are column names and values are the data to insert.

    Raises:
        ValueError: If the table name or data is invalid.
        sqlite3.Error: If an error occurs while executing the SQL command.

    Example:
        # Insert a single record
        db.insert("users", {"name": "Alice", "age": 25})

        # Insert multiple records (using a loop)
        records = [
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35},
        ]
        for record in records:
            db.insert("users", record)
    """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not data or not isinstance(data, dict):
            raise ValueError("Data must be a non-empty dictionary.")

        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Error inserting record: {e}")

    def select(self, table_name: str, where: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Selects records from the specified table.

        Args:
            table_name (str): The name of the table.
            where (Optional[str]): The WHERE clause to filter records (e.g., "age > 20").

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the selected records.

        Raises:
            ValueError: If the table name is invalid.
            sqlite3.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        query = f"SELECT * FROM {table_name}"
        if where:
            query += f" WHERE {where}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Error selecting records: {e}")

    def edit_table_name(self, table_name: str, new_table_name: str) -> None:
        """
            Renames an existing table in the SQLite database.

            Args:
                table_name (str): The current name of the table to be renamed.
                new_table_name (str): The new name for the table.

            Returns:
                None

            Raises:
                sqlite3.Error: If an error occurs while executing the SQL command (e.g., the table does not exist
                               or the new table name is already in use).
            """
        try:
            self.cursor.execute(f"ALTER TABLE {table_name} RENAME TO {new_table_name}")
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error | Method - edit_table_name: {str(e)}")

    def edit_column_name(self, table_name: str, column_name: str, new_column_name: str) -> None:
        """
            Renames a column in an existing table in the SQLite database.

            Args:
                table_name (str): The name of the table containing the column to be renamed.
                column_name (str): The current name of the column.
                new_column_name (str): The new name for the column.

            Returns:
                None

            Raises:
                sqlite3.Error: If an error occurs while executing the SQL command (e.g., the table or column does not exist
                               or the new column name is already in use).
            """
        try:
            self.cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {column_name} TO {new_column_name}")
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error | Method - edit_column_name: {str(e)}")

    def update(self, table_name: str, data: Dict[str, Any], where: str) -> None:
        """
        Updates records in the specified table.

        Args:
            table_name (str): The name of the table.
            data (Dict[str, Any]): A dictionary where keys are column names and values are the new data.
            where (str): The WHERE clause to specify which records to update (e.g., "name = 'Alice'").

        Raises:
            ValueError: If the table name, data, or WHERE clause is invalid.
            sqlite3.Error: If an error occurs while executing the SQL command.
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
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Error updating records: {e}")

    def delete_table(self, table_name: str) -> None:
        """
            Deletes a table from the SQLite database.

            Args:
                table_name (str): The name of the table to be deleted.

            Returns:
                None

            Raises:
                sqlite3.Error: If an error occurs while executing the SQL command (e.g., the table does not exist).
            """
        try:
            self.cursor.execute(f"DROP TABLE {table_name}")
            self.connection.commit()

        except sqlite3.Error as e:
            return print(f"Error | Method - delete_table: {str(e)}")

    def delete_column(self, table_name: str, column_name: str) -> None:
        """
            Deletes a column from an existing table in the SQLite database.

            Args:
                table_name (str): The name of the table from which the column will be deleted.
                column_name (str): The name of the column to be deleted.

            Returns:
                None

            Raises:
                sqlite3.Error: If an error occurs while executing the SQL command (e.g., the table or column does not exist).
                              Note: SQLite does not support dropping columns directly. This operation requires creating a new table
                              without the column, copying data, and renaming the table.
            """
        try:
            self.cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
            self.connection.commit()

        except sqlite3.Error as e:
            return print(f"Error | Method - delete_column: {str(e)}")

    def delete(self, table_name: str, where: str) -> None:
        """
        Deletes records from the specified table.

        Args:
            table_name (str): The name of the table.
            where (str): The WHERE clause to specify which records to delete (e.g., "age < 18").

        Raises:
            ValueError: If the table name or WHERE clause is invalid.
            sqlite3.Error: If an error occurs while executing the SQL command.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")

        if not where or not isinstance(where, str):
            raise ValueError("WHERE clause must be a non-empty string.")

        query = f"DELETE FROM {table_name} WHERE {where}"

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Error deleting records: {e}")
