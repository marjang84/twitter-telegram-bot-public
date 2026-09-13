import urllib.request
import urllib.error

urls = [
    "https://nitter.net/The_RockTrading/rss",
    "https://nitter.space/The_RockTrading/rss",
    "https://nitter.1d4.us/The_RockTrading/rss",
    "https://nitter.adminforge.de/The_RockTrading/rss",
    "https://nitter.nerdvpn.de/The_RockTrading/rss",
    "https://nitter.woodland.cafe/The_RockTrading/rss",
    "https://nitter.esmailelbob.xyz/The_RockTrading/rss",
]

for url in urls:
    print("\n================================")
    print("TESTING:", url)

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/rss+xml,application/xml,text/xml,text/html,*/*"
            }
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
            text = data.decode("utf-8", errors="replace")

            print("STATUS:", response.status)
            print("CONTENT-TYPE:", response.headers.get("Content-Type"))
            print("BYTES:", len(data))
            print("START:", text[:500])

    except urllib.error.HTTPError as error:
        print("HTTP ERROR:", error.code)

    except Exception as error:
        print("ERROR:", repr(error))

print("\nTEST FINISHED")
