from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..auth import get_db, current_user, oauth
from ..schemas import AuthRegisterRequest, AuthLoginRequest, AuthResponse, UserOut
from ..models import User
from ..utils.security import hash_password, verify_password, create_jwt
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse)
def register(body: AuthRegisterRequest, db: Session = Depends(get_db)):
    if settings.auth_mode == "noauth":
        raise HTTPException(status_code=400, detail="Registration disabled in noauth mode")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(email=body.email, password_hash=hash_password(body.password))
    db.add(u); db.commit()
    token = create_jwt(u.id)
    return {"token": token, "user": {"id": u.id, "email": u.email, "role": u.role}}

@router.post("/login", response_model=AuthResponse)
def login(body: AuthLoginRequest, db: Session = Depends(get_db)):
    if settings.auth_mode == "noauth":
        # Return dev tokenless user for FE compat
        u = db.query(User).filter(User.email=="dev@learnai.local").first()
        if not u:
            u = User(email="dev@learnai.local")
            db.add(u); db.commit()
        token = create_jwt(u.id)
        return {"token": token, "user": {"id": u.id, "email": u.email, "role": u.role}}
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not u.password_hash or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(u.id)
    return {"token": token, "user": {"id": u.id, "email": u.email, "role": u.role}}

@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db)):
    # in noauth mode, return dev user without requiring a token
    if settings.auth_mode == "noauth":
        u = db.query(User).filter(User.email=="dev@learnai.local").first()
        if not u:
            u = User(email="dev@learnai.local")
            db.add(u); db.commit()
        return {"id": u.id, "email": u.email, "role": u.role}
    from ..auth import current_user as cu
    user = cu()  # type: ignore
    return {"id": user.id, "email": user.email, "role": user.role}

# OAuth (optional) routes kept simple: you can switch AUTH_MODE=oauth to use.
@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    if not settings.enable_oauth:
        raise HTTPException(status_code=400, detail="OAuth disabled")
    if provider not in oauth:
        raise HTTPException(status_code=404, detail="Provider not configured")
    redirect_uri = getattr(settings, f"{provider}_redirect_uri", None) or ""
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    if not settings.enable_oauth:
        raise HTTPException(status_code=400, detail="OAuth disabled")
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)
    if provider == "google":
        userinfo = token.get("userinfo")
        if not userinfo:
            resp = await client.get("userinfo")
            userinfo = resp.json()
        email = userinfo.get("email"); pid = userinfo.get("sub")
    elif provider == "github":
        resp = await client.get("user"); userinfo = resp.json()
        email = userinfo.get("email") or (await client.get("user/emails")).json()[0]["email"]
        pid = str(userinfo.get("id"))
    else:
        raise HTTPException(status_code=400, detail="Unknown provider")

    if not email: raise HTTPException(status_code=400, detail="Email not available")

    u = db.query(User).filter(User.provider==provider, User.provider_id==pid).first()
    if not u:
        u = db.query(User).filter(User.email==email).first()
        if not u:
            u = User(email=email, provider=provider, provider_id=pid)
            db.add(u)
        else:
            u.provider = provider; u.provider_id = pid
        db.commit()
    from ..utils.security import create_jwt
    jwt_token = create_jwt(u.id, expires_minutes=settings.oauth_jwt_exp_min)
    return {"token": jwt_token, "user": {"id": u.id, "email": u.email, "role": u.role}}
