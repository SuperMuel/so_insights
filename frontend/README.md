# SO Insights Frontend

A Streamlit-based web interface for the SO Insights project, providing access to workspace management, data ingestion, chatbot interaction, and topic analysis features.

## Features

- Workspace management
- Data ingestion interface
- Chatbot for data interaction
- Topic analysis visualization

## Prerequisites

- Python 3.12+
- Working Backend API
- API Key(s) for the chatbot LLM
- Voyage API key for retrieving documents

## Quick Start
1. Install dependencies:
    ```
    poetry install
    ```

2. Set up environment variables:
   Create a `.env` file with:
   ```
   SO_INSIGHTS_API_URL=your_backend_api_url
   VOYAGEAI_API_KEY=your_voyageai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index
   ```

4. Locally run the application:
   ```
   poetry run streamlit run app.py
   ```

## Project Structure

- `app.py`: Main entry point
- `pages/`: Individual pages for different features
- `src/`: Utility functions and settings
- `sdk/`: Generated API client for backend communication



## Generating Backend SDK

To update the backend SDK used by the frontend:

1. Navigate to the backend directory:
   ```
   cd ../backend
   ```

2. Run the SDK generation script:
   ```
   poetry run python generate_client_sdk.py -o ../frontend/sdk
   ```

This command will generate the SDK based on the current backend API and place it in the `frontend/sdk` directory.








