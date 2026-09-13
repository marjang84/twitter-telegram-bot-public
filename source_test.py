import urllib.request
import urllib.error

urls = [
    "https://rss.xcancel.com/The_RockTrading/rss",
    "https://xcancel.com/The_RockTrading/rss",
]

for url in urls:
    print("\n================================")
    print("TESTING:", url)

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/rss+xml,application/xml,text/xml,*/*"
            }
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()

        text = data.decode("utf-8", errors="replace")

        print("BYTES:", len(data))
        print("FULL RESPONSE START")
        print(text)
        print("FULL RESPONSE END")

    except urllib.error.HTTPError as error:
        print("HTTP ERROR:", error.code)

    except Exception as error:
        print("ERROR:", repr(error))

print("\nTEST FINISHED")
