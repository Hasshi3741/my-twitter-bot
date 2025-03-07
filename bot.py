import requests
from bs4 import BeautifulSoup
import os

# 検索するアカウントとキーワード
TARGET_ACCOUNTS = ["ds_izumisano", "furu1_AMrinkuu"]  # 取得したいXアカウントのID
KEYWORDS = ["ストレージ","デュエ"]  # 含まれているべき単語

# Discord Webhook URL
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Xのツイートをスクレイピングする関数
def get_tweets(username):
    url = f"https://nitter.net/{username}"  # Xのクローンサイト（変更の可能性あり）
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []  # 取得失敗時は空のリストを返す

    soup = BeautifulSoup(response.text, "html.parser")
    tweets = []

    for tweet in soup.find_all("div", class_="timeline-item"):
        text = tweet.find("div", class_="tweet-content").text.strip()
        tweet_url = "https://twitter.com" + tweet.find("a", class_="tweet-link")["href"]

        if all(keyword in text for keyword in KEYWORDS):  # すべてのキーワードを含むツイートを取得
            tweets.append(f"{text}\n🔗 {tweet_url}")

    return tweets

# Discordにツイートを送信する関数
def send_to_discord(messages):
    for msg in messages:
        payload = {"content": msg}
        requests.post(DISCORD_WEBHOOK, json=payload)

# メイン処理
if __name__ == "__main__":
    all_tweets = []
    for account in TARGET_ACCOUNTS:
        all_tweets.extend(get_tweets(account))

    if all_tweets:  # 条件に合うツイートがあれば送信
        send_to_discord(all_tweets)
