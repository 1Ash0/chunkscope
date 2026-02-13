import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Minimal setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
try:
    from app.core.database import engine, get_async_database_url
except ImportError:
    def get_async_database_url():
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

async def list_presets():
    output_file = "presets_list.txt"
    with open(output_file, "w") as f:
        f.write("--- Listing all presets in Neon ---\n")
        try:
            url = get_async_database_url()
            eng = create_async_engine(url, echo=False)
            async with eng.connect() as conn:
                res = await conn.execute(text("SELECT id, name, category, configuration FROM presets;"))
                presets = res.fetchall()
                for p in presets:
                    line = f"ID: {p[0]} | Name: {p[1]} | Category: {p[2]}\n"
                    f.write(line)
                    print(line, end="", flush=True)
            await eng.dispose()
            f.write("--- End of List ---\n")
        except Exception as e:
            f.write(f"ERROR: {e}\n")
            print(f"ERROR: {e}", flush=True)
    print(f"\nResults written to {output_file}", flush=True)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(list_presets())
