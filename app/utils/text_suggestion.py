import os
import json
from collections import defaultdict, Counter
from app.utils.corpus_data import corpus

CACHE_FILE = "cache/user_cache.json"


# ---------- Trie Node ----------
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0


# ---------- Trie Implementation ----------
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, freq=1):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.freq += freq

    def suggest(self, prefix, max_suggestions=10):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results = []

        def dfs(n, path):
            if len(results) >= max_suggestions * 2:
                return
            if n.is_end:
                results.append(("".join(path), n.freq))
            for c, child in n.children.items():
                dfs(child, path + [c])

        dfs(node, list(prefix))
        results.sort(key=lambda x: -x[1])
        return [w for w, _ in results[:max_suggestions]]


# ---------- User Cache ----------
def load_user_cache():
    os.makedirs("cache", exist_ok=True)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            raw = json.load(f)
        user_cache = defaultdict(Counter)
        for k, v in raw.items():
            key_tuple = tuple(k.split("|")) if "|" in k else k
            user_cache[key_tuple] = Counter(v)
        return user_cache
    else:
        return defaultdict(Counter)


def save_user_cache(user_cache):
    serializable = {
        "|".join(k) if isinstance(k, tuple) else k: dict(v)
        for k, v in user_cache.items()
    }
    with open(CACHE_FILE, "w") as f:
        json.dump(serializable, f, indent=2)


# ---------- Model Initialization ----------
user_cache = load_user_cache()
global_ngrams = defaultdict(Counter)
trie = Trie()

# Load corpus into Trie
for sentence in corpus:
    words = sentence.lower().split()
    for w in words:
        trie.insert(w)
    for i in range(len(words) - 2):
        context = tuple(words[i:i + 2])
        next_word = words[i + 2]
        global_ngrams[context][next_word] += 1


# ---------- Core Suggestion ----------
def get_suggestions(prefix_or_context, top_n=5, is_prefix=True):
    suggestions = Counter()

    if is_prefix:
        # 1️⃣ Get personalized suggestions (boosted)
        for key, value in user_cache.items():
            if isinstance(key, str):
                for w, c in value.items():
                    if w.startswith(prefix_or_context):
                        suggestions[w] += c * 10  # boost personal frequency

        # 2️⃣ Get global trie suggestions
        for w in trie.suggest(prefix_or_context, max_suggestions=top_n * 2):
            suggestions[w] += 1  # base freq

    else:
        context = prefix_or_context
        if context in global_ngrams:
            suggestions.update(global_ngrams[context])
        if context in user_cache:
            for w, c in user_cache[context].items():
                suggestions[w] += c * 10

    # 3️⃣ Sort by frequency, return top N
    ranked = [w for w, _ in suggestions.most_common(top_n)]
    return ranked


# ---------- Update User Cache ----------
def update_user_cache(context, next_word):
    """Update frequency when user selects or types a word."""
    user_cache[context][next_word] += 1
    save_user_cache(user_cache)


# ---------- Unified Suggestion ----------
def suggest(user_input):
    """
    Compatible with main_ui.
    Returns -> (prefix_suggestions, context_suggestions)
    """
    words = user_input.strip().lower().split()
    if not words:
        return [], []

    prefix_suggestions, context_suggestions = [], []

    # 1️⃣ Prefix completion (current partial word)
    if not user_input.endswith(" "):
        current_prefix = words[-1]
        prefix_suggestions = get_suggestions(current_prefix, top_n=4, is_prefix=True)

    # 2️⃣ Context prediction (next word after space)
    if len(words) > 1 and user_input.endswith(" "):
        context = tuple(words[-2:])
        context_suggestions = get_suggestions(context, top_n=2, is_prefix=False)

    return prefix_suggestions, context_suggestions


# ---------- Example Test ----------
if __name__ == "__main__":
    print("word suggestion")
