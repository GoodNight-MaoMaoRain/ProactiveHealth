from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from schemas.schemas import Content
from services.chatbot import get_robot_response, event_generator

router = APIRouter()

@router.post("/call-robot/")
async def call_robot(request: Request, content: Content):
    try:
        # 获取机器人响应
        robot_response = await get_robot_response(content.content)
        print(robot_response)
        # 使用生成器流式返回数据
        return StreamingResponse(event_generator(robot_response, request), media_type="text/event-stream")
    except Exception as exc:
        return {'errno':'1', 'errmsg':f'An error occurred: {str(exc)}'}
