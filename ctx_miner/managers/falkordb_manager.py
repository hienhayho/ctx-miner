"""FalkorDB Manager for handling database connections and operations."""

from typing import Optional, Dict, Any
from graphiti_core.driver.falkordb_driver import FalkorDriver
import redis
from redis.exceptions import ConnectionError
from loguru import logger
from ctx_miner.core.schemas import FalkorDBConfig


class FalkorDBManager:
    """Manages FalkorDB connections and database operations."""

    def __init__(
        self,
        config: FalkorDBConfig,
    ):
        """
        Initialize FalkorDB Manager.

        Args:
            config: FalkorDB configuration
        """
        self.config = config
        self._driver: Optional[FalkorDriver] = None
        self._redis_client: Optional[redis.Redis] = None

    async def check_connection(self) -> bool:
        """
        Check if connection to FalkorDB is possible.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Create Redis client for basic operations
            self._redis_client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                decode_responses=True,
            )

            # Test connection with ping
            self._redis_client.ping()
            logger.info(
                f"Successfully connected to FalkorDB at {self.config.host}:{self.config.port}"
            )
            return True

        except ConnectionError as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to FalkorDB: {e}")
            return False

    async def database_exists(self, database_name: Optional[str] = None) -> bool:
        """
        Check if a database exists in FalkorDB.

        Args:
            database_name: Name of the database to check. Uses self.database if None.

        Returns:
            bool: True if database exists, False otherwise
        """
        db_name = database_name or self.config.database

        if not self._redis_client:
            await self.check_connection()

        try:
            # In FalkorDB, databases are Redis keys with graph: prefix
            graph_key = f"graph:{db_name}"
            return bool(self._redis_client.exists(graph_key))
        except Exception as e:
            logger.error(f"Error checking if database exists: {e}")
            return False

    async def create_database(self, database_name: Optional[str] = None) -> bool:
        """
        Create a new database in FalkorDB.

        Args:
            database_name: Name of the database to create. Uses self.database if None.

        Returns:
            bool: True if database created successfully, False otherwise
        """
        db_name = database_name or self.config.database

        try:
            # In FalkorDB, databases are created automatically when first accessed
            # We'll create a driver instance to initialize the database
            temp_driver = FalkorDriver(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                database=db_name,
            )

            # Close the temporary driver
            await temp_driver.close()

            logger.info(f"Database '{db_name}' initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False

    async def list_databases(self) -> list[str]:
        """
        List all databases in FalkorDB.

        Returns:
            list[str]: List of database names
        """
        if not self._redis_client:
            await self.check_connection()

        try:
            # Find all keys with graph: prefix
            graph_keys = self._redis_client.keys("graph:*")
            # Extract database names from keys
            databases = [key.replace("graph:", "") for key in graph_keys]
            return databases
        except Exception as e:
            logger.error(f"Error listing databases: {e}")
            return []

    async def delete_database(self, database_name: Optional[str] = None) -> bool:
        """
        Delete a database from FalkorDB.

        Args:
            database_name: Name of the database to delete. Uses self.database if None.

        Returns:
            bool: True if database deleted successfully, False otherwise
        """
        db_name = database_name or self.config.database

        if not self._redis_client:
            await self.check_connection()

        try:
            # Delete the graph key
            graph_key = f"graph:{db_name}"
            result = self._redis_client.delete(graph_key)
            if result:
                logger.info(f"Database '{db_name}' deleted successfully")
                return True
            else:
                logger.warning(f"Database '{db_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting database: {e}")
            return False

    def get_driver(self) -> FalkorDriver:
        """
        Get or create a FalkorDriver instance.

        Returns:
            FalkorDriver: Driver instance for database operations
        """
        if not self._driver:
            self._driver = FalkorDriver(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                database=self.config.database,
            )
        return self._driver

    async def close(self):
        """Close all connections."""
        if self._driver:
            await self._driver.close()
            self._driver = None

        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None

    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information.

        Returns:
            Dict[str, Any]: Connection details
        """
        return {
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "connected": await self.check_connection(),
            "databases": await self.list_databases(),
        }
