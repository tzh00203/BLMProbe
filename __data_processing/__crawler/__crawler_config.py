"""
Crawler Configuration:
Centralized configuration for Google and Bing utilities.
"""

PROCESS_COUNT = 1
TIME_SLEEP = 0.6
QUEUE_RETRY_COUNT = 3

# ========================= Google Config =========================

# Headers for Google web scraping
HEADERS_GOOGLE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
}

# Google Custom Search API credentials
# GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your key
# GOOGLE_CX = "YOUR_GOOGLE_CX"  # Replace with your Custom Search Engine ID
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
GOOGLE_CX = "YOUR_GOOGLE_CX"


# Retry count for Google utilities
GOOGLE_RETRY_COUNT = 5

# Default request timeout in seconds
GOOGLE_TIMEOUT = 5

# ========================= Bing Config =========================

# Headers for Bing web scraping
HEADERS_BING = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
}

# Bing API subscription key
BING_API_KEY = "YOUR_BING_API_KEY"  # Replace with your key

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
