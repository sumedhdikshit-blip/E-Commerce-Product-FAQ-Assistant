from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from app.resources.router import get_route
from app.resources.faq import faq_chain
from app.resources.sql import ProductRAG

app = FastAPI(title="E-Commerce Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

product_rag = ProductRAG()


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/chat")
async def chat(req: ChatRequest):
    query = req.message.strip()

    if not query:
        return JSONResponse(status_code=400, content={"response": "Please enter a message."})

    try:
        route = get_route(query)

        if route == "faq":
            answer = faq_chain(query)
        elif route == "sql":
            answer = product_rag.ask(query)
        else:
            answer = (
                "Sorry, I can only help with FAQs, products, pricing, "
                "ratings, discounts and catalog-related questions."
            )

        return {"response": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"response": f"Error: {str(e)}"})


@app.get("/health")
async def health():
    return {"status": "ok"}