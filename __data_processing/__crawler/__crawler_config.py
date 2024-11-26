"""
Crawler Configuration:
Centralized configuration for Google and Bing utilities.
"""

# ========================= Google Config =========================

# Headers for Google web scraping
HEADERS_GOOGLE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Google Custom Search API credentials
GOOGLE_API_KEY = "AIzaSyDXJHCij9rf2SAjn9OESjYZBfXIDbZ2O6s"  # Replace with your key
GOOGLE_CX = "13b381ee978e24fd1"  # Replace with your Custom Search Engine ID

# Retry count for Google utilities
GOOGLE_RETRY_COUNT = 5

# Default request timeout in seconds
GOOGLE_TIMEOUT = 5

# ========================= Bing Config =========================

# Headers for Bing web scraping
HEADERS_BING = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76"
}

# Bing API subscription key
BING_API_KEY = "55b005939e8e4244b7559a7486818b5a"  # Replace with your key

# Bing API endpoint
BING_API_URL = "https://api.bing.microsoft.com/v7.0/search"

# Default parameters for Bing API search
BING_API_PARAMS = {
    "count": 15,  # Number of results per query
    "responseFilter": "webpages",
    "mkt": "en-US",  # Market for search results
}

# Retry count for Bing utilities
BING_RETRY_COUNT = 5

# Default request timeout in seconds
BING_TIMEOUT = 5
