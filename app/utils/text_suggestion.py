import os
import json
import threading
from collections import defaultdict, Counter
from groq import Groq
from dotenv import load_dotenv
from app.utils.corpus_data import corpus

# ------------------ CONFIG ------------------
CACHE_FILE = "cache/user_cache.json"
CORPUS_FILE = "cache/adaptive_corpus.json"
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ------------------ Thread-safe I/O ------------------
def load_json(path, default):
    os.makedirs("cache", exist_ok=True)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default
    return default


def save_json(path, data):
    os.makedirs("cache", exist_ok=True)

    def _save():
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("⚠️ Save error:", e)

    threading.Thread(target=_save, daemon=True).start()


def serialize_user_cache(user_cache):
    return {k if isinstance(k, str) else "|".join(k): dict(v) for k, v in user_cache.items()}


# ------------------ Trie ------------------
class TrieNode:
    __slots__ = ("children", "is_end", "freq")

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, freq=1):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True
        node.freq += freq

    def suggest(self, prefix, limit=10):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        results = []

        def dfs(n, path):
            if len(results) >= limit:
                return
            if n.is_end:
                results.append(("".join(path), n.freq))
            for c, child in n.children.items():
                dfs(child, path + [c])

        dfs(node, list(prefix))
        results.sort(key=lambda x: -x[1])
        # Ensure no duplicates, clean single words only
        return [w.strip() for w, _ in results if " " not in w][:limit]


# ------------------ Initialization ------------------
user_cache_raw = load_json(CACHE_FILE, {})
user_cache = defaultdict(Counter)
for k, v in user_cache_raw.items():
    user_cache[k] = Counter(v)
user_cache.setdefault("words", Counter())

adaptive_corpus = load_json(CORPUS_FILE, [])

trie = Trie()
combined_words = set()
for s in corpus:
    combined_words.update(s.lower().split())
combined_words.update(adaptive_corpus)
for w in combined_words:
    trie.insert(w)


# ------------------ Groq Fallback ------------------
def groq_suggest_words(prefix):
    """Generate up to 3 valid single words for prefix using Groq."""
    try:
        prompt = f"""
Suggest 3 distinct English words starting with "{prefix}".
Each should be one clean word only, no phrases or spaces.
Separate them with commas.
Example: time, tiny, tire
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        text = response.choices[0].message.content.strip()

        # Clean and filter strictly one-word items
        words = [w.strip().lower() for w in text.replace("|", ",").split(",") if w.strip()]
        words = [w.split()[0] for w in words if w.isalpha() or w.replace("-", "").isalpha()]
        return list(dict.fromkeys(words))[:3]
    except Exception as e:
        print("⚠️ Groq fallback error:", e)
        return []


# ------------------ Core Suggestion ------------------
def get_suggestions(prefix, top_n=4):
    """Return up to 4 distinct word suggestions for given prefix."""
    prefix = prefix.lower()
    suggestions = Counter()

    # 1️⃣ Personalized suggestions
    for w, c in user_cache["words"].items():
        if w.startswith(prefix):
            suggestions[w] += c * 10

    # 2️⃣ Trie-based completions
    for w in trie.suggest(prefix, limit=top_n * 3):
        if w.startswith(prefix):
            suggestions[w] += 1

    # Rank top results
    ranked = [w for w, _ in suggestions.most_common(top_n)]

    # 3️⃣ If less than 4 → async Groq fallback
    if len(ranked) < top_n:
        def async_fetch():
            new_words = groq_suggest_words(prefix)
            if new_words:
                for w in new_words:
                    if w not in adaptive_corpus:
                        adaptive_corpus.append(w)
                        trie.insert(w)
                save_json(CORPUS_FILE, adaptive_corpus)

        threading.Thread(target=async_fetch, daemon=True).start()

    # 4️⃣ Ensure exactly 4 distinct, valid single-word suggestions
    clean_ranked = [w for w in ranked if w and " " not in w][:top_n]
    while len(clean_ranked) < top_n:
        clean_ranked.append("")  # Fill empty slots for UI

    return clean_ranked[:top_n]


# ------------------ Update User Cache ------------------
def update_user_cache(context_or_word, next_word=None):
    """Update personalized word frequency safely."""
    try:
        if next_word:
            key = "|".join(context_or_word) if isinstance(context_or_word, (list, tuple)) else str(context_or_word)
            user_cache[key][next_word] += 1
            user_cache["words"][next_word] += 1
        else:
            word = context_or_word
            user_cache["words"][word] += 1

        word_to_add = next_word or context_or_word
        if word_to_add not in adaptive_corpus:
            adaptive_corpus.append(word_to_add)
            trie.insert(word_to_add)
            save_json(CORPUS_FILE, adaptive_corpus)

        save_json(CACHE_FILE, serialize_user_cache(user_cache))
    except Exception as e:
        print("⚠️ update_user_cache error:", e)


# ------------------ Unified Suggest ------------------
def suggest(user_input):
    """Returns -> (prefix_suggestions, []) — stops on space."""
    if not user_input or not user_input.strip():
        return ["", "", "", ""], []

    if user_input.endswith(" "):
        return ["", "", "", ""], []

    prefix = user_input.split()[-1].lower()
    prefix_suggestions = get_suggestions(prefix, top_n=4)
    return prefix_suggestions, []


# ------------------ Quick Test ------------------
if __name__ == "__main__":
    print("word suggestion")
