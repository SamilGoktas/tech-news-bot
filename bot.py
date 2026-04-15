import tweepy
from google import genai
import requests
import os
import time

# Kimlik Bilgileri
X_KEYS = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET")
}
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
NEWS_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    # Haberleri çekiyoruz
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        if res.get("articles") and len(res["articles"]) > 0:
            article = res["articles"][0]
            return f"Haber: {article['title']}\nLink: {article['url']}"
    except Exception as e:
        print(f"Haber çekme hatası: {e}")
    return None

def main():
    # 1. Gemini İstemcisi
    client_gemini = genai.Client(api_key=GEMINI_KEY)

    # 2. Haberi Al
    news_content = get_tech_news()
    if not news_content:
        print("Haber bulunamadı, işlem durduruldu.")
        return

    # 3. Tweet Oluştur (Model ismini en garanti haliyle yazıyoruz)
    prompt = f"Aşağıdaki teknoloji haberini bir uzman gibi Türkçe yorumla ve X için etkileyici bir tweet oluştur. Linki mutlaka ekle. 270 karakteri geçme:\n{news_content}"
    
    try:
        # 2026'nın en stabil model ismi: 'gemini-1.5-flash'
        response = client_gemini.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        tweet = response.text
    except Exception as e:
        print(f"Gemini hatası: {e}. Alternatif model deneniyor...")
        # Eğer yukarıdaki hata verirse, 'gemini-pro' (klasik isim) dene
        response = client_gemini.models.generate_content(
            model='gemini-1.5-pro', 
            contents=prompt
        )
        tweet = response.text

    # 4. X'te Paylaş
    try:
        client_x = tweepy.Client(**X_KEYS)
        # Karakter sınırını kontrol et ve tweeti at
        final_tweet = tweet[:280]
        client_x.create_tweet(text=final_tweet)
        print(f"Tweet başarıyla atıldı: {final_tweet}")
    except Exception as e:
        print(f"X API Hatası (İzinlerini kontrol et!): {e}")

if __name__ == "__main__":
    main()
