from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from trading.infrastructure.models import OrderModel, TradeModel
from trading.api.routes import router as orders_router

print("=" * 60)
print("Starting Trading Platform API...")
print("=" * 60)

print("\nCreating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created!")

app = FastAPI(
    title="Trading Platform API",
    description="DDD Implementation - Trading Context (Core Domain)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders_router)

@app.get("/")
def root():
    return {
        "message": "Trading Platform API",
        "status": "running",
        "version": "1.0.0",
        "database": "SQLite",
        "docs": "http://localhost:8000/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("Server: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)