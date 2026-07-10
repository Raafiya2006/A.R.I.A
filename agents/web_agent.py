import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

import re
import ollama

def make_it_human(raw, question):
    """Make ARIA sound like a friend, not a robot"""
    try:
        response = ollama.chat(model='phi3', messages=[
            {
                'role': 'system',
                'content': """You are ARIA, Raafiya's best friend and assistant. 
Answer like a smart friend texting — casual, short, to the point.
MAX 2 sentences. No bullet points. No formal language.
Don't say "according to" or "based on". Just say it naturally.
Don't repeat yourself. Sound like you actually know this."""
            },
            {
                'role': 'user',
                'content': f"Question: {question}\nFacts: {raw[:400]}\n\nAnswer casually in max 2 sentences:"
            }
        ], options={'num_predict': 80, 'temperature': 0.5})

        result = response['message']['content'].strip()

        # Kill bad patterns
        bad = ['according to', 'based on', 'i apologize', 'as an ai',
               'developed by', 'i cannot', 'i am unable', 'it is worth noting',
               'it should be noted', 'please note']
        for b in bad:
            if b in result.lower():
                idx = result.lower().index(b)
                result = result[:idx].strip()

        sentences = re.split(r'(?<=[.!?])\s', result)
        result = ' '.join(sentences[:2]).strip()

        if not result or len(result) < 5:
            return raw[:150]
        return result
    except:
        # Fallback — just trim raw text
        sentences = re.split(r'(?<=[.!?])\s+', raw.replace('\n', ' '))
        return ' '.join(sentences[:2])[:200]

def clean_text(raw, max_sentences=2, max_chars=250):
    raw = raw.replace('\n', ' ').strip()
    # Remove duplicate sentences
    sentences = re.split(r'(?<=[.!?])\s+', raw)
    seen = set()
    unique = []
    for s in sentences:
        s_clean = s.strip().lower()
        if s_clean not in seen and len(s_clean) > 10:
            seen.add(s_clean)
            unique.append(s.strip())
    clean = ' '.join(unique[:max_sentences]).strip()
    return clean[:max_chars] if clean else raw[:max_chars]

def get_news(topic="world news", max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(topic, max_results=max_results))
            if not results:
                results = list(ddgs.text(f"latest {topic}", max_results=3))
                if not results:
                    return "Nothing in the news right now on that."
                parts = [r.get('title', '') for r in results[:2]]
                raw = ". ".join(parts)
                return make_it_human(raw, f"what is the latest {topic}")

            parts = []
            for r in results[:3]:
                title = r.get('title', '')
                body = r.get('body', '')[:80]
                if title:
                    parts.append(f"{title}. {body}")

            raw = " ".join(parts)
            return make_it_human(raw, f"what is the latest {topic}")
    except Exception as e:
        return f"Couldn't get news: {e}"

def web_search(query, max_results=5):
    try:
        with DDGS() as ddgs:
            # Add "news" to make it more specific
            search_query = query + " news 2026"
            results = list(ddgs.text(search_query, max_results=max_results))

            if not results:
                news = list(ddgs.news(query, max_results=3))
                if news:
                    parts = [f"{r.get('title', '')}. {r.get('body', '')[:80]}" for r in news[:2]]
                    raw = " ".join(parts)
                    return make_it_human(raw, query)
                return f"Couldn't find anything on {query}."

            parts = []
            for r in results[:3]:
                body = r.get('body', '').strip()
                if body and len(body) > 20:
                    parts.append(body[:200])

            if not parts:
                titles = [r.get('title', '') for r in results[:3] if r.get('title')]
                raw = ". ".join(titles)
            else:
                raw = " ".join(parts)

            return make_it_human(raw, query)

    except Exception as e:
        return f"Search error: {e}"

def get_weather(city="Chennai"):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                f"weather {city} today temperature",
                max_results=3
            ))
            if results:
                raw = results[0].get('body', '')[:300]
                return make_it_human(raw, f"what is the weather in {city} today")
        return f"Can't get weather for {city} right now."
    except Exception as e:
        return f"Weather error: {e}"