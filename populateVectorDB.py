from langchain.schema.document import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import uuid
from unstructured.partition.pdf import partition_pdf
import base64
import io
from PIL import Image
from llm import CHAT_MODEL, IMAGE_MODEL
import os
import warnings
from database_utils import add_documents_to_sqlite
from typing import List

warnings.filterwarnings("ignore")

ID_KEY = os.getenv("ID_KEY")
FILE_KEY = os.getenv("FILE_KEY")
CHAT_DB_PATH = os.getenv("CHAT_DB_PATH")

TEXT_SUMMARIZATION_PROMPT_TEMPLATE = """
You are a research assistant creating searchable summaries of academic content.
You are analyzing content from an academic paper with the following context:

DOCUMENT CONTEXT: {document_context}

Now, create a concise summary of this specific text chunk that will be used for semantic search:

TEXT CHUNK: {element}

Provide a summary that:
1. Captures the key concepts and findings
2. Maintains technical accuracy
3. Is optimized for search retrieval
4. References the broader document context when relevant

Respond only with the summary, no additional comments.
Return the summary in plain text without markdown elements.
"""

TABLE_SUMMARIZATION_PROMPT_TEMPLATE = """
You are a research assistant creating searchable summaries of tables from academic papers.
You are analyzing a table from an academic paper with the following context:

DOCUMENT CONTEXT: {document_context}

Now, create a concise summary of this table that will be used for semantic search:

TABLE: {element}

Provide a summary that:
1. Describes what the table shows (variables, measurements, comparisons)
2. Highlights key findings or patterns in the data
3. Mentions the context within the broader research
4. Is optimized for search retrieval

Respond only with the summary, no additional comments.
Return the summary in plain text without markdown elements.
"""

IMAGE_SUMMARIZATION_PROMPT_TEMPLATE = """
You are a research assistant analyzing images from academic papers.
You are analyzing an image from an academic paper with the following context:

DOCUMENT CONTEXT: {document_context}

Describe this image in detail, focusing on:
1. What type of figure/image it is (graph, diagram, photograph, etc.)
2. Key visual elements and their relationships
3. Any data, trends, or patterns shown
4. How it relates to the research context
5. Any text, labels, or annotations visible

Provide a comprehensive description that will be useful for search and understanding.
Respond only with the description, no additional comments.
Return the description in plain text without markdown elements.
"""

TEXT_SUMMARIZATION_PROMPT = ChatPromptTemplate.from_template(TEXT_SUMMARIZATION_PROMPT_TEMPLATE)
TABLE_SUMMARIZATION_PROMPT = ChatPromptTemplate.from_template(TABLE_SUMMARIZATION_PROMPT_TEMPLATE)

TEXT_SUMMARIZATION_CHAIN = {"element": lambda x: x["element"], "document_context": lambda x: x["document_context"]} | TEXT_SUMMARIZATION_PROMPT | CHAT_MODEL | StrOutputParser()
TABLE_SUMMARIZATION_CHAIN = {"element": lambda x: x["element"], "document_context": lambda x: x["document_context"]} | TABLE_SUMMARIZATION_PROMPT | CHAT_MODEL | StrOutputParser()

def extract_document_context(chunks) -> str:
    context_parts = []
    
    text_chunks = [chunk for chunk in chunks if "CompositeElement" in str(type(chunk))][:3]
    
    for chunk in text_chunks:
        if hasattr(chunk, 'text'):
            context_parts.append(chunk.text)
    
    document_context = " ".join(context_parts)
    
    if len(document_context) > 5000:
        document_context = document_context[:5000] + "..."
    
    return document_context

def process_images_with_context(images: List[str], document_context: str) -> List[str]:
    image_summaries = []
    
    for i, image_b64 in enumerate(images):
        try:
            image_data = base64.b64decode(image_b64)
            image_pil = Image.open(io.BytesIO(image_data))
            
            contextual_prompt = IMAGE_SUMMARIZATION_PROMPT_TEMPLATE.format(
                document_context=document_context
            )
            
            response = IMAGE_MODEL.generate_content([contextual_prompt, image_pil])
            summary = response.text.strip() if response.text else ""
            
            if not summary:
                print(f"Empty summary for image {i}, using fallback.")
                summary = f"[Image {i+1} from academic paper - content could not be analyzed]"
                
            image_summaries.append(summary)
            
        except Exception as e:
            print(f"Error processing image {i}: {e}")
            image_summaries.append(f"[Image {i+1} could not be processed: {str(e)}]")
    
    return image_summaries

def populateVectorDB(file_location: str, RETRIEVER):
    try:
        chunks = partition_pdf(
            filename=file_location,
            infer_table_structure=True,
            strategy="hi_res",
            extract_image_block_types=["Image", "FigureCaption"],
            extract_image_block_to_payload=True,
            chunking_strategy="by_title",
            max_characters=12000, 
            combine_text_under_n_chars=1000,  
            new_after_n_chars=8000,
            overlap=200, 
            include_page_breaks=True
        )
        print(f"✅ PDF Chunking Complete - {len(chunks)} chunks extracted")
    except Exception as e:
        print(f"❌ Error during PDF chunking: {e}")
        return

    document_context = extract_document_context(chunks)
    print(f"✅ Document context extracted: {len(document_context)} characters")

    tables = []
    texts = []
    images = []
    
    for chunk in chunks:
        chunk_type = str(type(chunk))
        
        if "Table" in chunk_type:
            tables.append(chunk)
        elif "CompositeElement" in chunk_type:
            texts.append(chunk)
            sub_elements = getattr(chunk.metadata, "orig_elements", [])
            for el in sub_elements:
                el_type = str(type(el))
                if "Table" in el_type:
                    tables.append(el)
                elif "Image" in el_type:
                    image_b64 = getattr(el.metadata, "image_base64", None)
                    if image_b64:
                        images.append(image_b64)
        elif "Image" in chunk_type:
            image_b64 = getattr(chunk.metadata, "image_base64", None)
            if image_b64:
                images.append(image_b64)

    print(f"Content categorized:")
    print(f"Text chunks: {len(texts)}")
    print(f"Tables: {len(tables)}")
    print(f"Images: {len(images)}")

    if texts:
        try:
            print("🔄 Processing text chunks...")
            
            text_inputs = [
                {"element": chunk.text if hasattr(chunk, 'text') else str(chunk), 
                 "document_context": document_context}
                for chunk in texts
            ]
            
            text_summaries = TEXT_SUMMARIZATION_CHAIN.batch(text_inputs, {"max_concurrency": 3})
            print("✅ Text summarization complete")

            text_docs = []
            doc_ids = []
            original_docs = []
            
            for i, chunk in enumerate(texts):
                summary = text_summaries[i].strip() if i < len(text_summaries) else ""
                if not summary:
                    print(f"Empty summary for text chunk {i}")
                    summary = (chunk.text if hasattr(chunk, 'text') else str(chunk))[:1000]

                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                
                text_docs.append(Document(
                    page_content=summary, 
                    metadata={ID_KEY: doc_id, FILE_KEY: file_location, "Type": "TEXT"}
                ))
                
                original_content = chunk.text if hasattr(chunk, 'text') else str(chunk)
                original_docs.append(Document(
                    page_content=original_content, 
                    metadata={ID_KEY: doc_id, FILE_KEY: file_location, "Type": "TEXT", "filename": file_location}
                ))

            RETRIEVER.vectorstore.add_documents(text_docs)
            add_documents_to_sqlite(CHAT_DB_PATH, doc_ids, original_docs)
            print(f"✅ Added {len(text_docs)} text documents to stores")
            
        except Exception as e:
            print(f"Error processing text chunks: {e}")

    if tables:
        try:
            print("🔄 Processing tables...")
            
            table_html_list = []
            for table in tables:
                if hasattr(table.metadata, 'text_as_html'):
                    table_html_list.append(table.metadata.text_as_html)
                elif hasattr(table, 'text_as_html'):
                    table_html_list.append(table.text_as_html)
                elif hasattr(table, 'text'):
                    table_html_list.append(table.text)
                else:
                    table_html_list.append(str(table))
            
            table_inputs = [
                {"element": html_content, "document_context": document_context}
                for html_content in table_html_list
            ]
            
            table_summaries = TABLE_SUMMARIZATION_CHAIN.batch(table_inputs, {"max_concurrency": 3})
            print("✅ Table summarization complete")

            table_docs = []
            table_ids = []
            original_table_docs = []
            
            for i, table in enumerate(tables):
                summary = table_summaries[i].strip() if i < len(table_summaries) else ""
                if not summary:
                    print(f"Empty summary for table {i}")
                    summary = table_html_list[i][:1000] if i < len(table_html_list) else "[Missing Table]"

                table_id = str(uuid.uuid4())
                table_ids.append(table_id)
                
                table_docs.append(Document(
                    page_content=summary, 
                    metadata={ID_KEY: table_id, FILE_KEY: file_location, "Type": "TABLE"}
                ))
                
                original_html = table_html_list[i] if i < len(table_html_list) else "[Missing Table]"
                original_table_docs.append(Document(
                    page_content=original_html, 
                    metadata={
                        ID_KEY: table_id, 
                        FILE_KEY: file_location, 
                        "Type": "TABLE", 
                        "text_as_html": original_html,
                        "filename": file_location
                    }
                ))

            RETRIEVER.vectorstore.add_documents(table_docs)
            add_documents_to_sqlite(CHAT_DB_PATH, table_ids, original_table_docs)
            print(f"✅ Added {len(table_docs)} table documents to stores")
            
        except Exception as e:
            print(f"❌ Error processing tables: {e}")

    if images:
        try:
            print("🔄 Processing images with context...")
            
            image_summaries = process_images_with_context(images, document_context)
            print("✅ Image analysis complete")

            image_docs = []
            img_ids = []
            original_image_docs = []
            
            for i, (image_b64, summary) in enumerate(zip(images, image_summaries)):
                img_id = str(uuid.uuid4())
                img_ids.append(img_id)
                
                image_docs.append(Document(
                    page_content=summary, 
                    metadata={ID_KEY: img_id, FILE_KEY: file_location, "Type": "IMAGE"}
                ))
                
                original_image_docs.append(Document(
                    page_content=image_b64, 
                    metadata={
                        ID_KEY: img_id, 
                        FILE_KEY: file_location, 
                        "Type": "IMAGE",
                        "filename": file_location,
                        "image_summary": summary
                    }
                ))

            RETRIEVER.vectorstore.add_documents(image_docs)
            add_documents_to_sqlite(CHAT_DB_PATH, img_ids, original_image_docs)
            print(f"✅ Added {len(image_docs)} image documents to stores")
            
        except Exception as e:
            print(f"Error processing images: {e}")

    print("Document processing complete!")
    print(f"Summary:")
    print(f"Text documents: {len(texts)}")
    print(f"Table documents: {len(tables)}")  
    print(f"Image documents: {len(images)}")
    print(f"File: {file_location}")