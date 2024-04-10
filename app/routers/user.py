from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..database import engine
from .. import schemas, models, utils

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[schemas.UserRead])
def get_users():
    with Session(engine) as session:
        users = session.exec(select(models.User)).all()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No users to show."
            )
        return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate):
    with Session(engine) as session:
        existing_user = session.exec(
            select(models.User).where(models.User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered.",
            )
        hashed_password = utils.get_password_hash(user.password)
        extra_data = {"hashed_password": hashed_password}
        db_user = models.User.model_validate(user, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


@router.get("/{id}", response_model=schemas.UserRead)
def get_user(id: int):
    with Session(engine) as session:
        user = session.get(models.User, id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: '{id}' not found.",
            )
        return user


@router.patch("/{id}", response_model=schemas.UserRead)
def update_user(id: int, user: schemas.UserUpdate):
    with Session(engine) as session:
        db_user = session.get(models.User, id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find a user with id: {id}",
            )
        user_data = user.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = utils.get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)  # type: ignore
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user
