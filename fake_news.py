import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

sarvam_url = "https://api.sarvam.ai/v1/chat/completions"


def is_future_claim(text):
    current_year = datetime.now().year
    for year in range(current_year + 1, current_year + 10):
        if str(year) in text:
            return True
    return False  

def extract_keywords(text):
    stop_words = {"the", "is", "in", "on", "at", "a", "an", "and", "of", "to"}
    words = text.lower().split()
    keywords = [word for word in words if word not in stop_words]
    return " ".join(keywords[:6])

# 🔹 Fetch latest news
def get_latest_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            return None

        if data.get("totalResults", 0) == 0:
            return []

        articles = []
        for article in data["articles"]:
            title = article["title"]
            source = article["source"]["name"]
            link = article["url"]

            articles.append(f"{title} ({source})\n{link}")

        return articles

    except:
        return None

# 🔹 Analyze with Sarvam AI
def analyze_news(claim, evidence):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    evidence_text = "\n\n".join(evidence) if evidence else "No reliable news found."

    prompt = f"""
You are a professional fact-checking AI.

CLAIM:
{claim}

EVIDENCE:
{evidence_text}

Rules:
- If confirmed by multiple trusted sources → REAL
- If contradicted or false → FAKE
- If no or weak evidence → UNVERIFIED
- If event is in future → UNVERIFIED

IMPORTANT:
- If no evidence, keep confidence below 40%

Return STRICT format:

Classification:
Confidence:
Reason:
Key Entities:
Summary:
"""

    data = {
        "model": "sarvam-m",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(sarvam_url, headers=headers, json=data, timeout=20)
        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Sarvam API Error: {e}"

# 🔹 Terminal UI
def main():
    print("\n")
    print(" 🧠 AI LIVE FAKE NEWS DETECTOR ")
    print(" ⚡ Real-Time + Smart Verification System ")
    print("\n")

    while True:
        claim = input("📝 Enter news claim:\n> ")

        # 🔹 Future detection
        if is_future_claim(claim):
            print("\n⚠️ This claim refers to a future event.")
            print("📊 Result: UNVERIFIED (Event not occurred yet)\n")
            continue

        print("\n🔍 Extracting keywords...")
        keywords = extract_keywords(claim)
        print("🔑 Keywords:", keywords)

        print("\n🌐 Fetching latest news...")
        evidence = get_latest_news(keywords)

        # 🔹 Handle API failure
        if evidence is None:
            print("\n❌ News API failed. Proceeding with AI only...\n")
            evidence = []

        elif len(evidence) == 0:
            print("\n⚠️ No related news found.\n")

        else:
            print("\n📰 Recent News:\n")
            for i, news in enumerate(evidence, 1):
                print(f"{i}. {news}\n")

        print("🤖 Analyzing with AI...\n")
        result = analyze_news(claim, evidence)

        print("------------- 📊 Analysis -------------\n")
        print(result)
        print("\n--------------------------------------")

        again = input("\n🔁 Check another news? (yes/no): ").lower()
        if again != "yes":
            print("\n👋 Program stopped.")
            break

# 🔹 Run
if __name__ == "__main__":
    main()