'''
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def suggest_sentences(string):
    content = f"""
    You help the user to type fast by giving appropriate suggestions.
    The user is a patient suffering from ALS who can move only his eyes.

    Given the words: "{string}", suggest 2 short sentences as suggestions which 
    contains the given words in the sentence
    Format them as: Reply 1 | Reply 2
    """
    suggeston_resp = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": content
            }
        ],

        model="llama-3.3-70b-versatile"

    )

    suggestion_text = suggeston_resp.choices[0].message.content.strip()
    suggestions = [s.strip() for s in suggestion_text.split('|') if s.strip()][:2]

    return suggestions

if __name__ == '__main__':
    suggestions = suggest_sentences("help")
    print(suggestions)
'''


import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def suggest_sentences(text: str):
    """
    Generate two short, natural sentence suggestions that include the given text.
    Intended for assistive typing systems (e.g., ALS users).
    """
    prompt = f"""
You are an assistive text suggestion model that helps an ALS patient type faster
by predicting natural short sentences.

Requirements:
- Use the given text exactly or naturally within the sentences.
- Keep each suggestion short (max ~8–10 words).
- Make them grammatically correct and human-like.
- Do not add explanations or numbering.
- Return exactly two suggestions separated by a "|" character.

Given text: "{text}"
Now generate two different complete sentence suggestions.
Format strictly as:
<sentence 1> | <sentence 2>
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    suggestion_text = response.choices[0].message.content.strip()
    suggestions = [s.strip() for s in suggestion_text.split("|") if s.strip()][:2]

    return suggestions


if __name__ == "__main__":
    suggestions = suggest_sentences("help")
    print(suggestions)
