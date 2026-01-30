"""
Apply missing PostgreSQL enum types to Neon database.
Run this script once to create the enum types.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def create_enums():
    """Create missing PostgreSQL enum types."""
    enum_statements = [
        "CREATE TYPE document_type AS ENUM ('pdf', 'txt', 'md', 'docx', 'html', 'code');",
        "CREATE TYPE pipeline_status AS ENUM ('draft', 'running', 'completed', 'failed');",
        "CREATE TYPE evaluation_status AS ENUM ('pending', 'running', 'completed', 'failed');",
        "CREATE TYPE chunking_method AS ENUM ('fixed_size', 'recursive', 'semantic', 'sentence', 'paragraph', 'markdown', 'code', 'table', 'heading', 'agentic');",
    ]
    
    async with engine.begin() as conn:
        for stmt in enum_statements:
            try:
                await conn.execute(text(stmt))
                print(f"✅ Created: {stmt.split()[2]}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"⏭️  Already exists: {stmt.split()[2]}")
                else:
                    print(f"❌ Error: {e}")
    
    print("\nDone! Enum types are now available.")


if __name__ == "__main__":
    asyncio.run(create_enums())
