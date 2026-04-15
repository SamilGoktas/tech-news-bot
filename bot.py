import os
import requests
from atproto import Client
from groq import Groq

# 1. GÜVENLİK: GitHub Secrets'tan anahtarları çekiyoruz
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_KEY = os.getenv("NEWS_API_KEY")

def get_tech_news():
    """Haber başlığını ve kısa özetini çeker."""
    url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        if res.get("articles") and len(res["articles"]) > 0:
            article = res["articles"][0]
            # Linki AI'ya vermiyoruz ki yanlışlıkla paylaşmasın
            return f"Haber Başlığı: {article['title']}\nHaber Özeti: {article['description']}"
    except Exception as e:
        print(f"Haber çekme hatası: {e}")
    return None

def main():
    # 2. Bağlantıları kur
    try:
        client_groq = Groq(api_key=GROQ_API_KEY)
        client_bsky = Client()
        client_bsky.login(BSKY_HANDLE, BSKY_PASSWORD)
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        return

    # 3. Güncel haberi getir
    news_content = get_tech_news()
    if not news_content:
        print("Haber bulunamadı.")
        return

    # 4. Yapay Zeka ile İnsancıl Yorum Oluştur
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": """Sen çok popüler bir teknoloji blogger'ısın. 
                    Takipçilerinle sanki bir kafede sohbet ediyormuş gibi samimi bir dil kullanmalısın.
                    
                    KURALLAR:
                    1. ASLA link paylaşma.
                    2. Haberi olduğu gibi kopyalama, kendi yorumunu ekle (Örn: 'Vay be, sonunda bu da oldu!', 'Bunu beklemiyordum' gibi).
                    3. Samimi, enerjik ve kısa cümleler kur.
                    4. Emojileri dozunda kullan.
                    5. Toplam metin 280 karakteri ASLA geçmesin."""
                },
                {
                    "role": "user", 
                    "content": f"Şu teknoloji gelişmesini takipçilerine heyecanlı bir şekilde anlat (Link verme): \n{news_content}"
                }
            ],
        )
        post_text = completion.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        print(f"AI Hatası: {e}")
        return

    # 5. Bluesky'da Paylaş
    try:
        # Karakter sınırını garantiye al
        final_post = post_text[:300]
        client_bsky.send_post(text=final_post)
        print(f"Başarıyla paylaşıldı: \n{final_post}")
    except Exception as e:
        print(f"Bluesky Gönderim Hatası: {e}")

if __name__ == "__main__":
    main()
