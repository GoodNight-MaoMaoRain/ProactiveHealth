from sqlalchemy.orm import Session
from pg_sql.models import FaceInfo
from typing import Optional
from uuid import UUID


def get_face_info(db: Session, user_id: UUID) -> Optional[FaceInfo]:
    return db.query(FaceInfo).filter(FaceInfo.user_id == user_id).first()


def update_face_info(db: Session, face_info: FaceInfo) -> None:
    db.add(face_info)
    db.commit()
    db.refresh(face_info)
