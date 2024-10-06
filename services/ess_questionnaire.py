from pydantic import ValidationError
from sqlalchemy.orm import Session
from schemas.schemas import ESSQuestionnaire
from pg_sql.models import DrowsinessDegree
from crud.crud_ess import create_ess_entry
from loguru import logger


def calculate_score(data):
    try:
        score = sum([
            data.q1.value, data.q2.value, data.q3.value, data.q4.value,
            data.q5.value, data.q6.value, data.q7.value, data.q8.value
        ])
        logger.info(f"嗜睡得分计算成功，得分为: {score}")
        return score

    except Exception as e:
        logger.error(f"嗜睡得分计算失败: {str(e)}")
        return {"errno": "1", "msg": f"嗜睡得分计算失败: {str(e)}"}


def calculate_bmi(height, weight):
    try:
        height_in_meters = height / 100.0
        bmi = weight / (height_in_meters ** 2)
        logger.info(f"BMI 计算成功，BMI值为: {bmi}")
        return round(bmi, 2)

    except ZeroDivisionError as e:
        logger.error(f"BMI 计算失败，可能由于无效的身高值: {str(e)}")
        return {"errno": "1", "msg": f"BMI 计算失败，可能由于无效的身高值: {str(e)}"}
    except Exception as e:
        logger.error(f"BMI 计算失败: {str(e)}")
        return {"errno": "1", "msg": f"BMI 计算失败: {str(e)}"}


def handle_ess_submission(data: ESSQuestionnaire, db: Session):
    try:
        score = calculate_score(data)
        if isinstance(score, dict):  # 检查是否返回错误字典
            return score

        bmi = calculate_bmi(data.height, data.weight)
        if isinstance(bmi, dict):  # 检查是否返回错误字典
            return bmi

        # 根据得分确定嗜睡程度
        if score < 9:
            drowsiness_degree = DrowsinessDegree.NORMAL
        elif score < 15:
            drowsiness_degree = DrowsinessDegree.SUSPICIOUS
        else:
            drowsiness_degree = DrowsinessDegree.EXCESSIVE

        # 创建 ESS 数据库记录
        ess_entry = create_ess_entry(db, "路人甲", bmi, score, drowsiness_degree)

        result = {
            "status": "success",
            "score": score,
            "bmi": bmi,
            "result": f"根据得分和BMI的结果,您的测试结果为{drowsiness_degree.value}",
            "bmi_result": f"您的 BMI 是 {bmi}"
        }

        return {"errno": "0", "result": result}

    except ValidationError as e:
        return {"errno": "1", "msg": f"数据验证失败: {str(e)}"}

    except ValueError as e:
        return {"errno": "1", "msg": f"数据处理失败: {str(e)}"}

    except Exception as e:
        return {"errno": "1", "msg": f"提交失败: {str(e)}"}

    # 提交数据的格式为：{
    #     "height": 175,
    #     "weight": 70,
    #     "q2": "MODERATE_CHANCE",
    #     "q3": "SLIGHT_CHANCE",
    #     "q4": "NO_CHANCE",
    #     "q5": "HIGH_CHANCE",
    #     "q6": "MODERATE_CHANCE"
    # }