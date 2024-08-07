# SO Insights Backend

This is the backend service for the SO Insights project. It's built with FastAPI and uses MongoDB for data storage.

## Building the Docker Image
```bash
docker build -t so-insights-backend -f backend/Dockerfile .
```
   
Note: The build command is run from the root directory of the project, not from the backend directory. This is because the Dockerfile needs access to the `shared` package located in the parent directory.

## Running the Docker Container

Create a `.env` file in the `backend` directory if it doesn't exist already. Add your environment variables.

2. Run the Docker container:
```bash
docker run -p 8000:8000 --e MONGODB_URI="..." -e MONGODB_DATABSE="actual_db_name" so-insights-backend
```
3. The API should now be accessible at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development
For development purposes, you might want to run the application outside of Docker. To do this:

1. Ensure you have Python 3.12 installed.
2. Install Poetry: `pip install poetry`
3. Navigate to the backend directory: `cd backend`
4. Install dependencies: `poetry install`
5. Run the application: `poetry run uvicorn src.api:app --reload`