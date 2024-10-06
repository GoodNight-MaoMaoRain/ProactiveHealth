from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.schemas import ESSQuestionnaire
from services.ess_questionnaire import handle_ess_submission
from pg_sql.database import get_db

router = APIRouter()

@router.post('/submit_ess')
async def submit_ess(data: ESSQuestionnaire, db: Session = Depends(get_db)):
    result = handle_ess_submission(data, db)
    return result

