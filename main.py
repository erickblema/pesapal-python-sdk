from fastapi import FastAPI

app = FastAPI(
    title="SDK Payments API",
    description="Payment processing SDK API",
    version="1.0.0"
)


@app.get("/")
async def hello():
    """Hello message endpoint"""
    return {"message": "Hello, World!"}
