import os
import json
from collections import defaultdict
from groq import Groq
from dotenv import load_dotenv

# -----------------------------
# Load environment and initialize Groq
# -----------------------------
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# -----------------------------
# File paths
# -----------------------------
DATASET_FILE = "drishti_llm_training.jsonl"
HISTORY_FILE = "user_history.json"

# -----------------------------
# Load dataset from JSONL
# -----------------------------
def load_dataset():
    dataset = {}
    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    dataset[entry["keyword"].lower()] = entry["sentences"]
                except json.JSONDecodeError:
                    continue
    else:
        print(f"⚠️ Dataset file '{DATASET_FILE}' not found.")
    return dataset


# -----------------------------
# Load or auto-create usage history
# -----------------------------
def load_history():
    if not os.path.exists(HISTORY_FILE):
        print("🆕 No history file found. Creating new one...")
        history = defaultdict(int)
        save_history(history)
        return history
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            return defaultdict(int, data)
    except json.JSONDecodeError:
        print("⚠️ History file corrupt. Resetting new file.")
        history = defaultdict(int)
        save_history(history)
        return history


# -----------------------------
# Save history after updates
# -----------------------------
def save_history(history):
    # Convert defaultdict to normal dict before saving
    with open(HISTORY_FILE, "w") as f:
        json.dump(dict(history), f, indent=2)


# -----------------------------
# Groq fallback: generate new suggestions
# -----------------------------
def groq_generate_suggestions(keyword: str):
    prompt = f"""
You are an assistive text suggestion model that helps an ALS patient type faster
by predicting natural short sentences.

Requirements:
- Use the given text exactly or naturally within the sentences.
- Keep each suggestion short (max 8–10 words).
- Make them grammatically correct and human-like.
- Do not add explanations or numbering.
- Return exactly two suggestions separated by a "|" character.

Given text: "{keyword}"
Now generate two different complete sentence suggestions.
Format strictly as:
<sentence 1> | <sentence 2>
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    suggestion_text = response.choices[0].message.content.strip()
    return [s.strip() for s in suggestion_text.split("|") if s.strip()][:2]


# -----------------------------
# Suggest sentences with personalization
# -----------------------------
def suggest_sentences(keyword: str):
    dataset = load_dataset()
    history = load_history()
    keyword = keyword.lower().strip()

    print(f"\n🧠 Searching suggestions for '{keyword}'...")

    # Case 1: Keyword found in dataset
    if keyword in dataset:
        sentences = dataset[keyword]
        ranked = sorted(sentences, key=lambda s: history.get(s, 0), reverse=True)
        top_two = ranked[:2]

        print("💬 Personalized Suggestions (based on your usage):")
        for i, s in enumerate(top_two, 1):
            print(f"  {i}. {s}")

        # Update usage frequency
        for s in top_two:
            history[s] = history.get(s, 0) + 1
        save_history(history)
        return top_two

    # Case 2: Keyword not in dataset → generate via Groq
    print("⚡ Keyword not found in dataset, generating via Groq...")
    try:
        suggestions = groq_generate_suggestions(keyword)
        print("💡 Generated new suggestions:")
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s}")

        # Save to dataset and history
        if suggestions:
            with open(DATASET_FILE, "a") as f:
                json.dump({"keyword": keyword, "sentences": suggestions}, f)
                f.write("\n")
            for s in suggestions:
                history[s] = history.get(s, 0) + 1
            save_history(history)

        return suggestions
    except Exception as e:
        print(f"❌ Error generating suggestions: {e}")
        return []


# -----------------------------
# Interactive loop
# -----------------------------
if __name__ == "__main__":
    suggestions = suggest_sentences("help")
    print(suggestions)