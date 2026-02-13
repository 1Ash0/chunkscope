import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Minimal setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

async def get_user():
    load_dotenv()
    url = os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+asyncpg://')
    eng = create_async_engine(url)
    async with eng.connect() as conn:
        res = await conn.execute(text('SELECT id, email FROM users LIMIT 1;'))
        user = res.fetchone()
        if user:
            print(f"USER_ID: {user[0]}")
            print(f"USER_EMAIL: {user[1]}")
    await eng.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(get_user())
