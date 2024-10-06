import httpx
import asyncio
import json

import httpx
import asyncio
import json


# 异步获取机器人响应
async def get_robot_response(content: str):
    """
    发送内容到指定的URL，获取机器人响应。

    :param content: 发送给机器人的文本内容
    :return: 机器人响应或错误信息
    """
    url = "http://192.168.10.97:8001/robot"
    params = {"content": content}  # 请求参数包含发送的文本内容

    try:
        # 使用 httpx 异步发送 GET 请求，无超时限制
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.get(url, params=params)
        response.raise_for_status()  # 如果请求返回的状态码是错误的，抛出异常
        response_data = response.json()  # 将响应转换为JSON格式

        # 从响应中提取 "robot_response" 字段
        if "robot_response" in response_data:
            return response_data["robot_response"]  # 如果字段存在，返回机器人响应
        else:
            return {'errno': '1', 'errmsg': 'not found robot_response'}

    except httpx.HTTPStatusError as exc:
        return {'errno': '1', 'errmsg': str(exc)}

    except Exception as exc:
        return {'errno': '1', 'errmsg': str(exc)}


# 异步事件生成器，用于逐字发送机器人响应
async def event_generator(robot_response: str, request):
    """
    逐字生成机器人响应的事件流。

    :param robot_response: 机器人返回的文本内容
    :param request: 请求对象，用于检查连接状态
    :return: 事件流，逐字发送机器人响应
    """
    for idx, word in enumerate(robot_response):
        # 检查请求是否断开连接
        if await request.is_disconnected():
            print("连接已中断")
            break  # 如果连接中断，停止生成事件

        # 将当前字转换为 JSON 格式
        data = json.dumps({"id": idx, "message": word}, ensure_ascii=False)

        # 使用 SSE (服务器发送事件) 发送数据，每次发送一个字
        yield f"data: {data}\n\n"

        # 模拟发送间隔，每个字等待 0.1 秒
        await asyncio.sleep(0.1)


# async def chat_bot(request: Request):
#     res_str = "这是一个流式输出他会将每个字挨个挨个的输出！！！"
#     for idx, word in enumerate(res_str):
#         if await request.is_disconnected():
#             print("连接已中断")
#             break
#         data = json.dumps({"id": idx, "message": word}, ensure_ascii=False)
#         yield data
#         await asyncio.sleep(0.1)
#
