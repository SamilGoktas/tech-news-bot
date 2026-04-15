import tweepy
from groq import Groq # Yeni kütüphane
import requests
import os

# Anahtarlar
X_KEYS = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET")
}
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        if res.get("articles"):
            article = res["articles"][0]
            return f"Haber: {article['title']}\nÖzet: {article['description']}\nLink: {article['url']}"
    except:
        return None
    return None

def main():
    # 1. Groq İstemcisi
    client_groq = Groq(api_key=GROQ_API_KEY)

    # 2. Haberi Al
    news_content = get_tech_news()
    if not news_content:
        print("Haber bulunamadı.")
        return

    # 3. Llama 3 ile Tweet Oluştur
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.1-70b-versatile", # Güçlü ve hızlı Llama 3.1 modeli
            messages=[
                {
                    "role": "system",
                    "content": "Sen profesyonel bir teknoloji editörüsün. Görevin haberleri etkileyici ve kısa tweetlere dönüştürmek."
                },
                {
                    "role": "user",
                    "content": f"Aşağıdaki haberi Türkçe yorumla, heyecan verici bir tweet yap. Linki ekle. Maksimum 270 karakter:\n{news_content}"
                }
            ],
        )
        tweet = completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Hatası: {e}")
        return

    # 4. X'te Paylaş
    try:
        client_x = tweepy.Client(**X_KEYS)
        # AI bazen tırnak içine alabilir, temizleyelim
        final_tweet = tweet.strip().replace('"', '')
        client_x.create_tweet(text=final_tweet[:280])
        print(f"Başarıyla paylaşıldı: {final_tweet[:50]}...")
    except Exception as e:
        print(f"X API Hatası: {e}")

if __name__ == "__main__":
    main()
