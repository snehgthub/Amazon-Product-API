from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, col, select
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2
from ..database import engine

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(
            select(models.User).where(
                col(models.User.email) == user_credentials.username
            )
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials",
            )
        if not utils.verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
            )

        access_token = oauth2.create_access_token(data={"user_id": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
