# optimized_chatbot.py — RAG for 1456 Pages with Gemini 2.5 Flash 🚀
import os
import json
import time
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# --- Configuration & Setup ---
load_dotenv()
# Define constants for better configuration management
CHUNK_SIZE = 700 
CHUNK_OVERLAP = 70
K_RETRIEVAL = 3 # Increased from 2 to 3 for better context coverage from a large docset
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_STORE_PATH = "faiss_index_1456_pages" # New: Save/Load the index

# --- Load & Pre-process Data ---
def load_and_split_documents(file_path="data/docs.json"):
    """Loads documents from JSON, converts to LangChain Document objects, and splits them."""
    print("⏳ Loading and parsing documents...")
    with open(file_path, "r", encoding="utf-8") as f:
        raw_docs = json.load(f)

    # Convert to Document objects
    documents = [
        Document(page_content=doc["content"], metadata={"source": doc["url"]})
        for doc in raw_docs
    ]

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP, 
        # Add common separators for better splitting logic
        separators=["\n\n", "\n", " ", ""] 
    )
    splits = text_splitter.split_documents(documents)
    print(f"✅ Loaded {len(documents)} source documents, resulting in {len(splits)} chunks.")
    return splits

# --- Vector Store (Optimized for Large Context) ---
def setup_vector_store(splits):
    """Sets up or loads the FAISS vector store."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    if os.path.exists(VECTOR_STORE_PATH):
        print(f"⏳ Loading existing FAISS index from '{VECTOR_STORE_PATH}'...")
        vectorstore = FAISS.load_local(
            folder_path=VECTOR_STORE_PATH, 
            embeddings=embeddings, 
            allow_dangerous_deserialization=True # Necessary for loading
        )
        print("✅ FAISS index loaded.")
    else:
        print("⏳ Creating new FAISS index (This may take a minute for 1456 pages)...")
        start_time = time.time()
        # Use from_documents for initial index creation
        vectorstore = FAISS.from_documents(splits, embeddings)
        # Save the index for future fast loads
        vectorstore.save_local(VECTOR_STORE_PATH)
        end_time = time.time()
        print(f"✅ FAISS index created and saved in {end_time - start_time:.2f} seconds.")

    return vectorstore

# --- Main QA Chain Setup ---
def setup_qa_chain(vectorstore):
    """Initializes the Gemini LLM and the RetrievalQA chain."""
    print("⏳ Setting up Gemini and QA chain...")
    
    # LLM: GEMINI 2.5 FLASH (Use environment variable for key)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,  # Keep low for factual Q/A
        max_tokens=1024,  # Increased output token limit for detailed answers
    )

    # QA Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity_score_threshold", # Optimization for relevance
            search_kwargs={"k": K_RETRIEVAL, "score_threshold": 0.75} # Use threshold
        ),
        return_source_documents=True,
        # Set chain_type="stuff" which is the default, but good to know
        chain_type="stuff"
    )
    print("✅ QA Chain ready.")
    return qa_chain

# --- Chat Interface (Refined) ---
def ask_question(qa_chain, query):
    """Processes a single question and prints the answer and sources."""
    print(f"\n💬 You: {query}")
    try:
        start_time = time.time()
        # Use .invoke() — modern LangChain
        result = qa_chain.invoke({"query": query})
        end_time = time.time()
        
        answer = result["result"]
        
        # Clean verbose output (no longer needed if prompt templates are good, but kept as safeguard)
        if answer.startswith("Answer:"):
            answer = answer.replace("Answer:", "", 1).strip()

        print(f"🤖 Bot (in {end_time - start_time:.2f}s): {answer}")
        
        # Display sources
        sources = [doc.metadata["source"] for doc in result["source_documents"]]
        unique_sources = list(set(sources)) # Only show unique URLs
        print(f"📚 Sources: {', '.join(unique_sources)}")

    except Exception as e:
        print(f"❌ Error during query: {e}")
        print("💡 Tip: Check your GEMINI_API_KEY, internet connection, or document format.")

if __name__ == "__main__":
    # 1. Load and Split Documents
    splits = load_and_split_documents()

    # 2. Setup Vector Store (Create or Load)
    vectorstore = setup_vector_store(splits)

    # 3. Setup QA Chain
    qa_chain = setup_qa_chain(vectorstore)

    print("\n\n🚀 RAG Chatbot (Powered by Gemini 2.5 Flash) Ready!")
    print("Ask me anything about your document set.")
    print("Type 'exit' or 'quit' to end.\n")

    # --- Interactive Mode ---
    while True:
        q = input("\n💬 You: ")
        if q.lower() in ["exit", "quit"]:
            break
        
        if not q.strip():
             continue
             
        ask_question(qa_chain, q)