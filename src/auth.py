import database
import os
import time
import requests
import jwt
from jwt import PyJWKClient
from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import HTTPBearer
from authlib.integrations.starlette_client import OAuth, OAuthError

REGION = "us-east-2"
USER_POOL_ID = "us-east-2_Y3j8IBnuE"
CLIENT_ID = "387ub3kl6t8ljnharhnbfrum1h"
CLIENT_SECRET = os.getenv("AWS_CLIENT_SECRET", "<client secret>")  # set in env
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
SERVER_METADATA_URL = f"{ISSUER}/.well-known/openid-configuration"
SCOPES = "openid email phone"

api = APIRouter(prefix="/user", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=SERVER_METADATA_URL,
    client_kwargs={"scope": SCOPES},
)

security = HTTPBearer(auto_error=False)

def require_user(request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session["user"]

# ---------------------------
# Routes
# ---------------------------
@api.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if user:
        email = user.get("email") or "(no email claim)"
        return HTMLResponse(
            f"<h3>Signed in</h3><p>{email}</p>"
            f'<p><a href="/protected">Protected route</a></p>'
            f'<p><a href="/logout">Logout</a></p>'
        )
    return HTMLResponse('<a href="/login">Login with Cognito</a>')

@api.get("/login")
async def login(request: Request):
    # Must be in your Cognito App client callback list
    redirect_uri = request.url_for("auth_callback")
    return await oauth.oidc.authorize_redirect(request, redirect_uri)

@api.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        # Exchanges code for tokens and validates ID token with JWKS
        token = await oauth.oidc.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e.error}")

    # Prefer OIDC userinfo if available. Fallback to ID token claims.
    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.oidc.parse_id_token(request, token)

    # Store minimal session info
    request.session["user"] = {
        "sub": userinfo.get("sub"),
        "email": userinfo.get("email"),
    }
    request.session["token"] = token  # access_token, id_token, etc.
    return RedirectResponse(url="/")

@api.get("/protected")
async def protected(_user=Depends(require_user)):
    # You have a valid session here
    return {"ok": True, "user": _user}

@api.get("/logout")
async def logout(request: Request):
    request.session.clear()
    # Optional: also hit Cognito logout endpoint if you use Hosted UI domain
    # Redirect back to home after local logout
    return RedirectResponse(url="/")

@api.post("/create")
def create_user(user: dict):
    response = table.put_item(Item=user)
    return {"valid": True, "data": response}

@api.get("/me")
def get_current_user():
    return {"valid": True, "data": "Get current user not implemented yet."} # TODO: Implement get current user logic with DynamoDB

@api.post("/update")
def update_user():
    return {"valid": True, "data": "User update not implemented yet."} # TODO: Implement user update logic with DynamoDB

@api.post("/get_data")
def get_user_data():
    return {"valid": True, "data": "Get user data not implemented yet."} # TODO: Implement get user data logic with DynamoDB
