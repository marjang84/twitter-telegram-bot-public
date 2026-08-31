import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import html
import re
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

RSS_URLS = [
    "https://rss.xcancel.com/The_RockTrading/rss",
    "https://nitter.perennialte.ch/The_RockTrading/rss",
    "https://nitter.net/The_RockTrading/rss",
]
LAST_ID_FILE = "last_tweet_id.txt"


def clean_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def get_tweets():
    last_error = None

    for rss_url in RSS_URLS:
        try:
            print(f"Trying RSS source: {rss_url}")

            request = urllib.request.Request(
                rss_url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*"
                }
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                rss_data = response.read()

            root = ET.fromstring(rss_data)
            channel = root.find("channel")

            if channel is None:
                raise ValueError("RSS channel not found")

            tweets = []

            for item in channel.findall("item"):
                title = clean_text(item.findtext("title", ""))
                link = item.findtext("link", "")
                guid = item.findtext("guid", link)

                # Keep the tweet ID consistent even when switching RSS sources
                status_match = re.search(r"/status/(\d+)", link or guid)

                if status_match:
                    tweet_id = status_match.group(1)
                else:
                    tweet_id = guid

                images = []

                # Look for media elements in the RSS item
                for element in item.iter():
                    tag = element.tag.lower()

                    if tag.endswith("content") or tag.endswith("thumbnail"):
                        image_url = element.attrib.get("url", "")
                        media_type = element.attrib.get("type", "")

                        if image_url and (
                            media_type.startswith("image/")
                            or image_url.lower().endswith(
                                (".jpg", ".jpeg", ".png", ".webp")
                            )
                        ):
                            image_url = urllib.parse.urljoin(
                                rss_url,
                                image_url
                            )

                            if image_url not in images:
                                images.append(image_url)

                # Images can also be inside the description HTML
                description = item.findtext("description", "")
                description = html.unescape(description or "")

                found_images = re.findall(
                    r'<img[^>]+src=["\']([^"\']+)["\']',
                    description,
                    flags=re.IGNORECASE
                )

                for image_url in found_images:
                    image_url = urllib.parse.urljoin(
                        rss_url,
                        image_url
                    )

                    if image_url not in images:
                        images.append(image_url)

                tweets.append({
                    "id": tweet_id,
                    "text": title,
                    "images": images
                })

            if not tweets:
                raise ValueError("RSS source returned no tweets")

            print(f"RSS source OK: {rss_url}")
            return tweets

        except Exception as error:
            last_error = error
            print(f"RSS source failed: {rss_url}")
            print(f"Reason: {error}")
            continue

    raise RuntimeError(
        f"All RSS sources failed. Last error: {last_error}"
    )


def telegram_request(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    encoded_data = urllib.parse.urlencode(data).encode()

    try:
        with urllib.request.urlopen(
            url,
            data=encoded_data,
            timeout=30
        ) as response:
            return response.read()

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        print(f"Telegram API error in {method}: HTTP {error.code}")
        print(f"Telegram response: {error_body}")
        raise


def send_text(text):
    telegram_request(
        "sendMessage",
        {
            "chat_id": CHAT_ID,
            "text": text
        }
    )


def send_photo(photo_url, caption=""):
    # Download the image ourselves first
    image_request = urllib.request.Request(
        photo_url,
       headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://nitter.perennialte.ch/"

        }
    )

    with urllib.request.urlopen(image_request, timeout=30) as response:
        image_data = response.read()
        content_type = response.headers.get(
            "Content-Type",
            "image/jpeg"
        )

    boundary = "----TelegramBotBoundary123456789"

    body = bytearray()

    def add_field(name, value):
        body.extend(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n".encode("utf-8")
        )

    add_field("chat_id", CHAT_ID)

    if caption:
        add_field("caption", caption)

    body.extend(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="tweet_image.jpg"\r\n'
        f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
    )

    body.extend(image_data)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    request = urllib.request.Request(
        url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()

    except urllib.error.HTTPError as error:
        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )
        print(f"Telegram photo upload error: HTTP {error.code}")
        print(f"Telegram response: {error_body}")
        raise

def send_to_telegram(tweet):
    text = tweet["text"]
    images = tweet["images"]

    # No image: send the tweet text normally
    if not images:
        send_text(text)
        return

    # Try first image with tweet text
    try:
        send_photo(images[0], text)
    except Exception as error:
        print(f"First photo failed: {error}")
        print("Sending tweet as text instead.")
        send_text(text)
        return

    # Additional images should never stop the bot
    for image_url in images[1:]:
        try:
            send_photo(image_url)
        except Exception as error:
            print(f"Additional photo failed: {error}")
            continue


def load_last_id():
    if not os.path.exists(LAST_ID_FILE):
        return None

    with open(LAST_ID_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()


def save_last_id(tweet_id):
    with open(LAST_ID_FILE, "w", encoding="utf-8") as file:
        file.write(tweet_id)


print("Checking @The_RockTrading...")

tweets = get_tweets()

if not tweets:
    print("No tweets found.")
    raise SystemExit

last_id = load_last_id()

# Keep only tweets with a real numeric X/Twitter status ID
valid_tweets = [
    tweet for tweet in tweets
    if str(tweet["id"]).isdigit()
]

if not valid_tweets:
    print("No valid tweet IDs found.")

elif last_id is None or not str(last_id).isdigit():
    # First-time initialization: remember newest tweet without resending history
    newest_id = max(
        valid_tweets,
        key=lambda tweet: int(tweet["id"])
    )["id"]

    save_last_id(newest_id)
    print("Initial tweet saved. No Telegram message sent.")

else:
    # A tweet is new only if its numeric ID is greater than the saved ID
    new_tweets = [
        tweet for tweet in valid_tweets
        if int(tweet["id"]) > int(last_id)
    ]

    # Send oldest first, newest last
    new_tweets.sort(key=lambda tweet: int(tweet["id"]))

    if not new_tweets:
        print("No new tweets.")

    else:
        for tweet in new_tweets:
            send_to_telegram(tweet)
            print("Sent:", tweet["text"])

        # Save the highest ID that was successfully processed
        newest_id = max(
            new_tweets,
            key=lambda tweet: int(tweet["id"])
        )["id"]

        save_last_id(newest_id)

print("Finished.")
