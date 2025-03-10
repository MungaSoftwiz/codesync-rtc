from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, projects

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Collaborative Coding Platform"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
