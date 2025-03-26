import re
import sqlite3
import logging
from typing import List, Any, Dict, Optional, Union, Tuple


class Database:
    def __init__(self, db_path: str) -> None:
        """
        Initializes a new database connection and sets up logging.

        Args:
            db_path: Path to the SQLite database file

        Raises:
            sqlite3.Error: If connection to the database fails

        Example:
            >>> db = Database("example.db")
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        try:
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.logger.info(f"Successfully connected to database at {db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def command(
            self,
            sql: str,
            params: Optional[Union[Tuple, Dict[str, Any]]] = None,
            *,
            executemany: bool = False,
            many_params: Optional[List[Union[Tuple, Dict[str, Any]]]] = None,
            fetch: bool = False,
            fetch_all: bool = False,
            commit: bool = True
    ) -> Optional[Union[List[Dict[str, Any]], List[Tuple], Dict[str, Any], Tuple, Any]]:
        """
        Executes SQL command with flexible options for different use cases.

        Args:
            sql: SQL command to execute
            params: Parameters for the query (tuple for positional, dict for named)
            executemany: If True, executes executemany with parameters from many_params
            many_params: Sequence of parameters for executemany
            fetch: If True, returns first row of results (after commit if commit=True)
            fetch_all: If True, returns all rows of results
            commit: If True, commits the transaction

        Returns:
            Depending on options:
            - None if just executing
            - Single row if fetch=True
            - List of rows if fetch_all=True or executemany=True

        Raises:
            ValueError: For invalid arguments
            sqlite3.Error: For database errors

        Examples:
            # Simple execution
            db.command("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

            # With parameters
            db.command("INSERT INTO users VALUES (?, ?)", (1, "Alice"))

            # Named parameters
            db.command("INSERT INTO users VALUES (:id, :name)", {"id": 2, "name": "Bob"})

            # Batch insert
            db.command(
                "INSERT INTO users VALUES (?, ?)",
                executemany=True,
                many_params=[(3, "Charlie"), (4, "David")]
            )

            # Fetch single row
            user = db.command("SELECT * FROM users WHERE id = ?", (1,), fetch=True)

            # Fetch all rows
            users = db.command("SELECT * FROM users", fetch_all=True)

            # Without auto-commit
            db.command("BEGIN")
            try:
                db.command("INSERT INTO users VALUES (5, 'Eve')", commit=False)
                db.command("COMMIT")
            except:
                db.command("ROLLBACK")
                raise
        """
        try:
            if not sql or not isinstance(sql, str):
                raise ValueError("SQL must be a non-empty string")

            if executemany:
                if not many_params:
                    raise ValueError("many_params required when executemany=True")
                if params:
                    raise ValueError("Use either params or many_params, not both")
            elif many_params:
                raise ValueError("many_params provided but executemany=False")

            if fetch and fetch_all:
                raise ValueError("Use either fetch or fetch_all, not both")

            if executemany:
                self.cursor.executemany(sql, many_params)
                result = None
            elif params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            if commit:
                self.connection.commit()

            if fetch:
                row = self.cursor.fetchone()
                if row and self.cursor.description:
                    columns = [col[0] for col in self.cursor.description]
                    result = dict(zip(columns, row))
                else:
                    result = row
            elif fetch_all:
                rows = self.cursor.fetchall()
                if rows and self.cursor.description:
                    columns = [col[0] for col in self.cursor.description]
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = rows
            else:
                result = None

            self.logger.debug(
                f"Executed command: {sql}\n"
                f"Params: {params or many_params}\n"
                f"Options: fetch={fetch}, fetch_all={fetch_all}, commit={commit}\n"
                f"Result: {result if result is not None else 'None'}"
            )

            return result

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(
                f"Command failed: {sql}\n"
                f"Params: {params or many_params}\n"
                f"Error: {str(e)}"
            )
            if isinstance(e, ValueError):
                raise ValueError(f"Command error: {str(e)}") from e
            else:
                if commit:  # Only rollback if we were supposed to commit
                    self.connection.rollback()
                raise sqlite3.Error(f"Database error: {str(e)}") from e

    def close(self) -> None:
        """
        Closes the database connection gracefully.

        Raises:
            sqlite3.Error: If closing the connection fails

        Example:
            >>> db.close()
        """
        try:
            self.connection.close()
            self.logger.info("Database connection closed")
        except sqlite3.Error as e:
            self.logger.error(f"Error closing connection: {str(e)}")
            raise sqlite3.Error(f"Error closing connection: {str(e)}") from e

    def read_tables(self) -> List[str]:
        """
        Retrieves names of all tables in the database.

        Returns:
            List of table names as strings

        Raises:
            sqlite3.Error: If query execution fails

        Example:
            >>> tables = db.read_tables()
            >>> print(tables)
            ['users', 'products']
        """
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in self.cursor.fetchall()]
            self.logger.info(f"Retrieved tables: {tables}")
            return tables
        except sqlite3.Error as e:
            self.logger.error(f"Error reading tables: {str(e)}")
            raise sqlite3.Error(f"Error reading tables: {str(e)}") from e

    def read_columns(self, table_name: str) -> List[Tuple]:
        """
        Retrieves column information for a specific table.

        Args:
            table_name: Name of the table to inspect

        Returns:
            List of tuples with column info (cid, name, type, notnull, dflt_value, pk)

        Raises:
            ValueError: If table_name is invalid
            sqlite3.Error: If table doesn't exist or query fails

        Example:
            >>> columns = db.read_columns("users")
            >>> for col in columns:
            ...     print(col[1], col[2])  # name and type
        """
        try:
            if not table_name or not isinstance(table_name, str):
                raise ValueError("Table name must be a non-empty string")

            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            self.logger.info(f"Retrieved columns for table '{table_name}': {columns}")
            return columns
        except sqlite3.Error as e:
            self.logger.error(f"Error reading columns from table '{table_name}': {str(e)}")
            raise sqlite3.Error(f"Error reading columns: {str(e)}") from e

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Creates a new table with specified columns.

        Args:
            table_name: Name of the table to create
            columns: Dictionary mapping column names to SQL types
                    (e.g., {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

        Raises:
            ValueError: If arguments are invalid
            sqlite3.Error: If table creation fails

        Example:
            >>> db.create_table("users", {
            ...     "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            ...     "name": "TEXT NOT NULL",
            ...     "age": "INTEGER"
            ... })
        """
        try:
            if not table_name or not isinstance(table_name, str):
                raise ValueError("Table name must be a non-empty string")

            if not columns or not isinstance(columns, dict):
                raise ValueError("Columns must be a non-empty dictionary")

            columns_def = ", ".join([f"{name} {type}" for name, type in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"

            self.cursor.execute(query)
            self.connection.commit()
            self.logger.info(f"Created table '{table_name}' with columns: {columns}")
        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error creating table '{table_name}': {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(str(e)) from e
            else:
                raise sqlite3.Error(f"Error creating table: {str(e)}") from e

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Inserts a new record into the specified table.

        Args:
            table_name: Name of the target table
            data: Dictionary of column-value pairs to insert

        Returns:
            The rowid of the inserted record

        Raises:
            ValueError: If arguments are invalid
            sqlite3.Error: If insertion fails

        Example:
            >>> rowid = db.insert("users", {"name": "Alice", "age": 30})
            >>> print(f"Inserted record with ID: {rowid}")
        """
        try:
            if not table_name or not isinstance(table_name, str):
                raise ValueError("Table name must be a non-empty string")

            if not data or not isinstance(data, dict):
                raise ValueError("Data must be a non-empty dictionary")

            columns = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            rowid = self.cursor.lastrowid
            self.logger.info(f"Inserted record into '{table_name}' with ID {rowid}")
            return rowid
        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error inserting into '{table_name}': {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(str(e)) from e
            else:
                raise sqlite3.Error(f"Error inserting record: {str(e)}") from e

    def select(
            self,
            table_name: str,
            where: Optional[str] = None,
            params: Optional[Union[Tuple, Dict[str, Any]]] = None,
            columns: Optional[List[str]] = None,
            order_by: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves records from the specified table with optional filtering and sorting.

        Args:
            table_name: Name of the table to query
            where: WHERE clause with placeholders (use ? or :name)
            params: Parameters for the WHERE clause
            columns: List of columns to select (None for all)
            order_by: Column(s) to order by (e.g., "name DESC")
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of dictionaries representing the records

        Raises:
            ValueError: If arguments are invalid
            sqlite3.Error: If query execution fails

        Examples:
            >>> # Get all users
            >>> users = db.select("users")

            >>> # Get specific columns with filtering
            >>> active_users = db.select(
            ...     "users",
            ...     where="status = ? AND age > ?",
            ...     params=("active", 18),
            ...     columns=["id", "name"],
            ...     order_by="name ASC",
            ...     limit=10
            ... )
        """
        try:
            if not isinstance(table_name, str) or not table_name.strip():
                raise ValueError("Table name must be a non-empty string")

            if where and not isinstance(where, str):
                raise ValueError("WHERE clause must be a string")

            if params and not isinstance(params, (tuple, dict)):
                raise ValueError("Parameters must be a tuple or dictionary")

            # Build the SELECT query
            selected_columns = ", ".join(columns) if columns else "*"
            query = f"SELECT {selected_columns} FROM {table_name}"

            # Add WHERE clause if provided
            if where:
                query += f" WHERE {where}"
                if params:
                    if isinstance(params, tuple) and where.count("?") != len(params):
                        raise ValueError("Parameter count doesn't match placeholders")
                    elif isinstance(params, dict):
                        missing = [k for k in params if f":{k}" not in where]
                        if missing:
                            raise ValueError(f"Missing placeholders for: {missing}")

            # Add ORDER BY if specified
            if order_by:
                if not re.match(r"^[\w,\s]+$", order_by):
                    raise ValueError("Invalid characters in ORDER BY clause")
                query += f" ORDER BY {order_by}"

            # Add LIMIT and OFFSET if specified
            if limit is not None:
                if not isinstance(limit, int) or limit < 0:
                    raise ValueError("LIMIT must be a non-negative integer")
                query += f" LIMIT {limit}"

                if offset is not None:
                    if not isinstance(offset, int) or offset < 0:
                        raise ValueError("OFFSET must be a non-negative integer")
                    query += f" OFFSET {offset}"

            self.logger.debug(f"Executing query: {query} with params: {params}")

            # Execute the query
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            # Format results
            rows = self.cursor.fetchall()
            column_names = [col[0] for col in self.cursor.description]
            result = [dict(zip(column_names, row)) for row in rows]

            self.logger.info(f"Selected {len(result)} records from '{table_name}'")
            return result

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error selecting from '{table_name}': {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(f"Selection error: {str(e)}") from e
            else:
                raise sqlite3.Error(f"Database error: {str(e)}") from e

    def update(self, table_name: str, data: Dict[str, Any], where: str, params: Optional[Tuple] = None) -> int:
        """
        Updates records matching the specified conditions.

        Args:
            table_name: Name of the table to update
            data: Dictionary of column-value pairs to update
            where: WHERE clause identifying records to update
            params: Additional parameters for WHERE clause

        Returns:
            Number of rows affected

        Raises:
            ValueError: If arguments are invalid
            sqlite3.Error: If update fails

        Example:
            >>> count = db.update(
            ...     "users",
            ...     {"status": "inactive", "last_updated": datetime.now()},
            ...     where="last_login < ?",
            ...     params=(datetime(2020, 1, 1),)
            ... )
            >>> print(f"Updated {count} records")
        """
        try:
            if not table_name or not isinstance(table_name, str):
                raise ValueError("Table name must be a non-empty string")

            if not data or not isinstance(data, dict):
                raise ValueError("Data must be a non-empty dictionary")

            if not where or not isinstance(where, str):
                raise ValueError("WHERE clause must be a non-empty string")

            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"

            # Combine data values with additional params
            values = tuple(data.values()) + (params if params else ())

            self.cursor.execute(query, values)
            self.connection.commit()
            count = self.cursor.rowcount
            self.logger.info(f"Updated {count} rows in '{table_name}'")
            return count

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error updating '{table_name}': {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(str(e)) from e
            else:
                raise sqlite3.Error(f"Update error: {str(e)}") from e

    def delete(self, table_name: str, where: str, params: Optional[Tuple] = None) -> int:
        """
        Deletes records matching the specified conditions.

        Args:
            table_name: Name of the table to delete from
            where: WHERE clause identifying records to delete
            params: Parameters for WHERE clause

        Returns:
            Number of rows deleted

        Raises:
            ValueError: If arguments are invalid
            sqlite3.Error: If deletion fails

        Example:
            >>> count = db.delete(
            ...     "users",
            ...     where="status = ? AND last_login < ?",
            ...     params=("inactive", datetime(2019, 1, 1))
            ... )
            >>> print(f"Deleted {count} inactive users")
        """
        try:
            if not table_name or not isinstance(table_name, str):
                raise ValueError("Table name must be a non-empty string")

            if not where or not isinstance(where, str):
                raise ValueError("WHERE clause must be a non-empty string")

            query = f"DELETE FROM {table_name} WHERE {where}"

            self.cursor.execute(query, params if params else ())
            self.connection.commit()
            count = self.cursor.rowcount
            self.logger.info(f"Deleted {count} rows from '{table_name}'")
            return count

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error deleting from '{table_name}': {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(str(e)) from e
            else:
                raise sqlite3.Error(f"Deletion error: {str(e)}") from e

    def edit_table_name(self, old_name: str, new_name: str) -> None:
        """
        Renames an existing table.

        Args:
            old_name: Current table name
            new_name: New table name

        Raises:
            ValueError: If names are invalid
            sqlite3.Error: If renaming fails

        Example:
            >>> db.edit_table_name("old_users", "users")
        """
        try:
            if not old_name or not isinstance(old_name, str):
                raise ValueError("Old table name must be a non-empty string")

            if not new_name or not isinstance(new_name, str):
                raise ValueError("New table name must be a non-empty string")

            query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
            self.cursor.execute(query)
            self.connection.commit()
            self.logger.info(f"Renamed table '{old_name}' to '{new_name}'")

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error renaming table: {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(str(e)) from e
            else:
                raise sqlite3.Error(f"Rename error: {str(e)}") from e

    def add_column(self, table_name: str, column_def: Dict[str, str]) -> None:
        """
        Adds a new column to an existing table.

        Args:
            table_name: Name of the target table
            column_def: Dictionary mapping column names to definitions
                      (e.g., {"email": "TEXT UNIQUE"})

        Raises:
            ValueError: If arguments are invalid or column exists
            sqlite3.Error: If operation fails

        Example:
            >>> db.add_column("users", {"email": "TEXT NOT NULL UNIQUE"})
        """
        try:
            if not table_name or not isinstance(table_name, str):
                raise ValueError("Table name must be a non-empty string")

            if not column_def or not isinstance(column_def, dict):
                raise ValueError("Column definition must be a non-empty dictionary")

            # Check if table exists
            if table_name not in self.read_tables():
                raise ValueError(f"Table '{table_name}' does not exist")

            # Get existing columns
            existing_columns = [col[1] for col in self.read_columns(table_name)]

            for col_name, col_type in column_def.items():
                if col_name in existing_columns:
                    raise ValueError(f"Column '{col_name}' already exists in '{table_name}'")

                query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                self.cursor.execute(query)
                self.connection.commit()
                self.logger.info(f"Added column '{col_name}' to '{table_name}'")

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(f"Error adding column: {str(e)}")
            if isinstance(e, ValueError):
                raise ValueError(str(e)) from e
            else:
                raise sqlite3.Error(f"Add column error: {str(e)}") from e
