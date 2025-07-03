import os
import dotenv
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import shutil
from llm import CHAT_MODEL
from populateVectorDB import populateVectorDB
from fastapi import Query
from typing import List
from database_utils import init_sqlite_db, get_documents_from_sqlite, delete_documents_from_sqlite, AddMessages, getAllMessages

dotenv.load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_DB_PATH")
CHAT_DB_PATH = os.getenv("CHAT_DB_PATH")
ID_KEY = os.getenv("ID_KEY")
FILE_KEY = os.getenv("FILE_KEY")
DATA_PATH = os.getenv("DATA_PATH")

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)

init_sqlite_db(CHAT_DB_PATH)

EMBEDDINGS = GoogleGenerativeAIEmbeddings(google_api_key=GOOGLE_API_KEY, model="models/embedding-001")
VECTOR_STORE = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=EMBEDDINGS)
RETRIEVER = VECTOR_STORE.as_retriever(search_kwargs={"k": 8})

app = FastAPI()
origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://localhost:5174"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/uploadFile")
async def uploadFile(file: Annotated[UploadFile, File()]):
    data_path = os.getenv("DATA_PATH")
    os.makedirs(data_path, exist_ok=True)
    file_location = os.path.join(data_path, file.filename)

    if not os.path.exists(file_location):
        try:
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            populateVectorDB(file_location, RETRIEVER)

            print(f"Saved file to {file_location}")
            return {"filename": file.filename, "message": "File saved successfully"}
        except Exception as e:
            print(f"Error saving file: {e}")
            if os.path.exists(file_location):
                os.remove(file_location)
            return {"filename": file.filename, "message": f"Error saving file: {file.filename}"}
    else:
        print(f"File {file_location} Already Exists.")
        return {"filename": file.filename, "message": "File Already Exists"}

@app.get("/getUploadedFiles")
def getUploadedFiles():
    uploaded_files = os.listdir(DATA_PATH)
    return {"uploaded_files": uploaded_files}

@app.delete("/deleteUploadedFile")
def deleteUploadedFile(filename: str):
    file_location = os.path.join(DATA_PATH, filename)

    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        collection = VECTOR_STORE._collection
        all_docs = collection.get(include=['metadatas', 'documents'])
        
        ids_to_delete = []
        docstore_keys_to_delete = []
        
        if all_docs['ids']:
            for i, metadata in enumerate(all_docs['metadatas']):
                if metadata and metadata.get(FILE_KEY) == file_location:
                    ids_to_delete.append(all_docs['ids'][i])
                    doc_id = metadata.get(ID_KEY)
                    if doc_id:
                        docstore_keys_to_delete.append(doc_id)
        
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            print(f"Deleted {len(ids_to_delete)} documents from vector store")
       
        if docstore_keys_to_delete:
            delete_documents_from_sqlite(CHAT_DB_PATH, docstore_keys_to_delete)
            print(f"Deleted {len(docstore_keys_to_delete)} documents from SQLite database")

        os.remove(file_location)
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.get("/getMessages")
def getMessages():
    return getAllMessages()

@app.get("/conversation")
def conversation(query: str = Query(...), sources: List[str] = Query(default=[])):
    AddMessages(query, "user")

    selected_files = []
    for source in sources:
        file_location = os.path.join(DATA_PATH, source)
        if os.path.exists(file_location):
            selected_files.append(file_location)
        else:
            raise HTTPException(status_code=404, detail=f"File {source} not found")

    if not selected_files:
        AddMessages("No Files Selected.", "bot")
        return {"response": "No Files Selected."}

    try:
        all_results = []
        for file in selected_files:
            try:
                matches = VECTOR_STORE.similarity_search_with_score(query=query,k=50,filter={FILE_KEY: file})
                all_results.extend(matches)
            except Exception as e:
                print(f"Error retrieving for {file}: {e}")
                continue

        if not all_results:
            AddMessages("No Relevant Documents Found.", "bot")
            return {"response": "No Relevant Documents Found."}

        all_results.sort(key=lambda x: x[1]) 

        texts, tables, images = [], [], []
        for doc, score in all_results:
            doc_type = doc.metadata.get("Type", "")
            if doc_type == "TEXT" and len(texts) < 8:
                texts.append((doc, score))
            elif doc_type == "TABLE" and len(tables) < 2:
                tables.append((doc, score))
            elif doc_type == "IMAGE" and len(images) < 5:
                images.append((doc, score))
            if len(texts) == 8 and len(tables) == 2 and len(images) == 5:
                break

        final_results = texts + tables + images

    except Exception as e:
        print(f"Error during retrieval: {e}")
        AddMessages("Retrieval failed.", "bot")
        return {"response": "Retrieval failed."}

    prompt_content = []
    system_instruction = SystemMessage(
    content="""You are a helpful research assistant. You will receive text, tables, and images extracted from academic papers.
            Use ONLY the provided content to answer the user's question.
            Do not make up anything or use outside knowledge.
            Provide a clear, well-structured, and accurate response based solely on the provided documents.
            You may use markdown for formatting (e.g., headings, bold text, bullet points).
            Always provide your answer in a logical, readable format.
            """)
    
    prompt_content.append(system_instruction)

    human_content = []

    try:
        for doc, score in final_results:
            doc_id = doc.metadata.get(ID_KEY)
            doc_type = doc.metadata.get("Type")
            file_path = doc.metadata.get(FILE_KEY)
            summary = doc.page_content

            print(f"Processing doc ID: {doc_id}, Type: {doc_type}, Score: {score}")
            try:
                original_elements = get_documents_from_sqlite(CHAT_DB_PATH, [doc_id])
                original_element = original_elements[0] if original_elements else None
            except Exception as e:
                print(f"Error fetching original for {doc_id}: {e}")
                original_element = None

            full_content = original_element.page_content if original_element else ""
            source_note = f"[From: {file_path}]"

            if doc_type == "TEXT":
                human_content.append({
                    "type": "text",
                    "text": f"{source_note}\nSummary: {summary}\nFull Text: {full_content}"
                })

            elif doc_type == "TABLE":
                table_html = original_element.metadata.get("text_as_html", full_content) if original_element else summary
                human_content.append({
                    "type": "text",
                    "text": f"{source_note}\nSummary: {summary}\nTable: {table_html}"
                })

            elif doc_type == "IMAGE":
                image_b64 = full_content if original_element else ""
                human_content.append({
                    "type": "text",
                    "text": f"{source_note}\nImage Summary: {summary}"
                })
                if image_b64:
                    human_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                    })

        human_content.append({"type": "text", "text": f"Question: {query}"})
        prompt_content.append(HumanMessage(content=human_content))

        response = CHAT_MODEL.invoke(prompt_content)
        AddMessages(response.content, "bot")
        return {"response": response.content}

    except Exception as e:
        print(f"Error constructing prompt or invoking model: {e}")
        error_message = "An error occurred while processing your request."
        AddMessages(error_message, "bot")
        raise HTTPException(status_code=500, detail=error_message)
