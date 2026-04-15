import os
import requests
from atproto import Client # Bluesky kütüphanesi
from groq import Groq

# Anahtarlar
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        if res.get("articles"):
            article = res["articles"][0]
            return f"Haber: {article['title']}\nLink: {article['url']}"
    except:
        return None
    return None

def main():
    # 1. AI ve Bluesky İstemcileri
    client_groq = Groq(api_key=GROQ_API_KEY)
    client_bsky = Client()
    client_bsky.login(BSKY_HANDLE, BSKY_PASSWORD)

    # 2. Haberi Al
    news_content = get_tech_news()
    if not news_content:
        print("Haber bulunamadı.")
        return

    # 3. AI ile Post Oluştur (Llama 3.3)
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sen bir teknoloji editörüsün. Haberleri Bluesky için etkileyici postlara dönüştürürsün."},
                {"role": "user", "content": f"Şu haberi Türkçe yorumla, emojiler ekle ve linki sona koy:\n{news_content}"}
            ],
        )
        post_text = completion.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        print(f"AI Hatası: {e}")
        return

    # 4. Bluesky'da Paylaş
    try:
        # Bluesky'da tweet yerine 'post' denir
        client_bsky.send_post(text=post_text)
        print(f"Bluesky'da başarıyla paylaşıldı: {post_text[:50]}...")
    except Exception as e:
        print(f"Bluesky Paylaşım Hatası: {e}")

if __name__ == "__main__":
    main()
