# chatbot_free.py — NOW WITH GEMINI 1.5 FLASH 🚀
import os
import json
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI  # ✅ Gemini Integration
from dotenv import load_dotenv

load_dotenv()

# --- Load scraped docs ---
with open("data/docs.json", "r", encoding="utf-8") as f:
    raw_docs = json.load(f)

documents = [
    Document(page_content=doc["content"], metadata={"source": doc["url"]})
    for doc in raw_docs
]

# --- Split text ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = text_splitter.split_documents(documents)

# --- Embeddings (FREE LOCAL) ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Vector Store ---
vectorstore = FAISS.from_documents(splits, embeddings)

# --- LLM: GEMINI 2.5 FLASH (FREE & FAST) ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",       # ✅ Super fast, great for docs
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1,
    max_tokens=512,
)

# --- QA Chain ---
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
    return_source_documents=True
)

# --- Chat Interface ---
def ask_question(query):
    print(f"\n💬 You: {query}")
    try:
        # Use .invoke() — modern LangChain
        result = qa_chain.invoke({"query": query})
        answer = result["result"]

        # Clean verbose output (if any)
        if "Answer:" in answer:
            answer = answer.split("Answer:")[-1].strip()
        if "Question:" in answer:
            answer = answer.split("Question:")[0].strip()

        print(f"🤖 Bot: {answer}")
        sources = [doc.metadata["source"] for doc in result["source_documents"]]
        print(f"📚 Source: {', '.join(sources[:2])}")  # Show top 2 sources

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Tip: Check your GEMINI_API_KEY in .env or internet connection.")

if __name__ == "__main__":
    print("🚀 CapillaryTech Chatbot (Powered by Gemini 1.5 Flash) Ready!")
    print("Ask me anything about Capillary APIs, customers, or campaigns.\n")

    # Example queries
    ask_question("How do I authenticate API requests?")
    ask_question("What fields are required to create a customer?")
    ask_question("How do I create a loyalty campaign?")

    # Uncomment for interactive mode
    while True:
        q = input("\n💬 You: ")
        if q.lower() in ["exit", "quit"]:
            break
        ask_question(q)