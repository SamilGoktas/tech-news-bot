import os
import requests
from atproto import Client
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
            # Sadece başlık ve linki gönderiyoruz ki AI çok dağılmasın
            return f"Haber Başlığı: {article['title']}\nLink: {article['url']}"
    except:
        return None
    return None

def main():
    client_groq = Groq(api_key=GROQ_API_KEY)
    client_bsky = Client()
    client_bsky.login(BSKY_HANDLE, BSKY_PASSWORD)

    news_content = get_tech_news()
    if not news_content:
        print("Haber bulunamadı.")
        return

    # 3. AI ile Post Oluştur (Sınırı çok net vurguluyoruz)
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sen bir teknoloji botusun. Görevin haberi özetleyip Bluesky'da paylaşmak. Çok kısa ve öz olmalısın. KESİNLİKLE 280 karakteri geçme."},
                {"role": "user", "content": f"Şu haberi Türkçe yorumla ve linki sonuna ekle. Toplam metin 280 karakteri ASLA geçmesin:\n{news_content}"}
            ],
        )
        post_text = completion.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        print(f"AI Hatası: {e}")
        return

    # 4. Bluesky'da Paylaş (Garantici Sınır)
    try:
        # Metin her ihtimale karşı 300 karakterden uzunsa kesiyoruz
        final_post = post_text[:300]
        client_bsky.send_post(text=final_post)
        print(f"Bluesky'da başarıyla paylaşıldı: {final_post[:50]}...")
    except Exception as e:
        print(f"Bluesky Paylaşım Hatası: {e}")

if __name__ == "__main__":
    main()
