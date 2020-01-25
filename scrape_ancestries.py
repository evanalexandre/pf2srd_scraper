from selenium import webdriver
from bs4 import BeautifulSoup
import json

driver = webdriver.Chrome('chromedriver.exe')
site = 'https://2e.aonprd.com/'

# list available ancestry pages
driver.get(site + 'Ancestries.aspx')
content = driver.page_source
soup = BeautifulSoup(content, features='html.parser')
ancestry_pages = []
for a in soup.findAll('h2', attrs={'class': 'title'}):
    a = a.find('a')
    page = a.get('href')
    ancestry_pages.append(page)


# explore ancestry pages
ancestries = {}
ancestries['ancestries'] = []
for page in ancestry_pages:
    ancestry = {}
    driver.get(site + page)
    content = driver.page_source
    soup = BeautifulSoup(content, features='html.parser')
    details = soup.find('span', attrs={'id': 'ctl00_MainContent_DetailedOutput'})
    h1titles = [h1 for h1 in details.findAll('h1', attrs={'class': 'title'})]
    mechanics = h1titles[1]
    ancestry['name'] = mechanics.get_text().split('Mechanics')[0].strip()
    traits = details.findAll('span', attrs={'class': 'trait'})
    traits = [trait.find('a').get_text() for trait in traits]
    ancestry['traits'] = traits
    ancestry['source'] = details.find('a', attrs={'class': 'external-link'}).i.get_text()
    ancestry['hit_points'] = int(details.find('h2', string='Hit Points', attrs={'class': 'title'}).next_sibling)
    ancestry['size'] = details.find('h2', string='Size', attrs={'class': 'title'}).next_sibling
    ancestry['speed'] = int(details.find('h2', string='Speed', attrs={'class': 'title'}).next_sibling.split()[0])
    ability_boosts = details.find('h2', string='Ability Boosts', attrs={'class': 'title'})
    sibling = ability_boosts.next_sibling
    boosts = []
    while sibling.name != 'h2':
        if sibling.name != 'br':
            boosts.append(sibling)
        sibling = sibling.next_sibling
    ancestry['ability_boosts'] = boosts
    ability_flaw = details.find('h2', string='Ability Flaw(s)', attrs={'class': 'title'})
    if ability_flaw:
        ancestry['ability_flaw'] = ability_flaw.next_sibling
    languages = details.find('h2', string='Languages', attrs={'class': 'title'})
    sibling = languages.next_sibling
    languages = []
    try:
        while sibling.name != 'h2':
            if sibling.name != 'br':
                try:
                    languages.append(sibling.get_text())
                except:
                    languages.append(sibling)
            sibling = sibling.next_sibling
    except:
        print('Hit end of page')
    ancestry['languages'] = languages
    ancestries['ancestries'].append(ancestry)

with open('ancestries.json', 'w') as outfile:
    json.dump(ancestries, outfile)
