import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router, templates

def create_app() -> FastAPI:
    app = FastAPI(title="Modern AI Chatbot", version="1.0.0")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(router)
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
