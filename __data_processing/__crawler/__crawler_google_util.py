"""
Google Search Utilities:
1. Perform Google search using web scraping or Google Custom Search API.
2. Extract top search results including titles and URLs.
"""

import requests
from bs4 import BeautifulSoup
from __crawler_config import HEADERS_GOOGLE, GOOGLE_API_KEY, GOOGLE_CX, GOOGLE_RETRY_COUNT, GOOGLE_TIMEOUT

def google_search(query: str, retry_count: int = GOOGLE_RETRY_COUNT):
    """
    Perform a Google search using web scraping and return the top 10 results.
    Args:
        query (str): The search query.
        retry_count (int): Number of retry attempts in case of failure.
    Returns:
        list: A 2D list containing [links, titles].
              links: List of URLs from the search results.
              titles: List of corresponding titles.
    """
    url = f"https://www.google.com/search?hl=en&q={query}&btnG=Search"
    html_content = None

    # Retry mechanism for robust crawling
    while retry_count > 0:
        try:
            response = requests.get(url, headers=HEADERS_GOOGLE, timeout=GOOGLE_TIMEOUT)
            if response.status_code == 200:
                html_content = response.text
                break
            else:
                retry_count -= 1
        except Exception as e:
            print(f"Error during Google search: {e}")
            retry_count -= 1

    # Return empty results if no content was retrieved
    if html_content is None:
        return [[], []]

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    search_results = soup.find_all("div", class_="g")
    search_links = [[], []]

    # Extract titles and links from search results
    for result in search_results:
        try:
            title = result.find("h3").text
            link = result.find("a")["href"]
            if link.startswith("http") and link not in search_links[0]:
                search_links[0].append(link)
                search_links[1].append(title)
        except Exception as e:
            print(f"Error parsing result: {e}")

    return search_links


def google_api_search(query: str, retry_count: int = GOOGLE_RETRY_COUNT):
    """
    Perform a Google search using the Google Custom Search API and return the top 10 results.
    Args:
        query (str): The search query.
        retry_count (int): Number of retry attempts in case of failure.
    Returns:
        list: A 2D list containing [links, titles].
              links: List of URLs from the search results.
              titles: List of corresponding titles.
    """
    api_url = f"https://customsearch.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&q={query}&cx={GOOGLE_CX}"

    search_results = None

    # Retry mechanism for robust API calls
    while retry_count > 0:
        try:
            response = requests.get(api_url, timeout=GOOGLE_TIMEOUT)
            if response.status_code == 200:
                search_results = response.json()
                break
            else:
                print(f"Error: Received status code {response.status_code}")
                retry_count -= 1
        except Exception as e:
            print(f"Error during Google API search: {e}")
            retry_count -= 1

    search_links = [[], []]
    if search_results is None or "items" not in search_results:
        return search_links

    # Extract titles and links from API results
    for result in search_results["items"]:
        try:
            title = result.get("title")
            link = result.get("link")
            if link.startswith("http") and link not in search_links[0]:
                search_links[0].append(link)
                search_links[1].append(title)
        except Exception as e:
            print(f"Error parsing API result: {e}")

    # Limit results to top 10
    return [search_links[0][:10], search_links[1][:10]]
