from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from loguru import logger
from settings import AppSettings
# 获取应用配置
settings = AppSettings()

# 创建 SQLAlchemy 引擎
try:
    engine = create_engine(settings.database_url)
    logger.info('数据库引擎启动成功')
except:
    logger.error('数据库引擎创建失败')
    engine = None # 确保异常情况下为None

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库会话管理
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 定义基类
Base = declarative_base()

# 创建数据库
def create_database():
    if engine is None:
        logger.error('数据库引擎不可用，无法创建表')
    try:
        Base.metadata.create_all(bind=engine)
        logger.info('所有表创建成功')
    except Exception as e:
        logger.error(f"表创建失败: {str(e)}")


# 关闭数据库连接
def dispose_database():
    engine.dispose()






