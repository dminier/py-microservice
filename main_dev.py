from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "myproject.application.bootstrap:Bootstrap.create_app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
