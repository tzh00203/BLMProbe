"""
Bing Search Utilities:
1. Perform Bing search using web scraping or Bing API.
2. Extract top search results including titles and URLs.
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from __crawler_config import HEADERS_BING, BING_API_KEY, BING_API_URL, BING_API_PARAMS, BING_RETRY_COUNT

def bing_search(search_query: str, retry_count: int = BING_RETRY_COUNT):
    """
    Perform a Bing search using web scraping and return the top 10 results.
    Args:
        search_query (str): The search query.
        retry_count (int): Number of retry attempts in case of failure.
    Returns:
        list: A 2D list containing [links, titles].
              links: List of URLs from the search results.
              titles: List of corresponding titles.
    """
    url = f"https://cn.bing.com/search?q={search_query}&ensearch=1"
    html_content = None

    # Retry mechanism for robust crawling
    while retry_count > 0:
        try:
            response = requests.get(url, headers=HEADERS_BING)
            if response.status_code == 200:
                html_content = response.text
                break
            else:
                retry_count -= 1
        except Exception as e:
            print(f"Error during Bing search: {e}")
            retry_count -= 1

    # Return empty results if no content was retrieved
    if html_content is None:
        return [[], []]

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    search_results = soup.find_all("li", class_="b_algo")
    search_links = [[], []]

    # Extract titles and links from search results
    for result in search_results:
        try:
            title = result.find("h2").text
            link = result.find("cite").text
            if link.startswith("http") and link not in search_links[0]:
                search_links[0].append(link)
                search_links[1].append(title)
        except Exception as e:
            print(f"Error parsing result: {e}")

    return search_links


def bing_api_search(search_query: str, retry_count: int = BING_RETRY_COUNT):
    """
    Perform a Bing search using the Bing API and return the top 10 results.
    Args:
        search_query (str): The search query.
        retry_count (int): Number of retry attempts in case of failure.
    Returns:
        list: A 2D list containing [links, titles].
              links: List of URLs from the search results.
              titles: List of corresponding titles.
    """
    search_results = None

    # Retry mechanism for robust API calls
    while retry_count > 0:
        try:
            response = requests.get(
                BING_API_URL,
                headers={"Ocp-Apim-Subscription-Key": BING_API_KEY},
                params={"q": search_query, **BING_API_PARAMS}
            )
            if response.status_code == 200:
                search_results = response.json()
                break
            else:
                print(f"Error: Received status code {response.status_code}")
                retry_count -= 1
        except Exception as e:
            print(f"Error during Bing API search: {e}")
            retry_count -= 1

    search_links = [[], []]
    if search_results is None or "webPages" not in search_results:
        return search_links

    # Extract titles and links from API results
    for result in search_results["webPages"]["value"]:
        try:
            title = result["name"]
            link = result["url"]
            if link.startswith("http") and link[-4:] != ".pdf" and link not in search_links[0]:
                search_links[0].append(link)
                search_links[1].append(title)
        except Exception as e:
            print(f"Error parsing API result: {e}")

    # Limit results to top 10
    return [search_links[0][:10], search_links[1][:10]]


if __name__ == "__main__":
    pprint(bing_api_search("IoT device security"))
