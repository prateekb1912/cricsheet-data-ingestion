from app import app  # Import the FastAPI app

if __name__ == "__main__":
    import os
    import uvicorn
    os.environ.setdefault("UVICORN_ENV", "production")  # Set environment variable if needed
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run the app with Uvicorn 