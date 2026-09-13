import urllib.request
import urllib.error

urls = [
    "https://rss.xcancel.com/The_RockTrading/rss",
    "https://nitter.perennialte.ch/The_RockTrading/rss",
    "https://xcancel.com/The_RockTrading/rss",
    "https://nitter.poast.org/The_RockTrading/rss",
    "https://nitter.privacyredirect.com/The_RockTrading/rss",
    "https://nitter.tiekoetter.com/The_RockTrading/rss",
    "https://nuku.trabun.org/The_RockTrading/rss",
    "https://twiiit.com/The_RockTrading/rss",
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

            print("STATUS:", response.status)
            print("CONTENT-TYPE:", response.headers.get("Content-Type"))
            print("BYTES:", len(data))
            print("START:", data[:200].decode("utf-8", errors="replace"))

    except urllib.error.HTTPError as error:
        print("HTTP ERROR:", error.code)

    except Exception as error:
        print("ERROR:", repr(error))

print("\nTEST FINISHED")
