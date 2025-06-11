import aiohttp
import asyncio
import aiomysql
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

async def create_database_pool():
    return await aiomysql.create_pool(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        autocommit=True
    )

async def run_pipeline():
    pool = None
    try:
        pool = await create_database_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS federal_documents (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        document_number VARCHAR(255) UNIQUE,
                        title TEXT,
                        publication_date DATE,
                        summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Sample data
                await cur.execute("""
                    INSERT INTO federal_documents 
                    (document_number, title, publication_date, summary)
                    VALUES 
                    ('2025-001', 'AI Regulation Framework', '2025-01-15', 'New guidelines for AI development'),
                    ('2025-002', 'Climate Change Action Plan', '2025-02-20', 'Federal climate policy updates')
                    ON DUPLICATE KEY UPDATE title=VALUES(title)
                """)
                
        print("Pipeline completed successfully")
        
    except Exception as e:
        print(f"Pipeline error: {e}")
    finally:
        if pool:
            pool.close()
            await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run_pipeline())