"""
Fix database column type mismatch.
Alters file_type column from document_type enum to VARCHAR.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def fix_column_type():
    """Alter file_type column to VARCHAR."""
    statements = [
        # Remove the old enum-typed column constraint and change to varchar
        """ALTER TABLE documents 
           ALTER COLUMN file_type TYPE VARCHAR(20) 
           USING file_type::text;""",
    ]
    
    async with engine.begin() as conn:
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
                print("SUCCESS: Column altered to VARCHAR(20)")
            except Exception as e:
                if "already" in str(e).lower():
                    print("Already VARCHAR, skipping")
                else:
                    print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(fix_column_type())
