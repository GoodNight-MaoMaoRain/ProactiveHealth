from fastapi import APIRouter, UploadFile, File, Request, Form, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from loguru import logger
from uuid import uuid4
import uuid
from crud.crud_face import delete_photo
from pg_sql.database import get_db
from common.enums import PhotoType
from services.face_recognition import handle_upload_photo, process_results, get_result

router = APIRouter()


@router.get('/generate_uuid', summary='获取uuid')
async def generate_uuid():
    try:
        new_uuid = uuid4()
        return {"errno": "0", "uuid": str(new_uuid)}
    except Exception as e:
        return {"errno": "1", "msg": f"UUID 生成失败: {e}"}


@router.post('/upload_photo', summary='上传用户照片')
async def upload_photo(
        request: Request,
        photo_type: PhotoType = Form(...),
        photo: UploadFile = File(...),
        user_id: uuid.UUID = Form(None),  # 这里可以是 None，表示可选
        db: Session = Depends(get_db)
):
    try:
        logger.info(f"请求方法: {request.method} 请求路径: {request.url.path}")
        logger.info(f"photo_type: {photo_type}")

        # 确保 photo_type 是合法的
        if photo_type not in ["front", "side"]:
            return {"errno": "1", "msg": "无效的照片类型"}

        file_content = await photo.read()

        # 处理 user_id
        if not user_id:
            user_id = uuid.uuid4()  # 生成新的 UUID

        # 调用服务层处理上传逻辑
        result = await handle_upload_photo(photo_type=photo_type, file_content=file_content, user_id=user_id, db=db)

        return result

    except SQLAlchemyError as e:
        logger.error(f"数据库操作失败: {e}")
        return {"errno": "1", "msg": "数据库操作失败"}
    except Exception as e:
        logger.error(f"上传{photo_type}照片失败: {e}")
        return {"errno": "1", "msg": f'上传{photo_type}照片失败：{e}'}


@router.delete('/delete_photo', summary='删除用户上传照片')
async def delete_user_photo(
        user_id: uuid.UUID = Form(...),
        photo_type: PhotoType = Form(...),
        db: Session = Depends(get_db)
):
    try:
        result = delete_photo(db, user_id, photo_type.value)
        if result:
            logger.info(f'UUID {user_id} 的{photo_type.value}照片已删除')
            return {"status": "success", "message": f"{photo_type.value} 照片已删除"}
        else:
            return {"errno": "1", "msg": "用户记录未找到或无效的照片类型"}

    except SQLAlchemyError as e:
        logger.error(f"数据库操作失败: {e}")
        return {"errno": "1", "msg": "数据库操作失败"}
    except Exception as e:
        logger.error(f"删除照片失败: {e}")
        return {"errno": "1", "msg": f'删除照片失败：{e}'}


@router.get('/get_results/', summary='获取由算法产生的值')
async def get_results(request: Request, user_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        logger.info(f"请求方法: {request.method} 请求路径: {request.url.path}")
        result = await process_results(user_id, db)
        return {"errno": "0", "result": result}
    except Exception as e:
        logger.error(f"获取用户{user_id}结果失败: {e}")
        return {'errno': '1', "msg": f'获取用户{user_id}结果失败：{e}'}


@router.get('/detection_result/', summary='获取患病概率')
async def get_detection_result(user_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        result = await get_result(user_id, db)
        return result
    except Exception as e:
        logger.error(f'获取结果失败：{e}')
        return {'errno': '1', "msg": f'获取结果失败：{e}'}
