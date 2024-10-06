from typing import Optional
from pydantic import BaseModel, Field, conint
from common.enums import SleepinessLevel
from uuid import UUID


# 定义Ess问卷的模型
class ESSQuestionnaire(BaseModel):
    height: conint(gt=0) = Field(..., description='身高，单位为厘米')
    weight: conint(gt=0) = Field(..., description='体重，单位为千克')

    q1: SleepinessLevel
    q2: SleepinessLevel
    q3: SleepinessLevel
    q4: SleepinessLevel
    q5: SleepinessLevel
    q6: SleepinessLevel
    q7: SleepinessLevel
    q8: SleepinessLevel


class QuestionModel(BaseModel):
    question: str


class ImageRequest(BaseModel):
    image_base64: str
    user_id: UUID

class FaceInfoResponse(BaseModel):
    front_photo: Optional[str] = None
    side_photo: Optional[str] = None

class Content(BaseModel):
    content: str = None


class FaceInfo(BaseModel):
    user_id: UUID
    neck_circumference: float
    facial_fat_accumulation: str
    nasolabial_angle: float
    mandible: float

class FaceResponse(BaseModel):
    errno: str
    result: dict