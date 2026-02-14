from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.controllers.auth_controller import AuthController
from app.controllers.data_source_controller import DataSourceController
from app.models.account import AccountRole
from app.schemas.data_source import (
    DataSourceType,
    DataSourceStatus,
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    DataSourceListItem,
)

router = APIRouter(prefix="/data-sources", tags=["Data Sources"])


def get_current_user_from_token(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization.replace("Bearer ", "")
    return AuthController.get_current_user(db, token)


def require_admin(current_user):
    """Check if the current user is an admin."""
    if current_user.role != AccountRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def check_resource_access(current_user, resource_owner_id: UUID, team_id: Optional[UUID], db: Session):
    """
    Check if user has access to a resource.
    Admin can access everything.
    Regular users can only access their own or their team's resources.
    """
    # Admin has full access
    if current_user.role == AccountRole.ADMIN:
        return True
    
    # User owns the resource
    if resource_owner_id == current_user.id:
        return True
    
    # Resource belongs to user's team
    if team_id:
        team_ids = DataSourceController._get_team_ids_for_account(db, current_user.id)
        if team_id in team_ids:
            return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this resource"
    )


@router.post("", response_model=DataSourceResponse, status_code=201)
def create_data_source(
    request: DataSourceCreate,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Create a new data source.
    
    The authenticated user becomes the creator.
    
    - **title**: Unique data source title (1-255 characters)
    - **type**: Type of database (postgresql, mysql, oracle)
    - **config**: Database connection configuration (validated based on type)
    - **team_id**: Optional team to associate the data source with
    """
    current_user = get_current_user_from_token(authorization, db)
    return DataSourceController.create_data_source(db, request, current_user.id)


@router.get("", response_model=List[DataSourceListItem])
def list_data_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[DataSourceType] = Query(None, description="Filter by data source type"),
    status: Optional[DataSourceStatus] = Query(None, description="Filter by status"),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    List data sources with optional filtering.
    
    - **Admin**: Returns all data sources in the system
    - **Regular users**: Returns only their own and their team's data sources
    
    - **skip**: Number of data sources to skip (pagination)
    - **limit**: Maximum number of data sources to return
    - **type**: Filter by type (postgresql, mysql, oracle)
    - **status**: Filter by status (active, inactive, error, pending)
    """
    current_user = get_current_user_from_token(authorization, db)
    
    # Admin gets all data sources
    if current_user.role == AccountRole.ADMIN:
        return DataSourceController.list_data_sources(
            db, skip=skip, limit=limit, type_filter=type, status_filter=status
        )
    
    # Regular users get their own + team's data sources
    return DataSourceController.get_my_data_sources(
        db, current_user.id, skip=skip, limit=limit, type_filter=type, status_filter=status
    )


@router.get("/my", response_model=List[DataSourceListItem])
def get_my_data_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[DataSourceType] = Query(None, description="Filter by data source type"),
    status: Optional[DataSourceStatus] = Query(None, description="Filter by status"),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get all data sources accessible to the current user.
    
    Includes data sources created by the user and data sources
    belonging to teams where the user is owner, member, or manager.
    
    - **type**: Filter by type (postgresql, mysql, oracle)
    - **status**: Filter by status (active, inactive, error, pending)
    """
    current_user = get_current_user_from_token(authorization, db)
    return DataSourceController.get_my_data_sources(
        db, current_user.id, skip=skip, limit=limit, type_filter=type, status_filter=status
    )


@router.get("/by-creator/{account_id}", response_model=List[DataSourceListItem])
def get_data_sources_by_creator(
    account_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get data sources created by a specific account.
    
    Admin can query any account. Regular users can only query their own.
    
    - **account_id**: The ID of the account to filter by
    """
    current_user = get_current_user_from_token(authorization, db)
    
    # Admin can access any account, users can only access their own
    if current_user.role != AccountRole.ADMIN and current_user.id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own data sources"
        )
    
    return DataSourceController.get_data_sources_by_creator(
        db, account_id, skip=skip, limit=limit
    )


@router.get("/by-team/{team_id}", response_model=List[DataSourceListItem])
def get_data_sources_by_team(
    team_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get data sources belonging to a specific team.
    
    Admin can query any team. Regular users can only query teams they belong to.
    
    - **team_id**: The ID of the team to filter by
    """
    current_user = get_current_user_from_token(authorization, db)
    
    # Admin can access any team, users can only access their teams
    if current_user.role != AccountRole.ADMIN:
        user_team_ids = DataSourceController._get_team_ids_for_account(db, current_user.id)
        if team_id not in user_team_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this team's data sources"
            )
    
    return DataSourceController.get_data_sources_by_team(
        db, team_id, skip=skip, limit=limit
    )


@router.get("/for-account-teams/{account_id}", response_model=List[DataSourceListItem])
def get_data_sources_for_account_teams(
    account_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get data sources for all teams associated with an account.
    
    Admin can query any account. Regular users can only query their own.
    
    First retrieves all team IDs where the account is owner, member, or manager,
    then returns data sources belonging to those teams.
    
    - **account_id**: The ID of the account
    """
    current_user = get_current_user_from_token(authorization, db)
    
    # Admin can access any account, users can only access their own
    if current_user.role != AccountRole.ADMIN and current_user.id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own team's data sources"
        )
    
    return DataSourceController.get_data_sources_for_account_teams(
        db, account_id, skip=skip, limit=limit
    )


@router.get("/{data_source_id}", response_model=DataSourceResponse)
def get_data_source(
    data_source_id: UUID,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get data source details by ID.
    
    Admin can view any data source. Regular users can only view their own
    or their team's data sources.
    
    Returns full data source details with masked password in config.
    """
    current_user = get_current_user_from_token(authorization, db)
    data_source = DataSourceController.get_data_source(db, data_source_id)
    
    # Check access
    check_resource_access(current_user, data_source.created_by, data_source.team_id, db)
    
    return data_source


@router.patch("/{data_source_id}", response_model=DataSourceResponse)
def update_data_source(
    data_source_id: UUID,
    request: DataSourceUpdate,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Update a data source.
    
    Admin can update any data source. Regular users can only update their own
    or their team's data sources.
    
    - **title**: Optional new title (must be unique)
    - **status**: Optional new status
    - **config**: Optional new configuration (validated against existing type)
    - **team_id**: Optional new team association
    """
    current_user = get_current_user_from_token(authorization, db)
    
    # Get data source to check access
    data_source = DataSourceController.get_data_source(db, data_source_id)
    check_resource_access(current_user, data_source.created_by, data_source.team_id, db)
    
    return DataSourceController.update_data_source(db, data_source_id, request)


@router.delete("/{data_source_id}")
def delete_data_source(
    data_source_id: UUID,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Delete a data source.
    
    Admin can delete any data source. Regular users can only delete their own
    or their team's data sources.
    """
    current_user = get_current_user_from_token(authorization, db)
    
    # Get data source to check access
    data_source = DataSourceController.get_data_source(db, data_source_id)
    check_resource_access(current_user, data_source.created_by, data_source.team_id, db)
    
    return DataSourceController.delete_data_source(db, data_source_id)
