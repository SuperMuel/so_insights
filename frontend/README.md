# SO Insights Frontend

The Streamlit-based web interface for the SO Insights project, providing a comprehensive platform for workspace management, data analysis, content generation, and chatbot interaction.

## Features

- **Workspace Management**: Create, edit, and switch between workspaces for different projects or topics.
- **Data Sources Management**: Configure and manage both web search and RSS feed ingestion sources, and more coming soon.
- **Topic Analysis**: Visualize and interact with clustering results from ingested data. Provide feedback to improve subsequent analyses.
- **Content Studio**: Generate social media content and blog posts based on analyzed topics, with AI-generated text and images.
- **Chatbot Interface**: Interact with your data through natural language queries.

## Prerequisites

- Python 3.12+
- Working Backend API
- API Keys for:
  - OpenAI (for GPT models)
  - Anthropic (for Claude models)
  - VoyageAI (for embeddings)
  - Pinecone (for vector database)
  - GetImg.ai (for image generation)

## Quick Start

1. Install dependencies:
    ```
    poetry install
    ```

2. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   SO_INSIGHTS_API_URL=your_backend_api_url
   VOYAGEAI_API_KEY=your_voyageai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GETIMG_API_KEY=your_getimg_api_key
   ```

   If you with to log LLM calls using [Langsmith](https://www.langchain.com/langsmith) :  
   ```
   LANGCHAIN_PROJECT=<your_langsmith_project>
   LANGCHAIN_API_KEY=<your_langsmith_api_key>
   LANGCHAIN_TRACING_V2=true
   ```

3. Locally run the application:
   ```
   poetry run streamlit run app.py
   ```

## Project Structure

- `app.py`: Main entry point and navigation setup
- `src/`:
  - `pages/`: Individual page implementations (workspaces, topics, content_studio, chatbot)
  - `shared.py`: Shared utility functions
  - `app_settings.py`: Application settings and configuration
  - `content_generation.py`: Functions for content generation
  - `image_generation.py`: Functions for image generation
- `sdk/`: Generated API client for backend communication

## Key Components

1. **Workspaces**: Manage multiple workspaces for different projects or topics.
2. **Topics**: Analyze and visualize detected topics in collected articles.
3. **Content Studio**: Generate content for various platforms (Twitter, LinkedIn, blog posts) based on analyzed topics.
4. **Chatbot**: Ask questions about your data using natural language.

## Customization

- The application supports custom logos for light and dark themes. Set `LOGO_LIGHT_URL` and `LOGO_DARK_URL` in your environment variables to use custom logos.
- Check the settings in `src/app_settings.py` to customize various aspects of the application, such as the number of clusters per page or auto-refresh intervals. Add environment variables to override these settings.

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


# Docker

To build the docker image, run : 

```bash
docker build -t so-insights-frontend -f frontend.Dockerfile .
```

To run the docker image, run :

```bash
docker run -p 8501:8501  -e STREAMLIT_SERVER_PORT=8501 -e STREAMLIT_SERVER_ADDRESS=localhost  -e SO_INSIGHTS_API_URL="<api_url>" --env-file .\frontend\.env     -t so-insights-frontend
```


# Authentication

The frontend application requires authentication to interact with the backend API. This is achieved using the organization's `X-Organization-ID` header.

### Login Flow

1. **Access Code Input:**
   - When accessing the application for the first time, users are prompted to enter a secret access code provided by the administrator.

2. **Exchange for Organization ID:**
   - The access code is sent to the backend API endpoint `/organizations/by-secret-code` to retrieve the corresponding `organization_id`.

3. **Session Persistence:**
   - The `organization_id` is stored in the user's session and used to authenticate subsequent API calls.

4. **Headers in API Requests:**
   - All API requests made by the frontend include the `X-Organization-ID` header to authenticate the user.
