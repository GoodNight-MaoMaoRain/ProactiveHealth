import datetime
from sqlalchemy import Column, Integer, Enum, Float, String, DateTime, LargeBinary,UUID
from common.enums import FatAccumulation,DrowsinessDegree,NeckLength,Nasolabial,LowerJaw
from pg_sql.database import Base
import uuid


class FaceInfo(Base):
    __tablename__ = 'face_info'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)

    # 颈围
    front_photo = Column(LargeBinary, nullable=True)  # 保存正脸的完整照片
    neck_circumference = Column(Float, nullable=True)
    neck_circumference_photo = Column(LargeBinary, nullable=True)
    neck_length_analysis = Column(Enum(NeckLength), nullable=True) # 异常结果
    # 面部脂肪堆积
    facial_fat_accumulation = Column(Enum(FatAccumulation), nullable=True)
    facial_fat_accumulation_photo = Column(LargeBinary, nullable=True)

    # 鼻唇角
    side_photo = Column(LargeBinary, nullable=True)  # 保存侧脸的完整照片
    nasolabial_angle = Column(Float, nullable=True)
    nasolabial_angle_photo = Column(LargeBinary, nullable=True)
    nasolabial_corners_analy = Column(Enum(Nasolabial), nullable=True) # 异常结果

    # 下颌骨
    mandible = Column(Float, nullable=True)
    mandible_photo = Column(LargeBinary, nullable=True)
    lower_jaw_corner_analy = Column(Enum(LowerJaw), nullable=True)  # 异常结果



class Ess(Base):
    __tablename__ = "sleep_ess"
    id = Column(Integer, primary_key=True, index=True)
    # 患者姓名
    patient_name = Column(String, default=None)
    # BMI
    bmi = Column(Float, nullable=True)
    # 总分
    score = Column(Integer, nullable=False)
    # 嗜睡程度
    drowsiness_degree = Column(Enum(DrowsinessDegree), nullable=False)
    # 创建时间
    create_time = Column(DateTime, default=datetime.datetime.utcnow, index=True)
