import uuid
from sqlalchemy.orm import Session
from pg_sql.models import FaceInfo


def get_face_info(db: Session, user_id: uuid.UUID):
    return db.query(FaceInfo).filter(FaceInfo.user_id == user_id).first()


def delete_photo(db: Session, user_id: uuid.UUID, photo_type: str):
    db_face_info = get_face_info(db, user_id)
    if not db_face_info:
        return None

    if photo_type == "front":
        db_face_info.front_photo = None
    elif photo_type == "side":
        db_face_info.side_photo = None
    else:
        return None

    db.add(db_face_info)
    db.commit()
    return db_face_info
