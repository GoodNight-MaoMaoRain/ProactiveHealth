from sqlalchemy.orm import Session
from pg_sql.models import Ess
from loguru import logger


def create_ess_entry(db: Session, patient_name: str, bmi: float, score: int, drowsiness_degree: str):
    try:
        ess_entry = Ess(
            patient_name=patient_name,
            bmi=bmi,
            score=score,
            drowsiness_degree=drowsiness_degree
        )
        db.add(ess_entry)
        db.commit()
        logger.info(f"ESS 记录创建成功: {ess_entry}")
        return ess_entry

    except Exception as e:
        logger.error(f"ESS 记录创建失败: {str(e)}")
        return {'errno':'1','msg':str(e)}
