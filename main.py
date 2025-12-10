from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from trading.api.routes import router as orders_router
from trading.api.auth_routes import router as auth_router  # ← Tambah import

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading Platform API",
    description="RESTful API untuk trading cryptocurrency dengan DDD",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)  # ← Register auth router
app.include_router(orders_router)  # ← Register orders router


@app.get("/")
def root():
    return {"message": "Trading Platform API", "version": "1.0.0", "docs": "/docs"}


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
