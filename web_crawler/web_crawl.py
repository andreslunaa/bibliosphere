import requests
from bs4 import BeautifulSoup

class WebCrawl_Search:
    def __init__(self):
        self.base_url = "https://www.goodreads.com"
        self.headers = {"User-Agent": "Chrome/58.0.3029.110"}

    def search(self, query):
        url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', class_='bookTitle', href=True):
            links.append(link['href'])
        return links

# Example usage for searching a keyword in Goodreads
# Query needs to be updated
query = "Ikigai"
we=WebCrawl_Search()
link=we.search(query)
webcrawl = WebCrawl_Search()
try:
    webcrawl_links = webcrawl.search(query)
    print(f"Links from Goodreads search results for '{query}':")
    print(webcrawl.base_url + webcrawl_links[0])
except IndexError:
    print("Please check the spelling")
