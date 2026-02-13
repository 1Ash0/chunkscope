import asyncio
import os
import sys
import json

# Minimal setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from app.core.database import engine, get_async_database_url
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def verify_pipeline_config():
    print("Verifying Pipeline Configuration mapping...", flush=True)
    url = get_async_database_url()
    eng = create_async_engine(url, echo=False, connect_args=engine.connect_args if hasattr(engine, 'connect_args') else {})
    
    try:
        async with eng.connect() as conn:
            # Check the most recent pipeline
            res = await conn.execute(text("""
                SELECT id, name, settings, nodes 
                FROM pipelines 
                ORDER BY created_at DESC LIMIT 1;
            """))
            pipe = res.fetchone()
            if pipe:
                print(f"\n--- PIPELINE: {pipe[0]} ---", flush=True)
                print(f"Name: {pipe[1]}", flush=True)
                
                settings = pipe[2] if isinstance(pipe[2], dict) else json.loads(pipe[2])
                print(f"Settings (Chunking): {settings.get('chunking')}", flush=True)
                
                # Check nodes for chunking node
                nodes = pipe[3] if isinstance(pipe[3], list) else json.loads(pipe[3])
                for node in nodes:
                    if node.get('type') == 'chunking':
                        print(f"Chunking Node Data: {node.get('data')}", flush=True)
            else:
                print("No pipeline found!", flush=True)
                
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
    finally:
        await eng.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_pipeline_config())
