from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio
import aiomysql
from ollama import AsyncClient

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Federal Documents RAG Agent",
    description="API for querying federal documents using local Ollama LLM",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database model
class UserQuery(BaseModel):
    query: str

# Global database connection pool
db_pool = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool"""
    global db_pool
    try:
        db_pool = await aiomysql.create_pool(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', 3306)),
            autocommit=True
        )
        print("✅ Database pool created successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections"""
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()
        print("✅ Database pool closed")

async def get_federal_documents(keyword: str):
    """Query federal documents from MySQL database"""
    if not db_pool:
        return "Database connection not available"
    
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("""
                    SELECT title, publication_date, summary 
                    FROM federal_documents
                    WHERE title LIKE %s OR summary LIKE %s
                    ORDER BY publication_date DESC
                    LIMIT 5
                """, (f"%{keyword}%", f"%{keyword}%"))
                
                results = await cur.fetchall()
                if not results:
                    return f"No documents found containing '{keyword}'"
                
                return "\n".join(
                    f"• {doc['title']} ({doc['publication_date']}): {doc['summary'][:150]}..."
                    for doc in results
                )
    except Exception as e:
        print(f"Database query error: {e}")
        return f"Error retrieving documents: {str(e)}"

async def process_user_query(user_prompt: str):
    """Process user query with Ollama LLM"""
    try:
        client = AsyncClient(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        
        # Keywords that trigger database lookup
        db_keywords = [
            'climate', 'ai', 'artificial intelligence', 
            'environment', 'policy', 'regulation'
        ]
        
        # Check if query requires database lookup
        requires_db = any(keyword in user_prompt.lower() for keyword in db_keywords)
        
        if requires_db:
            # Get relevant documents from database
            search_term = next(
                (keyword for keyword in db_keywords 
                 if keyword in user_prompt.lower()),
                "general"
            )
            db_results = await get_federal_documents(search_term)
            
            # Create LLM prompt with context
            llm_prompt = (
                f"User question: {user_prompt}\n\n"
                f"Relevant federal documents:\n{db_results}\n\n"
                "Please provide a concise answer based on these documents."
            )
            
            response = await client.chat(
                model='qwen2:0.5b',
                messages=[{'role': 'user', 'content': llm_prompt}],
                options={'temperature': 0.3}  # More factual responses
            )
            return response['message']['content']
        
        # For general knowledge questions
        response = await client.chat(
            model='qwen2:0.5b',
            messages=[{'role': 'user', 'content': user_prompt}],
            options={'temperature': 0.7}  # More creative responses
        )
        return response['message']['content']
        
    except Exception as e:
        print(f"LLM processing error: {e}")
        return f"Sorry, I encountered an error processing your request: {str(e)}"

@app.post("/api/query")
async def chat_with_agent(user_data: UserQuery):
    """API endpoint for user queries"""
    try:
        if not user_data.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        print(f"Processing query: '{user_data.query}'")
        response = await process_user_query(user_data.query)
        return {"response": response}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"API error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing your query"
        )

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "running",
        "llm": "Ollama (qwen2:0.5b)",
        "database": "MySQL"
    }