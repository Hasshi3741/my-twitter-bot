import requests
from bs4 import BeautifulSoup
import os

# 検索するアカウントとキーワード
TARGET_ACCOUNTS = ["ds_izumisano", "furu1_AMrinkuu"]  # 取得したいXアカウントのID
KEYWORDS = ["ストレージ"]  # 含まれているべき単語

# Discord Webhook URL
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

if not DISCORD_WEBHOOK:
    print("❌ エラー: DISCORD_WEBHOOK が設定されていません")
    exit(1)

# Xのツイートをスクレイピングする関数
def get_tweets(username):
    url = f"https://nitter.poast.org/{username}"  # Nitterのミラーサイトを使用
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"⚠️ {username} のツイート取得に失敗しました（ステータスコード: {response.status_code}）")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Nitterの新しいクラス構造をチェック
    tweets = []
    for tweet in soup.find_all("div", class_="tweet-body"):  # 変更点
        text = tweet.text.strip()
        tweet_link_tag = tweet.find("a", class_="tweet-link")

        if tweet_link_tag:
            tweet_url = "https://twitter.com" + tweet_link_tag["href"]
        else:
            tweet_url = "（URLなし）"

        if all(keyword in text for keyword in KEYWORDS):  # すべてのキーワードを含むツイートを取得
            tweets.append(f"{text}\n🔗 {tweet_url}")

    return tweets

# Discordにツイートを送信する関数
def send_to_discord(messages):
    for msg in messages:
        payload = {"content": msg}
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        
        if response.status_code != 204:
            print(f"⚠️ Discord送信エラー: {response.status_code}")

# メイン処理
if __name__ == "__main__":
    all_tweets = []
    for account in TARGET_ACCOUNTS:
        tweets = get_tweets(account)
        if tweets:
            all_tweets.extend(tweets)

    if all_tweets:  # 条件に合うツイートがあれば送信
        send_to_discord(all_tweets)
    else:
        print("✅ 条件に合うツイートはありませんでした")
