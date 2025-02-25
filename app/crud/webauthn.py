from models.models import WebAuthnCredential
from sqlalchemy.orm import Session


def create_webauthncredential(db: Session, webauthncredential: WebAuthnCredential) -> WebAuthnCredential:
    db.add(webauthncredential)
    db.commit()
    db.refresh(webauthncredential)

    return webauthncredential


def get_webauthncredential(db: Session, webauthncredential_id: bytes) -> WebAuthnCredential:
    return db.query(WebAuthnCredential).filter(WebAuthnCredential.credential_id == webauthncredential_id).first()


def update_webauthncredential(db: Session, webauthncredential: WebAuthnCredential) -> WebAuthnCredential:
    db_webauthncredential = get_webauthncredential(db, webauthncredential.credential_id)
    if db_webauthncredential:
        db_webauthncredential.sign_count = webauthncredential.current_sign_count
        db.commit()
    return db_webauthncredential
