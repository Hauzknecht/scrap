from bs4 import BeautifulSoup
import requests

URL = r"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" # vstupní argument
BASE_URL = r"https://volby.cz/pls/ps2017nss/"
response = requests.get(URL)
html_content = response.text

# Parse the HTML - vytvoří html strom
soup = BeautifulSoup(html_content, "html.parser")

# Najdi všechny <table> elementy - obsahuje města a odkazy
tables = soup.find_all("table")
for table in tables:
    # získej všechny řádky v tabulce
    rows = table.find_all("tr")[2:] # 2: - první dva řádky tě nezajímají, jedná se o hlavičku

    # Získej názvy měst + odkaz na jejich detail
    results = []
    for row in rows:
        # v každým řádku jsou 3 záznamy
        cells = row.find_all("td")
        if len(cells) >= 3:
            town_code = cells[0].get_text(strip=True) # sloupec 0
            town_name = cells[1].get_text(strip=True) # sloupec 1
            # sloupec 2, potřebuje hodnotu odkazu <a href="odkaz">X</a>
            x_link_tag = cells[2].find("a") # nejdu hyperlink
            x_url = x_link_tag["href"] if x_link_tag else None # vemu hodnotu argumentu href
            results.append((town_code, town_name, x_url)) # si ulož jak chces, jestli objekt nebo tak netuším co ti sedí, takhle vznikne list tuplů

    # co sis uložil
    for town_code, town, link in results:
        # odkazy na webu jsou jen relativní ps311?xjazyk=CZ&xkraj=12&xobec=590240&xvyber=7103, takže potřeba před to přilepit základ
        print(f"{town_code} - {town}: {BASE_URL+link}")

# v dalším kroku možné udělat cyklus kde opět pojedeš přes jednotlivá města
# načteš je pomocí bs
#response = requests.get(URL)
#html_content = response.text
#soup = BeautifulSoup(html_content, "html.parser")
# víceméně zas budeš hledat <tables> co jsem se díval, první tabulka je voliči/ obálky, zbytek tabulek strany/hlasy , takže tables[0] - hlasy tables[1:] - strany
