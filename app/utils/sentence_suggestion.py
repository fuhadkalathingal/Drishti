import os
import json
import threading
import time
from collections import defaultdict
from groq import Groq
from dotenv import load_dotenv

# -----------------------------
# Environment & File Setup
# -----------------------------
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

DATASET_FILE = os.path.join(CACHE_DIR, "drishti_llm_training.jsonl")
HISTORY_FILE = os.path.join(CACHE_DIR, "user_history.json")

# -----------------------------
# Global Memory Cache
# -----------------------------
dataset_cache = {}
history_cache = defaultdict(int)
lock = threading.Lock()


# -----------------------------
# Data Preload
# -----------------------------
def preload_data():
    """Load dataset and history to memory once at startup."""
    global dataset_cache, history_cache
    start = time.time()

    # Load dataset
    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    key = entry["keyword"].lower().strip()
                    # Merge sentences uniquely
                    if key not in dataset_cache:
                        dataset_cache[key] = list(dict.fromkeys(entry["sentences"]))
                    else:
                        for s in entry["sentences"]:
                            if s not in dataset_cache[key]:
                                dataset_cache[key].append(s)
                except Exception:
                    continue

    # Load history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                history_cache.update(data)
        except Exception:
            pass
    else:
        save_history()

    print(f"✅ Loaded {len(dataset_cache)} keywords and {len(history_cache)} history entries in {round(time.time() - start, 2)}s.")


# -----------------------------
# Safe Async Save
# -----------------------------
def save_history():
    def _save():
        with lock:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(dict(history_cache), f, indent=2)
    threading.Thread(target=_save, daemon=True).start()


def save_dataset(keyword, suggestions):
    """Efficiently update the dataset file — distinct per keyword."""
    with lock:
        # ✅ Ensure dataset_cache stays clean (unique + merged)
        if keyword in dataset_cache:
            for s in suggestions:
                if s not in dataset_cache[keyword]:
                    dataset_cache[keyword].append(s)
        else:
            dataset_cache[keyword] = suggestions

        # Rebuild the JSONL file cleanly (deduplicated)
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            for k, v in dataset_cache.items():
                json.dump({"keyword": k, "sentences": v}, f)
                f.write("\n")


# -----------------------------
# Groq Sentence Generator
# -----------------------------
def groq_generate_suggestions(keyword):
    """Generate up to 3 simple ALS-friendly short sentences."""
    prompt = f"""
You are helping an ALS patient communicate faster.
Generate up to 3 short, simple sentences (3–6 words) using the word "{keyword}".
No punctuation, no numbering, no explanations.
Separate each with '|'.
Examples:
help → help me please | need your help | call nurse
water → need water | drink water | get some water
Now generate:
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        suggestion_text = response.choices[0].message.content.strip()
        suggestions = [s.strip() for s in suggestion_text.split("|") if s.strip()][:3]

        if suggestions:
            # Ensure unique + short
            unique_sents = list(dict.fromkeys(suggestions))
            dataset_cache[keyword] = unique_sents
            for s in unique_sents:
                history_cache[s] += 1
            save_dataset(keyword, unique_sents)
            save_history()

        return suggestions
    except Exception as e:
        print(f"⚠️ Groq generation failed: {e}")
        return []


# -----------------------------
# Local Search & Personalization
# -----------------------------
def local_suggestions(keyword):
    """Return up to 3 best personalized cached sentences."""
    keyword = keyword.lower().strip()
    if keyword in dataset_cache:
        sentences = dataset_cache[keyword]
        ranked = sorted(sentences, key=lambda s: history_cache.get(s, 0), reverse=True)
        for s in ranked[:3]:
            history_cache[s] += 1
        save_history()
        return ranked[:3]
    return None


# -----------------------------
# Main Suggestion Interface
# -----------------------------
def suggest_sentences(keyword):
    """
    Returns up to 3 short ALS-friendly sentences.
    - Uses cache first
    - Falls back to async Groq for unseen keywords
    - Deduplicates everything
    """
    keyword = keyword.lower().strip()
    if not keyword:
        return []

    local = local_suggestions(keyword)
    if local:
        return local

    # Async Groq fallback if unseen
    def background_update():
        new_suggs = groq_generate_suggestions(keyword)
        if new_suggs:
            print(f"🧠 Cached new distinct suggestions for '{keyword}': {new_suggs}")

    threading.Thread(target=background_update, daemon=True).start()
    return []


# -----------------------------
# Preload at Import
# -----------------------------
preload_data()


# -----------------------------
# Example Run
# -----------------------------
if __name__ == "__main__":
    print("Suggestions")
