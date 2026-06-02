import requests
from bs4 import BeautifulSoup
import datetime
import os

# 🔐 必須保持這樣！這是在告訴 Python 去後台找名為 "TELEGRAM_BOT_TOKEN" 的箱子
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URL = "https://www.hkepc.com/forum/forumdisplay.php?fid=14"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_telegram_message(title, link):
    text = f"🚨 *HKEPC 交易廣場有新 Bid 帖！*\n\n📦 *主題:* {title}\n🔗 [點擊直達傳送門]({link})"
    tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(tg_url, json=payload)
    except Exception as e:
        print(f"Telegram 發送失敗: {e}")

def check_hkepc():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.encoding = 'big5'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        threads = soup.find_all('tbody', id=lambda x: x and x.startswith('normalthread_'))
        now_hkt = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        
        for thread in threads:
            author_td = thread.find('td', class_='author')
            if not author_td:
                continue
                
            time_span = author_td.find('span')
            time_str = time_span.get('title') if time_span else author_td.find('em').text.strip()
            
            try:
                if "-" in time_str:
                    post_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                else:
                    post_time = now_hkt
            except:
                post_time = now_hkt

            time_diff = (now_hkt - post_time).total_seconds()
            
            # ⏳ 如果貼文發表時間與現在相差小於 12 分鐘（容許排程些微延遲）
            if 0 <= time_diff <= 720:
                title_tag = thread.find('a', class_='xst')
                if title_tag:
                    title = title_tag.text.strip()
                    href = title_tag['href']
                    full_link = f"https://www.hkepc.com/forum/{href}"
                    
                    send_telegram_message(title, full_link)
                    print(f"發現新帖並發送通知: {title}")

    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    check_hkepc()
