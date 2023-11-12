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

