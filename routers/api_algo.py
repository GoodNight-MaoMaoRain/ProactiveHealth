from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.schemas import ImageRequest, FaceInfoResponse
from crud.crud_algo import get_face_info
from uuid import UUID
from pg_sql.database import get_db
from services.to_algo import encode_image_to_base64, process_side_photo, process_front_photo

router = APIRouter()

@router.get("/get-photos/{user_id}", response_model=FaceInfoResponse)
async def get_photos(user_id: UUID, db: Session = Depends(get_db)) -> FaceInfoResponse:
    face_info = get_face_info(db, user_id)
    if not face_info:
        raise HTTPException(status_code=404, detail="FaceInfo not found")

    front_photo_base64 = encode_image_to_base64(face_info.front_photo)
    side_photo_base64 = encode_image_to_base64(face_info.side_photo)

    return FaceInfoResponse(
        front_photo=front_photo_base64,
        side_photo=side_photo_base64
    )

@router.post("/get-front-photo/")
async def get_front_photo(image_request: ImageRequest, db: Session = Depends(get_db)) -> dict:
    result = await process_front_photo(image_request, db)
    return result

@router.post("/get-side-photo/")
async def get_side_photo(image_request: ImageRequest, db: Session = Depends(get_db)) -> dict:
    result = await process_side_photo(image_request, db)
    return result







