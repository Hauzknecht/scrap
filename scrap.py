from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests

URL = r"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"  # vstupní argument
BASE_URL = r"https://volby.cz/pls/ps2017nss/"
response = requests.get(URL)
html_content = response.text
# Parse the HTML - vytvoří html strom
soup = BeautifulSoup(html_content, "html.parser")


@dataclass
class Town:
    code: int
    location: str  # name
    registered: int
    envelopes: int
    valid: int
    results: list[int]  # seřazený počet hlasů pro jednotlivé strany

    def __str__(self):
        return f"{self.code} {self.location} {self.registered} {self.envelopes} {self.valid} {' '.join(str(v) for v in self.results)}"


@dataclass
class Region:
    parties: list[str]
    towns: list[Town]

    def __str__(self):
        return f"Parties: {' '.join(str(v) for v in self.parties)}"

    def get_parties(self, link: str):
        response = requests.get(link)
        html_content = response.text
        # Parse the HTML - vytvoří html strom
        soup = BeautifulSoup(html_content, "html.parser")
        # Najdi všechny <table> elementy - obsahuje údaje o voličích a tabulky se stranami a výsledky
        parties_tables = soup.find_all("table")[1:]  # první tabulka nás nezajímá
        for table in parties_tables:
            rows = table.find_all("tr")[2:]  # 2: - první dva řádky nás nezajímají, jedná se o hlavičku
            for row in rows:
                cells = row.find_all("td")
                if cells[1].get_text(strip=True) != "-":  # prázdné řádky mají skrytou hodnotu -
                    self.parties.append(cells[1].get_text(strip=True))  # sloupec s názvem strany


def create_town(code: int, location: str, link: str) -> Town:
    response = requests.get(link)
    html_content = response.text
    # Parse the HTML - vytvoří html strom
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")
    basic_info = tables[0].find_all("tr")[2]  # údaje o volební účasti jsou v první tabulce 3. řádek
    basic_info_cells = basic_info.find_all("td")
    parties_tables = soup.find_all("table")[1:]  # tabulky s hlasy pro strany
    results = []  # pro uchování hlasů
    for table in parties_tables:
        rows = table.find_all("tr")[2:]  # 2: - první dva řádky nás nezajímají, jedná se o hlavičku
        for row in rows:
            cells = row.find_all("td")
            if cells[1].get_text(strip=True) != "-":  # prázdné řádky mají skrytou hodnotu -
                results.append(cells[2].get_text(strip=True))  # sloupec s počtem hlasů
    return Town(
        code,
        location,
        basic_info_cells[3].get_text(strip=True),
        basic_info_cells[4].get_text(strip=True),
        basic_info_cells[7].get_text(strip=True),
        results,
    )


region = Region([], [])  # inicializace objektu

# Najdi všechny <table> elementy - obsahuje města a odkazy
tables = soup.find_all("table")
for table in tables:
    # získej všechny řádky v tabulce
    rows = table.find_all("tr")[2:]  # 2: - první dva řádky nás nezajímají, jedná se o hlavičku

    # Naplň objekty
    for row in rows:
        # v každým řádku jsou 3 záznamy
        cells = row.find_all("td")
        if len(cells) >= 3:
            town_code = cells[0].get_text(strip=True)  # sloupec 0
            town_name = cells[1].get_text(strip=True)  # sloupec 1
            # sloupec 2, potřebuje hodnotu odkazu <a href="odkaz">kod obce</a>
            x_link_tag = cells[0].find("a")  # nejdu hyperlink
            x_url = x_link_tag["href"] if x_link_tag else None  # vemu hodnotu argumentu href
            if x_url:  # není prázdný řádek / mám odkaz
                if not region.parties:  # nemám názvy stran
                    region.get_parties(BASE_URL + x_url)  # naplním strany do objektu region
                region.towns.append(create_town(town_code, town_name, BASE_URL + x_url))


print(region)
for town in region.towns:
    print(town)
