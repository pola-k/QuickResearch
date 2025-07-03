# QuickResearch

A powerful document processing and conversational AI system that enables intelligent querying of academic papers through advanced document analysis, multimodal content extraction, and semantic search capabilities.

## Features

🔍 **Intelligent Document Processing**: Extracts and analyzes text, tables, and images from PDF documents using advanced AI models

📊 **Multimodal Content Analysis**: Processes and summarizes different content types including text chunks, tables, and images

🤖 **Conversational AI Interface**: Chat with your documents using natural language queries

🗄️ **Hybrid Storage System**: Combines vector search with SQL database for efficient document retrieval

🔗 **RESTful API**: FastAPI-based backend with CORS support for web applications

📁 **Document Management**: Upload, delete, and manage multiple PDF documents

## Architecture

QuickResearch is a full-stack application with a sophisticated architecture:

### Backend
- **Vector Database**: Chroma for semantic search and document embeddings
- **SQL Database**: SQLite for structured data storage and chat history
- **AI Models**: Google Gemini for text processing and image analysis
- **Document Processing**: Unstructured library for PDF parsing and chunking
- **API**: FastAPI server with RESTful endpoints

### Frontend
- **React Application**: Modern React 18+ with hooks andfunctional components
- **Real-time UI**: Interactive chat interface with document management
- **File Upload**: Drag-and-drop PDF upload with progress tracking
- **Responsive Design**: Clean, modern interface with CSS styling

## Prerequisites

### Backend
- Python 3.8+
- Google AI API key (for Gemini models)
- Required Python packages (see requirements below)

### Frontend
- Node.js 16+
- npm or yarn package manager

## Installation

### Backend Setup

1. **Clone the repository**:
```bash
git clone https://github.com/pola-k/QuickResearch.git
cd QuickResearch
```

2. **Set up environment variables**:
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
VECTOR_DB_PATH=./vector_db
CHAT_DB_PATH=./chat_db/chat.db
DATA_PATH=./data
ID_KEY=doc_id
FILE_KEY=file_path
```

### Frontend Setup

1. **Navigate to the frontend directory**:
```bash
cd quickResearch
```

2. **Install Node.js dependencies**:
```bash
npm install
```

3. **Install required React packages**:
```bash
npm install axios
npm install react-markdown
```

## Required Dependencies

### Backend Dependencies
```txt
fastapi
uvicorn
langchain
langchain-community
langchain-google-genai
langchain-core
google-generativeai
chromadb
unstructured[pdf]
python-multipart
python-dotenv
pillow
sqlite3
```

## Quick Start

### Start the Backend Server

1. **Run the FastAPI server**:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### Start the Frontend Application

1. **In a new terminal, navigate to the frontend directory**:
```bash
cd quickResearch
```

2. **Start the React development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Using the Application

1. **Open your browser** and navigate to `http://localhost:5173`
2. **Upload PDF documents** using the drag-and-drop interface
3. **Select sources** from your uploaded documents
4. **Start chatting** with your documents using natural language queries

## API Endpoints

### Document Management

#### Upload Document
```http
POST /uploadFile
Content-Type: multipart/form-data
```
Upload a PDF file for processing and analysis.

#### Get Uploaded Files
```http
GET /getUploadedFiles
```
Returns a list of all uploaded documents.

#### Delete Document
```http
DELETE /deleteUploadedFile?filename=document.pdf
```
Removes a document and all associated data from the system.

### Conversation

#### Query Documents
```http
GET /conversation?query=your_question&sources=file1.pdf&sources=file2.pdf
```
Ask questions about your uploaded documents.

#### Get Chat History
```http
GET /getMessages
```
Retrieve all previous conversations.

## Usage Examples

### Web Interface Usage

1. **Document Upload**: 
   - Click the upload area or drag and drop PDF files
   - Wait for processing completion (indicated by progress loader)
   - View uploaded documents in the Sources panel

2. **Source Selection**:
   - Check/uncheck documents in the Sources panel
   - Selected sources will be used for querying

3. **Conversational Querying**:
   - Type your question in the chat input
   - Press Enter or click Send
   - View AI responses based on your selected documents

## Document Processing Pipeline

1. **PDF Parsing**: Uses `unstructured` library to extract content with high-resolution strategy
2. **Content Categorization**: Separates text, tables, and images
3. **AI Summarization**: Generates searchable summaries using Gemini models
4. **Vector Embedding**: Creates semantic embeddings for efficient search
5. **Database Storage**: Stores original content and metadata in SQLite

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `VECTOR_DB_PATH` | Path to vector database | `./vector_db` |
| `CHAT_DB_PATH` | Path to chat database | `./chat.db` |
| `DATA_PATH` | Path to uploaded files | `./data` |
| `ID_KEY` | Document ID key | `doc_id` |
| `FILE_KEY` | File path key | `file_path` |

### Chunking Strategy

The system uses intelligent chunking with the following parameters:
- **Max characters per chunk**: 12,000
- **Combine under**: 1,000 characters
- **New chunk after**: 8,000 characters
- **Overlap**: 200 characters

## Advanced Features

### Frontend Features

- **Real-time Chat Interface**: Interactive conversation with your documents
- **Document Management**: Upload, view, and delete PDF files with visual feedback
- **Source Selection**: Choose specific documents for targeted queries
- **Persistent State**: Chat history and document titles saved locally
- **Responsive Design**: Works on desktop and mobile devices
- **Loading States**: Visual feedback during file processing and query execution
- **Notification System**: Success and error messages for user actions

### Backend Features

### Multimodal Content Processing

- **Text Chunks**: Summarized for semantic search while preserving original content
- **Tables**: HTML structure maintained with intelligent summarization
- **Images**: Visual analysis with contextual descriptions

### Intelligent Retrieval

The system uses a balanced approach to content retrieval:
- Up to 8 text chunks (highest relevance)
- Up to 2 tables (structured data)
- Up to 5 images (visual content)

### Context-Aware Responses

All AI responses are generated with full document context, ensuring accurate and relevant answers based solely on the uploaded content.

## File Structure

```
QuickResearch/
├── server.py                    # FastAPI server and main endpoints
├── llm.py                      # AI model configuration
├── populateVectorDB.py         # Document processing pipeline
├── database_utils.py           # Database operations
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── data/                       # Uploaded PDF files
├── vector_db/                  # Vector database storage
├── chat_db/                    # SQLite database
└── quickResearch/              # Frontend React application
    ├── src/
    │   ├── App.jsx             # Main React component
    │   ├── App.css             # Global styles
    │   ├── Components/
    │   │   ├── Header/         # Header component
    │   │   ├── Sources/        # Document sources panel
    │   │   ├── Chat/           # Chat interface
    │   │   ├── Help Modal/     # Help modal component
    │   │   ├── Account Modal/  # Account modal component
    │   │   ├── Loader/         # Loading component
    │   │   └── Notification/   # Notification component
    │   └── main.jsx            # React entry point
    ├── package.json            # Node.js dependencies
    └── vite.config.js          # Vite configuration
```

## Troubleshooting

### Common Issues

#### Backend Issues
1. **Google API Key Error**: Ensure your API key is valid and has access to Gemini models
2. **Memory Issues**: Large PDFs may require increased memory allocation
3. **Processing Timeout**: Complex documents may take longer to process
4. **Port Conflicts**: Ensure port 8000 is available for the FastAPI server

#### Frontend Issues
1. **CORS Errors**: Make sure the backend server is running on the correct port
2. **File Upload Failures**: Check file size limits and network connectivity
3. **UI Not Loading**: Ensure all dependencies are installed with `npm install`
4. **Port Conflicts**: Default frontend port is 5173, ensure it's available

### Development Tips

1. **Hot Reload**: Both backend (with `--reload`) and frontend (with Vite) support hot reloading
2. **Network Issues**: Check if both servers are running and accessible
3. **File Permissions**: Ensure the application has write permissions for data directories

## Acknowledgments

- Built with [LangChain](https://langchain.com/) for document processing
- Uses [Google Gemini](https://ai.google.dev/) for AI capabilities
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Document parsing by [Unstructured](https://unstructured.io/)

---

**Note**: This project requires a Google AI API key for full functionality. Make sure to set up your environment variables properly before running the application.
