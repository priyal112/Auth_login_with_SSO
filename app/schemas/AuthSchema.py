from pydantic import BaseModel


class TokenResponse(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):

    # Refresh token received during sign in
    refresh_token: str


# Schema used when requesting a password reset
class ForgotPasswordRequest(BaseModel):

    email: str


class ResetPasswordRequest(BaseModel):

    token: str
    password: str