import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration & RAG Setup Placeholder ---
# In a full deployment, this section would contain the RAG initialization 
# (loading documents, creating/loading FAISS index, setting up RetrievalQA chain).

# Since we cannot run the full RAG setup (LangChain, FAISS) in this environment, 
# we'll use a placeholder for the context and directly call the Gemini API.

# 1. SIMULATED RAG CONTEXT (The actual RAG system would dynamically retrieve this)
USER_CONTEXT = """
**CONTEXT: Capillary Technologies Documentation Summary**

1.  **Authentication:** API requests are authenticated using a Bearer token (`Authorization: Bearer <TOKEN>`). Tokens are generated via the `/auth/token` endpoint using a client ID and secret. Tokens expire every 60 minutes and must be refreshed.
2.  **Customer Management:** To create a customer, the required fields are: `mobile_number` (unique identifier), `country_code`, and `first_name`. Optional fields include `email`, `birth_date` (format YYYY-MM-DD), and `loyalty_program_id`.
3.  **Loyalty Campaigns:** Loyalty campaigns are created through the `/campaigns` endpoint. A basic campaign requires a `name`, `type` ('points' or 'discounts'), a `start_date`, and `end_date`. A reward rule must be defined, such as 'Earn 5 points for every $1 spent in the Retail category.'
"""

SYSTEM_PROMPT = """
You are an expert technical support chatbot for Capillary Technologies, specializing in APIs, customer management, and loyalty campaigns. 
Your goal is to answer questions concisely and accurately using ONLY the provided CONTEXT. 
If the answer is not found in the context, state clearly, "I cannot find the answer in the provided documentation." 
Always provide a brief, direct answer.
"""
# 2. SIMULATED API CALL (This replaces the qa_chain.invoke() in the original script)
async def get_rag_answer(query):
    """
    Simulates the RAG process by constructing a prompt with fixed context 
    and calling the Gemini API.
    
    In a real system, this function would handle:
    1. Retrieval: vectorstore.similarity_search(query, k=3)
    2. Prompt Construction: Combining retrieved chunks + query
    3. Generation: qa_chain.invoke({"query": query})
    """
    
    # 1. Prompt Construction
    full_prompt = f"""
        --- CONTEXT RETRIEVED FROM 1456 PAGES ---
        {USER_CONTEXT}
        --- END CONTEXT ---
        
        USER QUERY: {query}
    """
    
    # 2. API Payload (Using the standard non-streaming endpoint)
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        }
    }
    
    # 3. Fetch (using synchronous requests here for simplicity in Flask, 
    # but actual implementation should use an async library if concurrency is needed)
    import requests
    response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
    response.raise_for_status() # Raise error for bad responses (4xx or 5xx)
    result = response.json()
    
    candidate = result.get('candidates', [{}])[0]
    answer_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', "Error: Model did not return text.")
    
    # 4. SIMULATED SOURCE GATHERING (The RAG chain would return actual sources)
    sources = []
    lower_answer = answer_text.lower()
    if 'authentication' in lower_answer:
        sources.append('https://docs.capillary.tech/api/auth/token')
    if 'customer' in lower_answer:
        sources.append('https://docs.capillary.tech/api/customer/create')
    if 'campaign' in lower_answer:
        sources.append('https://docs.capillary.tech/api/campaigns/loyalty')
        
    return answer_text, sources


# --- Flask Routes ---
@app.route("/")
def index():
    """Renders the chat interface."""
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    """Endpoint for user queries. Calls the RAG system and returns the response."""
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not configured on the server."}), 500
        
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing query parameter."}), 400

    try:
        # Get answer from the RAG system (simulated or real)
        answer, sources = get_rag_answer(query)
        
        # Return the structured response
        return jsonify({
            "answer": answer,
            "sources": sources
        })

    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": f"Internal server error or API failure: {e}"}), 500

if __name__ == "__main__":
    print("Running Flask app. Access the chat at http://127.0.0.1:5000")
    app.run(debug=True)
