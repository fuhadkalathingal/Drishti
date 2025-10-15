import json
import os
from collections import defaultdict, Counter
from corpus_data import corpus

CACHE_FILE = "user_cache.json"

# ---------- Trie Implementation ----------
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0  # frequency for ranking suggestions

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, freq=1):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.freq += freq

    def suggest(self, prefix, max_suggestions=5):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        suggestions = []

        def dfs(n, path):
            if len(suggestions) >= max_suggestions:
                return
            if n.is_end:
                suggestions.append(("".join(path), n.freq))
            for c, child in n.children.items():
                dfs(child, path + [c])

        dfs(node, list(prefix))
        # Sort by frequency descending
        suggestions.sort(key=lambda x: -x[1])
        return [word for word, _ in suggestions[:max_suggestions]]

# ---------- Load user cache ----------
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        raw = json.load(f)

    user_cache = defaultdict(Counter)
    for k, v in raw.items():
        key_tuple = tuple(k.split("|")) if "|" in k else k
        user_cache[key_tuple] = Counter(v)

else:
    user_cache = defaultdict(Counter)

global_ngrams = defaultdict(Counter)
trie = Trie()

for sentence in corpus:
    words = sentence.lower().split()
    # Insert words in trie for prefix suggestions
    for w in words:
        trie.insert(w)
    # Build trigram model
    for i in range(len(words)-2):
        context = tuple(words[i:i+2])
        next_word = words[i+2]
        global_ngrams[context][next_word] += 1

# ---------- Get suggestions ----------
def get_suggestions(prefix_or_context, user_cache, global_ngrams, top_n=5, is_prefix=True):
    """
    If is_prefix=True: prefix string -> word suggestions
    If is_prefix=False: tuple of words -> next-word suggestions
    """
    suggestions = Counter()

    if is_prefix:
        # Trie-based prefix completion
        for word in trie.suggest(prefix_or_context, max_suggestions=top_n):
            # User cache boosts frequency
            user_freq = user_cache.get(prefix_or_context, {}).get(word, 0)
            suggestions[word] = suggestions.get(word, 0) + user_freq + 1
    else:
        context = prefix_or_context
        if context in global_ngrams:
            suggestions.update(global_ngrams[context])
        if context in user_cache:
            for w, c in user_cache[context].items():
                suggestions[w] += c  # Boost with user-specific frequency

    # Return top N suggestions
    return [w for w, _ in suggestions.most_common(top_n)]

# Save user cache
def save_user_cache():
    """Save user cache safely to JSON file."""
    # Convert tuple keys to pipe-separated strings for JSON safety
    serializable_cache = {
        "|".join(k) if isinstance(k, tuple) else k: dict(v)
        for k, v in user_cache.items()
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(serializable_cache, f, indent=2)

# ---------- Update user cache ----------
def update_user_cache(context, next_word):
    user_cache[context][next_word] += 1
    save_user_cache()

def suggest(user_input, user_cache=None, global_ngrams=None):
    if user_cache is None:
        user_cache = globals().get("user_cache")
    if global_ngrams is None:
        global_ngrams = globals().get("global_ngrams")

    """
    Generate suggestions based on current input.
    Uses both prefix (current word) and context (previous words) logic.
    """

    words = user_input.strip().split()
    if not words:
        return [], []

    # 1️⃣ PREFIX suggestion (current word completion)
    prefix_suggestions = []
    if not user_input.endswith(" "):
        current_prefix = words[-1]
        prefix_suggestions = get_suggestions(
            current_prefix,
            user_cache,
            global_ngrams,
            top_n=4,
            is_prefix=True
        )


    # 2️⃣ CONTEXT suggestion (next word prediction)
    context_suggestions = []
    if len(words) > 1 and user_input.endswith(" "):
        context = tuple(words[-2:])
        context_suggestions = get_suggestions(
            context,
            user_cache,
            global_ngrams,
            top_n=4,
            is_prefix=False
        )

    return prefix_suggestions, context_suggestions

if __name__ == '__main__':
    user_input = "what is you"
    prefix_suggestions, context_suggestions = suggest(user_input)
    print(f"prefix: {prefix_suggestions}")
    print(f"context: {context_suggestions}")
