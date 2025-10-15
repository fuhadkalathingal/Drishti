from google import genai
import time
import os

# -----------------------------
# CONFIG
# -----------------------------
os.environ["GOOGLE_API_KEY"] = "AIzaSyDDPFy86k8vd5Y_3UD3SU4cciIlQjUc2c8"
client = genai.Client()
MODEL = "gemini-2.5-flash"
MAX_SUGGESTIONS = 2

def fetch_gemini_suggestions(prompt, max_results=MAX_SUGGESTIONS):
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[{"parts": [{"text": prompt}]}],
            )
            # response.candidates is a list of Candidate objects
            suggestions = []
            for c in getattr(response, "candidates", []):
                # Each candidate has content -> list of Content objects
                for content_part in getattr(c, "content", []):
                    # content_part.text holds the text
                    suggestions.append(getattr(content_part, "text", "").strip())
            return suggestions[:max_results]
        except Exception as e:
            if "overloaded" in str(e).lower():
                print(f"Model overloaded, retrying ({attempt+1}/5)...")
                time.sleep(2)
            else:
                print("Error:", e)
                return []
    print("Failed to get suggestions after multiple attempts.")
    return []

# -----------------------------
# TERMINAL TEST
# -----------------------------
print("=== Gemini-2.5-flash Sentence Suggestion Test ===")
print("Type a partial sentence. Type 'exit' to quit.\n")

while True:
    user_input = input("Input: ").strip()
    if user_input.lower() == "exit":
        break
    if not user_input:
        continue
    prompt = f"Complete this sentence: '{user_input}'. Suggest {MAX_SUGGESTIONS} full sentences."
    suggestions = fetch_gemini_suggestions(prompt)
    if suggestions:
        for i, s in enumerate(suggestions, 1):
            print(f"{i}. {s}")
    else:
        print("No suggestions returned.")
    print("-" * 50)
