import urllib.request
import urllib.error

urls = [
    "https://mobile.twstalker.com/The_RockTrading",
    "https://twstalker.com/The_RockTrading",
    "https://www.twstalker.com/The_RockTrading",
]

for url in urls:
    print("\n================================")
    print("TESTING:", url)

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "text/html,application/xhtml+xml,*/*",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
            text = data.decode("utf-8", errors="replace")

            print("STATUS:", response.status)
            print("FINAL URL:", response.geturl())
            print("CONTENT-TYPE:", response.headers.get("Content-Type"))
            print("BYTES:", len(data))
            print("START:", text[:1000])

    except urllib.error.HTTPError as error:
        print("HTTP ERROR:", error.code)

    except Exception as error:
        print("ERROR:", repr(error))

print("\nTEST FINISHED")
