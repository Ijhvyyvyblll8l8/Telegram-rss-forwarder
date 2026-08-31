import requests, feedparser, imaplib, email
from email.header import decode_header
from datetime import datetime, timedelta

TELEGRAM_TOKEN = "8858867073:AAG8vEaMsuJcdHQ3cG0dixuKoaKnemH0E4E"
CHAT_ID = "7852648519"
GMAIL_USER = "alihosseini22800@gmail.com"
GMAIL_APP_PASSWORD = "inkp eqlz wxhp xqoe"

NEWS_FEEDS = [
    "https://feeds.bbci.co.uk/persian/rss.xml",
    "https://rss.dw.com/rdf/rss-per-all",
    "https://www.isna.ir/rss",
]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for i in range(0, len(text), 4000):
        requests.post(url, data={"chat_id": CHAT_ID,
                                 "text": text[i:i+4000],
                                 "parse_mode": "HTML"})

def get_news():
    lines = ["📰 <b>اخبار امروز</b>"]
    for url in NEWS_FEEDS:
        try:
            feed = feedparser.parse(url)
            lines.append(f"\n<b>{feed.feed.get('title', '')}</b>")
            for e in feed.entries[:3]:
                lines.append(f"• <a href='{e.get('link','')}'>{e.get('title','')}</a>")
        except Exception:
            pass
    return "\n".join(lines)

def check_email():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        _, data = mail.search(None, f"(UNSEEN SINCE {since})")
        ids = data[0].split()
        if not ids:
            mail.logout()
            return "📧 ایمیل جدیدی ندارید."
        lines = [f"📧 <b>{len(ids)} ایمیل جدید:</b>"]
        for eid in ids[-5:]:
            _, msg_data = mail.fetch(eid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            msg = email.message_from_bytes(msg_data[0][1])
            subject = decode_header(msg.get("Subject", ""))[0][0]
            if isinstance(subject, bytes): subject = subject.decode(errors="ignore")
            lines.append(f"✉️ {subject}")
        mail.logout()
        return "\n".join(lines)
    except Exception as e:
        return f"خطای ایمیل: {e}"

if __name__ == "__main__":
    send_telegram(get_news() + "\n\n" + check_email())
