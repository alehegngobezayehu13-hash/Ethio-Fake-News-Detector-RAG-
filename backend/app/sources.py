from dataclasses import dataclass


@dataclass
class Feed:
    name: str
    url: str                  
    language: str            
    domains: tuple[str, ...]  
    paged: bool = False      


@dataclass
class Channel:
    name: str
    username: str  
    language: str  


BBC = ("bbc.com", "bbc.co.uk")
CNN = ("cnn.com",)

FEEDS = [
    Feed("BBC Amharic", "https://feeds.bbci.co.uk/amharic/rss.xml", "am", BBC),
    Feed("BBC Afaan Oromoo", "https://feeds.bbci.co.uk/afaanoromoo/rss.xml", "om", BBC),
    Feed("BBC Tigrinya", "https://feeds.bbci.co.uk/tigrinya/rss.xml", "ti", BBC),
    Feed("BBC Africa", "https://feeds.bbci.co.uk/news/world/africa/rss.xml", "en", BBC),
    Feed("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml", "en", BBC),
    Feed("CNN Africa", "http://rss.cnn.com/rss/edition_africa.rss", "en", CNN),
    Feed("CNN World", "http://rss.cnn.com/rss/edition_world.rss", "en", CNN),
    Feed("Ethiopia Check", "https://ethiopiacheck.org/feed", "en", ("ethiopiacheck.org",), paged=True),
    Feed("VOA Amharic", "https://amharic.voanews.com/api/epiqq", "am", ("voanews.com",)),
    Feed("VOA Tigrinya", "https://tigrigna.voanews.com/api/zgbkyl-vomx-tpe-v-v", "ti", ("voanews.com",)),
    Feed("VOA Afaan Oromoo", "https://www.voaafaanoromoo.com/api/z-ojyl-vomx-tpergbt", "om", ("voaafaanoromoo.com", "voanews.com")),
]

CHANNELS = [
    Channel("TIKVAH-ETHIOPIA (Telegram)", "tikvahethiopia", "am"),
]