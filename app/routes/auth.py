from fastapi import APIRouter, Depends, status, HTTPException

from app.dependencies.auth import get_user_service
from app.schemas.auth import UserRegister, UserResponse, UserLogin, TokenResponse
from app.services.user_service import UserService
from app.dependencies.security import get_current_user_id

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    service: UserService = Depends(get_user_service)
):
    try :
        user = service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email
    )

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, service: UserService = Depends(get_user_service)):

    try:
        access_token = service .login_user(
            username=user_data.username,
            password=user_data.password
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service)
):
    user = service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email
    )