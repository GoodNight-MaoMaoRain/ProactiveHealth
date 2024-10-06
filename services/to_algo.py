import base64
import uuid

import httpx
import logging
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from common.enums import FatAccumulation, NeckLength,Nasolabial,LowerJaw
from fastapi import APIRouter, HTTPException

from pg_sql.models import FaceInfo
from schemas.schemas import ImageRequest
from crud.crud_algo import get_face_info, update_face_info

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI路由
router = APIRouter()


# 将图像的二进制数据转换为Base64编码字符串
def encode_image_to_base64(image_data: Optional[bytes]) -> Optional[str]:
    """将图像的二进制数据转换为Base64编码字符串"""
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None


# 将Base64编码的字符串解码为字节数据
def decode_base64_to_bytes(base64_str: Optional[str]) -> Optional[bytes]:
    """将Base64编码的字符串解码为字节数据"""
    if base64_str:
        return base64.b64decode(base64_str)
    return None


# 调用外部服务并处理异常
async def call_external_service(url: str, params: dict) -> dict:
    """
    异步调用外部服务，并处理请求相关的错误

    :param url: 外部服务的URL
    :param params: 请求的参数
    :return: 外部服务的响应结果，以字典形式返回
    """
    try:
        async with httpx.AsyncClient() as client:
            # 发送POST请求给外部服务
            response = await client.post(url, json=params)
        # 检查响应的状态，如果不是200则引发异常
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        # 捕获请求异常并记录日志
        logger.error(f"请求错误: {url}: {exc}")
        return {"errno": "1", "msg": f'请求失败: {str(exc)}'}

    except httpx.HTTPStatusError as exc:
        # 捕获HTTP状态异常并记录日志
        logger.error(f"HTTP状态错误: {exc.response.text}")
        return {"errno": "1", "msg": f'请求失败: {str(exc)}'}

    except Exception as exc:
        # 捕获其他任何异常并记录日志
        logger.error(f"发生未预期的错误: {str(exc)}")
        return {"errno": "1", "msg": f'发生错误: {str(exc)}'}


# 处理正面照片数据
async def process_front_photo(image_request: ImageRequest, db: Session) -> dict:
    """
    处理前脸照片，调用外部API获取健康信息并更新数据库

    :param image_request: 包含图像及用户ID的请求数据
    :param db: 数据库会话
    :return: 外部服务返回的数据
    """
    url = "http://192.168.10.97:8001/front_face"  # 外部服务的URL
    params = {"image_front_face": image_request.image_base64, "user_id": str(image_request.user_id)}
    data = await call_external_service(url, params)  # 调用外部服务

    health_response = data.get('health_response', {})  # 获取健康分析的响应
    if isinstance(health_response, dict):
        face_info = get_face_info(db, image_request.user_id)  # 从数据库获取用户面部信息
        if face_info:
            # 更新用户的面部健康信息
            face_info.neck_circumference = health_response.get('neck_length')
            face_info.neck_circumference_photo = decode_base64_to_bytes(health_response.get('neck_seg_image'))
            # 新增异常
            face_info.neck_length_analysis = NeckLength(health_response.get('neck_length_analy'))
            face_info.facial_fat_accumulation = FatAccumulation(health_response.get('fat_accumulation'))
            face_info.facial_fat_accumulation_photo = decode_base64_to_bytes(health_response.get('fat_accumulation_image'))

            update_face_info(db, face_info)  # 更新数据库中的面部信息

    return data


# 处理侧面照片数据
async def process_side_photo(image_request: ImageRequest, db: Session) -> dict:
    """
    处理侧脸照片，调用外部API获取健康信息并更新数据库

    :param image_request: 包含图像及用户ID的请求数据
    :param db: 数据库会话
    :return: 外部服务返回的数据
    """
    url = "http://192.168.10.97:8001/side_face"  # 外部服务的URL
    params = {"image_side_face": image_request.image_base64, "user_id": str(image_request.user_id)}
    data = await call_external_service(url, params)  # 调用外部服务

    health_response = data.get('health_response', {})  # 获取健康分析的响应
    if isinstance(health_response, dict):
        face_info = get_face_info(db, image_request.user_id)  # 从数据库获取用户面部信息
        if face_info:
            # 更新用户的面部健康信息
            face_info.nasolabial_angle = health_response.get('nasolabial_corners')
            face_info.nasolabial_angle_photo = decode_base64_to_bytes(health_response.get('img_nasolabial_corners'))
            face_info.nasolabial_corners_analy = Nasolabial(health_response.get('nasolabial_corners_analy'))
            face_info.mandible = health_response.get('lower_jaw_corner')
            face_info.mandible_photo = decode_base64_to_bytes(health_response.get('nasolabial_angle_photo'))
            face_info.lower_jaw_corner_analy = LowerJaw(health_response.get('lower_jaw_corner_analy'))

            update_face_info(db, face_info)  # 更新数据库中的面部信息

    return data
