import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import chromadb
import datetime
import hashlib

client = chromadb.PersistentClient(path="C:\\Raafiya\\A.R.I.A\\chroma_db")
conversation_collection = client.get_or_create_collection("conversations")
facts_collection = client.get_or_create_collection("user_facts")

def save_conversation(user_input, aria_response):
    try:
        now = datetime.datetime.now()
        timestamp = now.isoformat()
        doc_id = hashlib.md5(f"{timestamp}{user_input}".encode()).hexdigest()
        conversation_collection.add(
            documents=[f"User: {user_input}\nARIA: {aria_response}"],
            metadatas=[{"timestamp": timestamp, "date": now.strftime("%Y-%m-%d"),
                       "time": now.strftime("%H:%M"), "user_input": user_input,
                       "aria_response": aria_response}],
            ids=[doc_id]
        )
    except Exception as e:
        print(f"Memory save error: {e}")

def search_memory(query, n=3):
    try:
        count = conversation_collection.count()
        if count == 0:
            return []
        results = conversation_collection.query(
            query_texts=[query],
            n_results=min(n, count)
        )
        if results and results["documents"] and results["documents"][0]:
            return results["documents"][0]
        return []
    except Exception as e:
        print(f"Memory search error: {e}")
        return []

def get_memory_context(user_input):
    try:
        if conversation_collection.count() == 0:
            return ""
        relevant = search_memory(user_input, n=3)
        if not relevant:
            return ""
        context = "Relevant past conversations:\n"
        for conv in relevant:
            context += f"- {conv}\n"
        return context
    except:
        return ""

def save_fact(key, value):
    try:
        facts_collection.upsert(
            documents=[value],
            metadatas=[{"key": key, "updated": datetime.datetime.now().isoformat()}],
            ids=[key]
        )
    except Exception as e:
        print(f"Fact save error: {e}")

def get_fact(key):
    try:
        result = facts_collection.get(ids=[key])
        if result and result["documents"]:
            return result["documents"][0]
        return None
    except:
        return None

def get_recent_conversations(n=5):
    try:
        results = conversation_collection.get(
            limit=n,
            include=["documents", "metadatas"]
        )
        if results and results["documents"]:
            return results["documents"]
        return []
    except Exception as e:
        return []