# beautifulsoup으로 파싱
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
  browser = p.chromium.launch(headless=False)
  page = browser.new_page()
  page.goto("http://quotes.toscrape.com/")
  html = page.content()
  soup = BeautifulSoup(html, 'lxml')
  #print(soup.find('span', class_='text').get_text())
  #print(soup.select_one('span.text').text)
  
  #body > div > div:nth-child(2) > div.col-md-8 > div:nth-child(1) > span:nth-child(2) > small
  #print(soup.select_one('small.author').text)

  quotes = soup.select('div.quote')  # 리스트로 반환
  quotes_list = []

  for quote in quotes:
    quotes_list.append({'quote':quote.select_one('span.text').text,
                      'author':quote.select_one('small.author').text})

  import pandas as pd
  df = pd.DataFrame(quotes_list)
  print(df.head())
  #print(quotes_list)