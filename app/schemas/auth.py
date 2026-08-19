from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):

    username:str = Field(min_length=3, max_length=50)
    email:EmailStr
    password:str = Field(min_length=8, max_length=100)

class UserResponse(BaseModel):

    user_id : int
    username : str
    email : EmailStr

class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50, description="Username of the user")
    password: str = Field(min_length=1, max_length=100, description="Password of the user")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

