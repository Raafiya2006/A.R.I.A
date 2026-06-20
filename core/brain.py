import ollama

def think(user_input, context=""):
    prompt = f"""You are ARIA — Agentic Reasoning and Intelligence Assistant. 
You are a personal AI assistant running locally on the user's laptop.
Be concise, helpful, and conversational. Keep responses short — you are speaking out loud.
{f'Context: {context}' if context else ''}

User: {user_input}
ARIA:"""
    
    response = ollama.chat(model='phi3', messages=[
        {'role': 'user', 'content': prompt}
    ])
    return response['message']['content'].strip()