import tweepy
import google.generativeai as genai
import requests
import os

# Anahtarları GitHub'dan çekiyoruz
X_KEYS = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET")
}
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
NEWS_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    # En güncel teknoloji haberlerini çekiyoruz
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    res = requests.get(url).json()
    if res.get("articles"):
        article = res["articles"][0] # En baştaki haberi al
        return f"Başlık: {article['title']}\nÖzet: {article['description']}\nLink: {article['url']}"
    return None

def main():
    # 1. AI'yı Hazırla
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 2. Haberi Al
    news_content = get_tech_news()
    if not news_content: return

    # 3. AI'ya Yorumlat (Türkçe ve Etkileyici)
    prompt = f"Aşağıdaki haberi bir teknoloji gurusu gibi Türkçe yorumla ve X için kısa bir tweet oluştur. Linki en sona ekle. Maksimum 270 karakter olsun:\n{news_content}"
    tweet = model.generate_content(prompt).text

    # 4. X'te Paylaş
    client = tweepy.Client(**X_KEYS)
    client.create_tweet(text=tweet[:280])
    print("Tweet başarıyla atıldı!")

if __name__ == "__main__":
    main()
