from dataclasses import dataclass

@dataclass
class Feed:
    name: str
    url: str                  
    language: str             
    domains: tuple[str, ...]


BBC = ("bbc.com", "bbc.co.uk")

FEEDS = [
    Feed("BBC Amharic", "https://feeds.bbci.co.uk/amharic/rss.xml", "am", BBC),
    Feed("BBC Afaan Oromoo", "https://feeds.bbci.co.uk/afaanoromoo/rss.xml", "om", BBC),
    Feed("BBC Tigrinya", "https://feeds.bbci.co.uk/tigrinya/rss.xml", "ti", BBC),
    Feed("BBC Africa", "https://feeds.bbci.co.uk/news/world/africa/rss.xml", "en", BBC),
    Feed("Ethiopia Check", "https://ethiopiacheck.org/feed", "en", ("ethiopiacheck.org",)),
]
