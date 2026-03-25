from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic model validates the incoming request body.
# If "question" is missing or not a string, FastAPI
# automatically returns a 422 error — no manual validation needed.
class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: QueryRequest):
    # .invoke() is synchronous. In production you'd use
    # .ainvoke() for async to avoid blocking the event loop.
    response = rag_chain.invoke(request.question)
    return {"answer": response}

# Run with: uvicorn main:app --reload