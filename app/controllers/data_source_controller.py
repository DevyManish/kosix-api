from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.logger import get_logger
from app.models.data_source import DataSource, DataSourceType, DataSourceStatus
from app.models.team import Team, team_members, team_managers
from app.models.account import Account
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    DataSourceListItem,
    validate_config,
    mask_config_password,
)

logger = get_logger(__name__)


class DataSourceController:
    """Controller for data source operations."""

    @staticmethod
    def create_data_source(
        db: Session,
        request: DataSourceCreate,
        created_by: UUID
    ) -> DataSourceResponse:
        """Create a new data source."""
        logger.info(f"Creating data source '{request.title}' for user {created_by}")

        # Check if title already exists
        existing = db.query(DataSource).filter(DataSource.title == request.title).first()
        if existing:
            logger.warning(f"Data source with title '{request.title}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source with this title already exists"
            )

        # Validate config against type (already done in schema, but extra safety)
        validate_config(request.type, request.config)

        data_source = DataSource(
            title=request.title,
            type=request.type.value,
            status=DataSourceStatus.PENDING.value,
            created_by=created_by,
            team_id=request.team_id,
            config=request.config
        )

        db.add(data_source)
        db.commit()
        db.refresh(data_source)

        logger.info(f"Successfully created data source: {data_source.id}")

        return DataSourceResponse(
            id=data_source.id,
            title=data_source.title,
            type=DataSourceType(data_source.type),
            status=DataSourceStatus(data_source.status),
            created_by=data_source.created_by,
            team_id=data_source.team_id,
            config=mask_config_password(data_source.config),
            created_at=data_source.created_at,
            updated_at=data_source.updated_at
        )

    @staticmethod
    def get_data_source(db: Session, data_source_id: UUID) -> DataSourceResponse:
        """Get data source by ID."""
        logger.info(f"Fetching data source: {data_source_id}")

        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            logger.warning(f"Data source not found: {data_source_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        return DataSourceResponse(
            id=data_source.id,
            title=data_source.title,
            type=DataSourceType(data_source.type),
            status=DataSourceStatus(data_source.status),
            created_by=data_source.created_by,
            team_id=data_source.team_id,
            config=mask_config_password(data_source.config),
            created_at=data_source.created_at,
            updated_at=data_source.updated_at
        )

    @staticmethod
    def list_data_sources(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        type_filter: Optional[DataSourceType] = None,
        status_filter: Optional[DataSourceStatus] = None
    ) -> List[DataSourceListItem]:
        """List data sources with optional filtering."""
        logger.info(f"Listing data sources (skip={skip}, limit={limit})")

        query = db.query(DataSource)

        if type_filter:
            query = query.filter(DataSource.type == type_filter.value)
        if status_filter:
            query = query.filter(DataSource.status == status_filter.value)

        data_sources = query.offset(skip).limit(limit).all()

        return [
            DataSourceListItem(
                id=ds.id,
                title=ds.title,
                type=DataSourceType(ds.type),
                status=DataSourceStatus(ds.status),
                created_by=ds.created_by,
                team_id=ds.team_id,
                created_at=ds.created_at
            )
            for ds in data_sources
        ]

    @staticmethod
    def update_data_source(
        db: Session,
        data_source_id: UUID,
        request: DataSourceUpdate
    ) -> DataSourceResponse:
        """Update a data source."""
        logger.info(f"Updating data source: {data_source_id}")

        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            logger.warning(f"Data source not found: {data_source_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # Check title uniqueness if being updated
        if request.title and request.title != data_source.title:
            existing = db.query(DataSource).filter(DataSource.title == request.title).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Data source with this title already exists"
                )
            data_source.title = request.title

        if request.status:
            data_source.status = request.status.value

        if request.team_id is not None:
            data_source.team_id = request.team_id

        if request.config:
            # Validate new config against existing type
            validate_config(DataSourceType(data_source.type), request.config)
            data_source.config = request.config

        db.commit()
        db.refresh(data_source)

        logger.info(f"Successfully updated data source: {data_source_id}")

        return DataSourceResponse(
            id=data_source.id,
            title=data_source.title,
            type=DataSourceType(data_source.type),
            status=DataSourceStatus(data_source.status),
            created_by=data_source.created_by,
            team_id=data_source.team_id,
            config=mask_config_password(data_source.config),
            created_at=data_source.created_at,
            updated_at=data_source.updated_at
        )

    @staticmethod
    def delete_data_source(db: Session, data_source_id: UUID) -> dict:
        """Delete a data source."""
        logger.info(f"Deleting data source: {data_source_id}")

        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            logger.warning(f"Data source not found: {data_source_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        db.delete(data_source)
        db.commit()

        logger.info(f"Successfully deleted data source: {data_source_id}")

        return {"message": "Data source deleted successfully"}

    @staticmethod
    def get_data_sources_by_creator(
        db: Session,
        account_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[DataSourceListItem]:
        """Get data sources created by a specific account."""
        logger.info(f"Fetching data sources created by account: {account_id}")

        # Verify account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        data_sources = db.query(DataSource).filter(
            DataSource.created_by == account_id
        ).offset(skip).limit(limit).all()

        return [
            DataSourceListItem(
                id=ds.id,
                title=ds.title,
                type=DataSourceType(ds.type),
                status=DataSourceStatus(ds.status),
                created_by=ds.created_by,
                team_id=ds.team_id,
                created_at=ds.created_at
            )
            for ds in data_sources
        ]

    @staticmethod
    def get_data_sources_by_team(
        db: Session,
        team_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[DataSourceListItem]:
        """Get data sources belonging to a specific team."""
        logger.info(f"Fetching data sources for team: {team_id}")

        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        data_sources = db.query(DataSource).filter(
            DataSource.team_id == team_id
        ).offset(skip).limit(limit).all()

        return [
            DataSourceListItem(
                id=ds.id,
                title=ds.title,
                type=DataSourceType(ds.type),
                status=DataSourceStatus(ds.status),
                created_by=ds.created_by,
                team_id=ds.team_id,
                created_at=ds.created_at
            )
            for ds in data_sources
        ]

    @staticmethod
    def _get_team_ids_for_account(db: Session, account_id: UUID) -> List[UUID]:
        """
        Get all team IDs associated with an account.
        Includes teams where the account is owner, member, or manager.
        """
        # Teams where user is owner
        owned_team_ids = db.query(Team.id).filter(Team.owner_id == account_id).all()
        owned_team_ids = [t[0] for t in owned_team_ids]

        # Teams where user is member
        member_team_ids = db.query(team_members.c.team_id).filter(
            team_members.c.account_id == account_id
        ).all()
        member_team_ids = [t[0] for t in member_team_ids]

        # Teams where user is manager
        manager_team_ids = db.query(team_managers.c.team_id).filter(
            team_managers.c.account_id == account_id
        ).all()
        manager_team_ids = [t[0] for t in manager_team_ids]

        # Return unique team IDs
        return list(set(owned_team_ids + member_team_ids + manager_team_ids))

    @staticmethod
    def get_data_sources_for_account_teams(
        db: Session,
        account_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[DataSourceListItem]:
        """
        Get data sources for all teams associated with an account.
        This includes teams where the account is owner, member, or manager.
        """
        logger.info(f"Fetching data sources for account's teams: {account_id}")

        # Verify account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Get all team IDs for this account
        team_ids = DataSourceController._get_team_ids_for_account(db, account_id)

        if not team_ids:
            return []

        # Get data sources for all these teams
        data_sources = db.query(DataSource).filter(
            DataSource.team_id.in_(team_ids)
        ).offset(skip).limit(limit).all()

        return [
            DataSourceListItem(
                id=ds.id,
                title=ds.title,
                type=DataSourceType(ds.type),
                status=DataSourceStatus(ds.status),
                created_by=ds.created_by,
                team_id=ds.team_id,
                created_at=ds.created_at
            )
            for ds in data_sources
        ]

    @staticmethod
    def get_my_data_sources(
        db: Session,
        account_id: UUID,
        skip: int = 0,
        limit: int = 20,
        type_filter: Optional[DataSourceType] = None,
        status_filter: Optional[DataSourceStatus] = None
    ) -> List[DataSourceListItem]:
        """
        Get all data sources accessible to an account.
        Includes:
        - Data sources created by the account
        - Data sources belonging to teams where account is owner/member/manager
        """
        logger.info(f"Fetching all accessible data sources for account: {account_id}")

        # Verify account exists
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        # Get team IDs for this account
        team_ids = DataSourceController._get_team_ids_for_account(db, account_id)

        # Build query for data sources created by account OR belonging to their teams
        query = db.query(DataSource)
        
        if team_ids:
            query = query.filter(
                (DataSource.created_by == account_id) | (DataSource.team_id.in_(team_ids))
            )
        else:
            query = query.filter(DataSource.created_by == account_id)

        # Apply optional filters
        if type_filter:
            query = query.filter(DataSource.type == type_filter.value)
        if status_filter:
            query = query.filter(DataSource.status == status_filter.value)

        data_sources = query.offset(skip).limit(limit).all()

        return [
            DataSourceListItem(
                id=ds.id,
                title=ds.title,
                type=DataSourceType(ds.type),
                status=DataSourceStatus(ds.status),
                created_by=ds.created_by,
                team_id=ds.team_id,
                created_at=ds.created_at
            )
            for ds in data_sources
        ]
