import asyncio
import os
from pathlib import Path
from sqlalchemy import select
from app.core.database import async_session_maker as async_session_factory
from app.models.models import User, Document
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

async def verify():
    with open("results.txt", "w", encoding="utf-8") as out:
        def log(msg):
            print(msg)
            out.write(msg + "\n")

        log("="*30)
        log("VERIFYING SYSTEM STATE")
        log("="*30)

        # 1. Check Uploads Directory
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            log(f"[WARN] Uploads directory {uploads_dir.absolute()} does not exist!")
        else:
            log(f"[OK] Uploads directory found at {uploads_dir.absolute()}")
            files = list(uploads_dir.glob("*"))
            if not files:
                log("  [WARN] No files in uploads directory.")
            else:
                log(f"  Found {len(files)} files:")
                for f in files:
                    log(f"  - {f.name} ({f.stat().st_size} bytes)")

        # 2. Check Database
        log("\n[INFO] Checking Database...")
        async with async_session_factory() as db:
            # Users
            users = (await db.execute(select(User))).scalars().all()
            log(f"  Found {len(users)} Users:")
            for u in users:
                log(f"  - ID: {u.id}, Email: {u.email}, Name: {u.name}")

            # Documents
            docs = (await db.execute(select(Document))).scalars().all()
            log(f"  Found {len(docs)} Documents:")
            for d in docs:
                user_email = "Unknown"
                if d.user_id:
                    user = await db.get(User, d.user_id)
                    user_email = user.email if user else "Orphaned"
                
                exists = Path(d.file_path).exists()
                status_icon = "[OK]" if exists else "[MISSING]"
                log(f"  {status_icon} ID: {d.id}")
                log(f"       Filename: {d.original_filename}")
                log(f"       Path: {d.file_path}")
                log(f"       User: {user_email}")
                log(f"       Type: {d.file_type}")
                log("-" * 20)

if __name__ == "__main__":
    asyncio.run(verify())
