import sqlite3
import pickle
import os
from typing import List, Optional
from langchain_core.documents import Document

def init_sqlite_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        

        cursor.execute("""CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_text TEXT,
                role TEXT
            )""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS Documents (
                id TEXT PRIMARY KEY,
                content TEXT,
                filename TEXT,
                type TEXT,
                metadata TEXT)""")
        
        conn.commit()

def add_documents_to_sqlite(db_path: str, doc_ids: List[str], documents: List[Document]):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for doc_id, document in zip(doc_ids, documents):
            filename = document.metadata.get("filename", "")
            doc_type = document.metadata.get("Type", "")
            metadata_str = pickle.dumps(document.metadata).decode('latin-1')
            
            cursor.execute("""INSERT OR REPLACE INTO Documents (id, content, filename, type, metadata) VALUES (?, ?, ?, ?, ?)""", (doc_id, document.page_content, filename, doc_type, metadata_str))
        
        conn.commit()

def get_documents_from_sqlite(db_path: str, doc_ids: List[str]) -> List[Optional[Document]]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(doc_ids))
        cursor.execute(f"SELECT id, content, filename, type, metadata FROM Documents WHERE id IN ({placeholders})", doc_ids)
        
        results = cursor.fetchall()
        
        doc_map = {}
        for row in results:
            doc_id, content, filename, doc_type, metadata_str = row
            try:
                metadata = pickle.loads(metadata_str.encode('latin-1')) if metadata_str else {}
            except:
                metadata = {"filename": filename, "Type": doc_type}
            
            doc_map[doc_id] = Document(page_content=content, metadata=metadata)

        return [doc_map.get(doc_id) for doc_id in doc_ids]

def delete_documents_from_sqlite(db_path: str, doc_ids: List[str]):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(doc_ids))
        cursor.execute(f"DELETE FROM Documents WHERE id IN ({placeholders})", doc_ids)
        
        conn.commit()

def get_documents_by_filename(db_path: str, filename: str) -> List[str]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM Documents WHERE filename = ?", (filename,))
        return [row[0] for row in cursor.fetchall()]
    
def AddMessages(message, role):
    try:

        connection = sqlite3.connect(os.getenv("CHAT_DB_PATH"))
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Messages (message_text, role) VALUES (?, ?);", (message, role))

        connection.commit()

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        try:
            cursor.close()
            connection.close()
        except:
            pass
        return False


def getAllMessages():
    connection = sqlite3.connect(os.getenv("CHAT_DB_PATH"))
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Messages")
    messages = cursor.fetchall()

    cursor.close()
    connection.close()

    all_messages = []

    for id, text, role in messages:
        message_dict = {"id": id, "content": text, "role": role}
        all_messages.append(message_dict)

    return all_messages