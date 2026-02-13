import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import async_session_maker, init_db
from app.services.preset_service import preset_service
from sqlalchemy import select, text
from app.models.models import Preset

async def main():
    print("Initializing database connection...")
    await init_db()
    
    async with async_session_maker() as db:
        print("Checking existing presets...")
        result = await db.execute(select(Preset))
        presets = result.scalars().all()
        print(f"Found {len(presets)} existing presets.")
        
        print("Loading builtin presets (create or update)...")
        loaded = await preset_service.load_builtin_presets(db)
        print(f"Successfully processed {len(loaded)} presets.")
            
        # Verify
        result = await db.execute(select(Preset))
        count = len(result.scalars().all())
        print(f"Final preset count: {count}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
