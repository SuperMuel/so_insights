# SO Insights Backend

This is the backend service for the SO Insights project. It's built with FastAPI and uses MongoDB for data storage.

## Building the Docker Image

To build the Docker image for the backend service, run the following command from the root directory of the project:

```bash
docker build -t so-insights-api -f Dockerfile.api .
```

Note: The build command is run from the root directory of the project, not from the backend directory. This is because the Dockerfile needs access to both the `backend` and `shared` directories.

## Running the Docker Container

1. Set up environment variables:
   You can either set environment variables directly or use a `.env` file.

   - `MONGODB_URI`: Your MongoDB connection string
   - `PORT` (optional): The port on which the API will run (default is 8000)

2. Run the Docker container:

   ```bash
   docker run -p 8000:8000 \
     -e MONGODB_URI="mongodb://your_mongodb_uri" \
     -e MONGODB_DATABASE="your_database_name" \
     -e PORT=8000 \
     so-insights-api
   ```

   Or, if you prefer using a `.env` file:

   ```bash
   docker run -p 8000:8000 --env-file ./backend/.env so-insights-api
   ```

3. The API should now be accessible at `http://localhost:8000` (or the port you specified).

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
5. Set up your environment variables in a `.env` file in the `backend` directory.
6. Run the application: `poetry run uvicorn src.api:app --reload`

# Authentication

The SO Insights backend requires organization-level authentication for accessing most of its resources. This is done using the X-Organization-ID header in the request.

### Authentication Flow
SoInsights Administrators create Organizations and their access codes for the clients.
Users receive the code and use it to login on the platform. 
Internally, the code is exchanged against the organization ID, which is subsequently sent in each request as `X-Organization-ID` header.
We wrongly assume that the org ID can't be guessed, and dangerously use it for authentication.

### Important Notes

This authentication mechanism is not highly secure and is designed for demonstration purposes. Ensure that access codes are kept private.

Future updates may introduce more robust authentication mechanisms