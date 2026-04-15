import tweepy
from google import genai
import requests
import os
import time

# Anahtarlar
X_KEYS = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET")
}
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
NEWS_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    # En taze haberi alalım
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        if res.get("articles") and len(res["articles"]) > 0:
            article = res["articles"][0]
            return f"Haber: {article['title']}\nLink: {article['url']}"
    except:
        return None
    return None

def main():
    # 1. Gemini İstemcisi
    client_gemini = genai.Client(api_key=GEMINI_KEY)

    # 2. Haberi Al
    news_content = get_tech_news()
    if not news_content:
        print("Haber bulunamadı.")
        return

    # 3. Tweet Oluştur (Gemini 2.0-flash kullanıyoruz, çünkü o çalışıyor!)
    prompt = f"Aşağıdaki teknoloji haberini Türkçe yorumla ve etkileyici bir tweet oluştur. Linki ekle. Maksimum 270 karakter:\n{news_content}"
    
    try:
        response = client_gemini.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        tweet = response.text
    except Exception as e:
        print(f"Gemini hatası (Muhtemelen Kota): {e}")
        return

    # 4. X'te Paylaş
    try:
        client_x = tweepy.Client(**X_KEYS)
        client_x.create_tweet(text=tweet[:280])
        print(f"BAŞARILI! Paylaşılan tweet: {tweet[:50]}...")
    except Exception as e:
        print(f"X API Hatası: {e}")

if __name__ == "__main__":
    main()
