from sqlalchemy.orm import Session
from app.models.user import TokenBlacklist

def blacklist_token(db: Session, token: str):
    db.add(TokenBlacklist(token=token))
    db.commit()

def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(TokenBlacklist).filter_by(token=token).first() is not None