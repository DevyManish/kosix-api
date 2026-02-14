from datetime import datetime
from typing import Optional, Union, Annotated
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class DataSourceType(str, Enum):
    """Data source type enumeration."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"


class DataSourceStatus(str, Enum):
    """Data source status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


# =============================================================================
# Base Config Class (Open-Closed Principle - Extensible for new DB types)
# =============================================================================

class BaseDataSourceConfig(BaseModel):
    """
    Base configuration for all data source types.
    Contains common connection fields shared across databases.
    Extend this class to add new database types (DRY principle).
    """
    host: str = Field(..., min_length=1, max_length=255, description="Database host address")
    port: int = Field(..., gt=0, le=65535, description="Database port number")
    username: str = Field(..., min_length=1, max_length=255, description="Database username")
    password: str = Field(..., min_length=1, description="Database password")


# =============================================================================
# Type-Specific Config Classes (Extending Base)
# =============================================================================

class PostgreSQLConfig(BaseDataSourceConfig):
    """PostgreSQL-specific configuration."""
    database: str = Field(..., min_length=1, max_length=255, description="Database name")
    ssl: bool = Field(default=False, description="Enable SSL connection")
    ssl_mode: Optional[str] = Field(
        default=None,
        pattern="^(disable|allow|prefer|require|verify-ca|verify-full)$",
        description="SSL mode (disable, allow, prefer, require, verify-ca, verify-full)"
    )
    connect_timeout: int = Field(default=10, ge=1, le=300, description="Connection timeout in seconds")
    application_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Application name for connection identification"
    )


class MySQLConfig(BaseDataSourceConfig):
    """MySQL-specific configuration."""
    database: str = Field(..., min_length=1, max_length=255, description="Database name")
    ssl: bool = Field(default=False, description="Enable SSL connection")
    charset: str = Field(default="utf8mb4", max_length=50, description="Character set")
    connect_timeout: int = Field(default=10, ge=1, le=300, description="Connection timeout in seconds")


class OracleConfig(BaseDataSourceConfig):
    """Oracle-specific configuration."""
    service_name: str = Field(..., min_length=1, max_length=255, description="Oracle service name")


# =============================================================================
# Config Type Union (For type-safe validation)
# =============================================================================

DataSourceConfigUnion = Union[PostgreSQLConfig, MySQLConfig, OracleConfig]

# Mapping of data source types to their config classes
CONFIG_CLASS_MAP = {
    DataSourceType.POSTGRESQL: PostgreSQLConfig,
    DataSourceType.MYSQL: MySQLConfig,
    DataSourceType.ORACLE: OracleConfig,
}


# =============================================================================
# Data Source Schemas
# =============================================================================

class DataSourceBase(BaseModel):
    """Base data source schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255)


class DataSourceCreate(DataSourceBase):
    """Schema for creating a new data source."""
    type: DataSourceType
    config: dict
    team_id: Optional[UUID] = None

    @model_validator(mode='after')
    def validate_config_matches_type(self):
        """Validate that config matches the declared type."""
        config_class = CONFIG_CLASS_MAP.get(self.type)
        if config_class is None:
            raise ValueError(f"Unsupported data source type: {self.type}")
        # Validate config against the appropriate schema
        config_class(**self.config)
        return self


class DataSourceUpdate(BaseModel):
    """Schema for updating a data source."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[DataSourceStatus] = None
    config: Optional[dict] = None
    team_id: Optional[UUID] = None


class DataSourceResponse(DataSourceBase):
    """Schema for data source response."""
    id: UUID
    type: DataSourceType
    status: DataSourceStatus
    created_by: Optional[UUID] = None
    team_id: Optional[UUID] = None
    config: dict  # Config without password for security
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DataSourceListItem(BaseModel):
    """Schema for data source in list responses."""
    id: UUID
    title: str
    type: DataSourceType
    status: DataSourceStatus
    created_by: Optional[UUID] = None
    team_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# Helper Functions
# =============================================================================

def get_config_class(data_source_type: DataSourceType) -> type[BaseDataSourceConfig]:
    """
    Get the config class for a given data source type.
    Useful for dynamic validation and serialization.
    """
    config_class = CONFIG_CLASS_MAP.get(data_source_type)
    if config_class is None:
        raise ValueError(f"Unsupported data source type: {data_source_type}")
    return config_class


def validate_config(data_source_type: DataSourceType, config: dict) -> BaseDataSourceConfig:
    """
    Validate and parse config for a given data source type.
    Returns the validated config instance.
    """
    config_class = get_config_class(data_source_type)
    return config_class(**config)


def mask_config_password(config: dict) -> dict:
    """
    Returns a copy of config with password masked.
    Useful for API responses.
    """
    masked = config.copy()
    if "password" in masked:
        masked["password"] = "********"
    return masked
