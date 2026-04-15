import tweepy
from google import genai # Yeni kütüphane
import requests
import os

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
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    res = requests.get(url).json()
    if res.get("articles"):
        article = res["articles"][0]
        return f"Haber: {article['title']}\nÖzet: {article['description']}\nLink: {article['url']}"
    return None

def main():
    # 1. Yeni Gemini İstemcisi
    client_gemini = genai.Client(api_key=GEMINI_KEY)

    # 2. Haberi Al
    news_content = get_tech_news()
    if not news_content: return

    # 3. Gemini 2.0 Kullanarak Tweet Oluştur (2026'nın standart modeli)
    prompt = f"Aşağıdaki haberi teknoloji meraklısı bir dille Türkçe yorumla ve X için kısa bir tweet oluştur. Linki ekle. Maksimum 270 karakter:\n{news_content}"
    
    response = client_gemini.models.generate_content(
        model='gemini-1.5-flash', # Güncel model ismi
        contents=prompt
    )
    tweet = response.text

    # 4. X'te Paylaş
    client_x = tweepy.Client(**X_KEYS)
    client_x.create_tweet(text=tweet[:280])
    print("İşlem Başarılı!")

if __name__ == "__main__":
    main()
