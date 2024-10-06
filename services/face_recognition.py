import base64
import uuid
from loguru import logger
from sqlalchemy.orm import Session

from common.enums import FatAccumulation, NeckLength, Nasolabial, LowerJaw
from crud.crud_face import get_face_info
from pg_sql.models import FaceInfo
from schemas.schemas import ImageRequest
from services.to_algo import process_side_photo, process_front_photo


# 验证照片类型并处理相应的面部照片
async def validate_photo(photo_type: str, image_request: ImageRequest, db: Session):
    """
    根据传入的照片类型调用相应的处理函数，并返回验证结果。

    :param photo_type: 照片类型 (front 或 side)
    :param image_request: 包含Base64图像和用户ID的请求对象
    :param db: 数据库会话
    :return: 包含健康响应结果的字典
    """
    if photo_type == "front":
        result = await process_front_photo(image_request=image_request, db=db)
    elif photo_type == "side":
        result = await process_side_photo(image_request=image_request, db=db)
    else:
        result = {"health_response": "无效的照片类型"}

    # 如果健康响应是字典，则对其进行处理
    if isinstance(result.get('health_response', ''), dict):
        result['health_response'] = {
            "fat_accumulation": result['health_response'].get("fat_accumulation", ""),  # 获取脂肪堆积信息
            "fat_accumulation_image": result['health_response'].get("fat_accumulation_image", "")  # 获取脂肪图像
        }

    return result


# 处理上传的照片并保存到数据库
async def handle_upload_photo(photo_type: str, file_content: bytes, user_id: uuid.UUID, db: Session):
    """
    处理上传的照片，调用验证函数进行校验，并保存照片到数据库。

    :param photo_type: 照片类型 (front 或 side)
    :param file_content: 上传的照片字节内容
    :param user_id: 用户的UUID
    :param db: 数据库会话
    :return: 上传结果消息
    """
    # 将照片转换为Base64编码并创建ImageRequest对象
    image_request = ImageRequest(image_base64=base64.b64encode(file_content).decode('utf-8'), user_id=user_id)
    result = await validate_photo(photo_type, image_request, db)

    # 如果健康响应是字符串，则表示上传照片不符合要求
    if isinstance(result.get('health_response', ''), str):
        logger.info(f"上传的{photo_type}照片不符合要求")
        return {"errno": "1", "msg": result['health_response']}

    # 从数据库获取用户面部信息，如果不存在则创建新的记录
    db_face_info = get_face_info(db, user_id)
    if not db_face_info:
        db_face_info = FaceInfo(user_id=user_id)

    # 根据照片类型保存正面或侧面的照片到数据库
    if photo_type == "front":
        db_face_info.front_photo = file_content
    elif photo_type == "side":
        db_face_info.side_photo = file_content

    db.add(db_face_info)
    db.commit()

    logger.info(f'{photo_type} 照片已保存到数据库并通过校验')
    return {"errno": "0", "result": f"{photo_type} 照片上传并保存成功"}


# 处理并返回用户的健康分析结果
async def process_results(user_id: uuid.UUID, db: Session):
    """
    根据用户ID从数据库获取面部信息，并生成健康分析的结果。

    :param user_id: 用户的UUID
    :param db: 数据库会话
    :return: 包含健康分析结果的字典
    """
    # 从数据库获取用户面部信息
    db_face_info = get_face_info(db, user_id)
    # if not db_face_info:
    #     return {"errno": "1", "msg": "用户记录未找到"}

    results = {}

    # 如果存在正面照片，则对其进行处理并返回分析结果
    if db_face_info.front_photo:
        front_photo_base64 = base64.b64encode(db_face_info.front_photo).decode('utf-8')
        image_request = ImageRequest(image_base64=front_photo_base64, user_id=user_id)
        front_result = await validate_photo("front", image_request, db)
        if isinstance(front_result['health_response'], str):
            return {"errno": "1", "msg": front_result['health_response']}
        results.update({"front": front_result})

    # 如果存在侧面照片，则对其进行处理并返回分析结果
    if db_face_info.side_photo:
        side_photo_base64 = base64.b64encode(db_face_info.side_photo).decode('utf-8')
        image_request = ImageRequest(image_base64=side_photo_base64, user_id=user_id)
        side_result = await validate_photo("side", image_request, db)
        if isinstance(side_result['health_response'], str):
            return {"errno": "1", "msg": side_result['health_response']}
        results.update({"side": side_result})

    # 将所有面部信息组合到最终结果中
    result = {
        "user_id": str(db_face_info.user_id),
        "neck_circumference": db_face_info.neck_circumference,
        "facial_fat_accumulation": db_face_info.facial_fat_accumulation,
        "nasolabial_angle": db_face_info.nasolabial_angle,
        "mandible": db_face_info.mandible,
        'neck_length_analysis': db_face_info.neck_length_analysis.value if db_face_info.neck_length_analysis else None,
        'facial_fat_accumulation': db_face_info.facial_fat_accumulation.value if db_face_info.facial_fat_accumulation else None,
        'nasolabial_corners_analy': db_face_info.nasolabial_corners_analy.value if db_face_info.nasolabial_corners_analy else None,
        'lower_jaw_corner_analy': db_face_info.lower_jaw_corner_analy.value if db_face_info.lower_jaw_corner_analy else None,
    }
    results.update({"info": result})

    return result


# 从数据库中提取信息
async def get_result(user_id: uuid.UUID, db: Session):
    face_info = get_face_info(db, user_id)

    # 打印 face_info 中的字段，检查值是否正确
    print(f"facial_fat_accumulation: {face_info.facial_fat_accumulation}")
    print(f"neck_length_analysis: {face_info.neck_length_analysis}")
    print(f"nasolabial_corners_analy: {face_info.nasolabial_corners_analy}")
    print(f"lower_jaw_corner_analy: {face_info.lower_jaw_corner_analy}")

    # 初始化总分
    total_score = 0

    # 处理 facial_fat_accumulation 的得分逻辑
    if face_info.facial_fat_accumulation == FatAccumulation.EXCESSIVE:
        total_score += 25
    else:
        total_score += 0  # '过少' 或 '正常'

    # 处理 neck_length_analysis 的得分逻辑
    if face_info.neck_length_analysis == NeckLength.ABNORMAL:
        total_score += 25
    else:
        total_score += 0  # '正常'

    # 处理 nasolabial_corners_analy 的得分逻辑
    if face_info.nasolabial_corners_analy == Nasolabial.ABNORMAL:
        total_score += 25
    else:
        total_score += 0  # '正常'

    # 处理 lower_jaw_corner_analy 的得分逻辑
    if face_info.lower_jaw_corner_analy == LowerJaw.ABNORMAL:
        total_score += 25
    else:
        total_score += 0  # '正常'

    print(f"Total Score: {total_score}")

    return {"errno": "0", 'result': total_score}
