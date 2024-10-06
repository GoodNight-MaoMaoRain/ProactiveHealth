import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from settings import AppSettings
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routers import api_ess, api_bot, api_algo, api_face
from pg_sql.database import create_database, dispose_database
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield
    dispose_database()


def get_application() -> FastAPI:
    settings = AppSettings()
    settings.configure_logging()

    app = FastAPI(
        title=settings.title,
        version=settings.version,
        lifespan=lifespan,
        debug=settings.debug,
        docs_url=None,

    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_face.router, prefix='/face', tags=['人脸识别'])
    app.include_router(api_ess.router, prefix='/ess', tags=['Ess嗜睡量表'])
    app.include_router(api_bot.router, prefix="/ai", tags=['问答机器人'])
    app.include_router(api_algo.router, prefix="", tags=['向算法服务器传人脸照'])

    return app


app = get_application()
# 挂载静态路由
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=settings.title,
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url="/static/swagger/img.png",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/swagger/redoc.standalone.js",
    )

if __name__ == '__main__':
    settings = AppSettings()
    uvicorn.run(app, host=settings.host, port=settings.port)
