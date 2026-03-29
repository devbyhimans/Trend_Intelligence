# Main entry point for the FastAPI application
from fastapi import FastAPI
from app.routes import search
from app.routes import health
from app.routes import trends
from app.routes import region
from app.models.search import Base
from app.db.connection import engine

# Initialize the FastAPI app instance
app = FastAPI()

Base.metadata.create_all(bind=engine)


# Register the search router to include its endpoints in the main app
app.include_router(search.router)
app.include_router(health.router)
app.include_router(trends.router)
app.include_router(region.router)

# Define a simple health-check route at the root URL ("/")
@app.get("/")
def root():
    # Health-check endpoint to affirm the API is running
    # Return a basic status message confirming the API is alive
    return {"status": "API running"}