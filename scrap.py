from bs4 import BeautifulSoup
import requests

URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"


def get_html(url: str) -> BeautifulSoup:
    """Funkce, která vrátí rozparsovaný HTML."""
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def get_parties(soup: BeautifulSoup) -> list[str]:
    """Funkce, která vrátí seznam politických stran."""
    parties = [] # list politických stran 
    tables = soup.find_all("table")[1:] # první tabulka nás nazajímá, obsahuje údaje o obálkách/voličích
    for table in tables:
        rows = table.find_all("tr")[2:]
        for row in rows:
            cells = row.find_all("td")
            # v tabulce jsou i prázdná řádky, které obsahují skrytý text "-", ty nechceme brát v potaz
            # to se dá zjistit v prohlížeči přes inspect element
            if len(cells) > 1 and cells[1].get_text(strip=True) != "-":
                parties.append(cells[1].get_text(strip=True))
    return ["code", "location", "registered", "envelopes", "valid"] + parties # vrátí hlavičku tabulky v .csv


def parse_town_detail(url: str, code: str, name: str) -> list:
    soup = get_html(url)
    tables = soup.find_all("table")

    basic_info_cells = tables[0].find_all("tr")[2].find_all("td") # 3. řádek první tabulky obsahuje potřebné informace
    registered = basic_info_cells[3].get_text(strip=True) # voliči
    envelopes = basic_info_cells[4].get_text(strip=True) # obálky
    valid = basic_info_cells[7].get_text(strip=True) # validní hlasy

    results = [] # počet hlasů pro jednotlivé strany
    for table in tables[1:]:
        rows = table.find_all("tr")[2:]
        for row in rows:
            cells = row.find_all("td")
            # v tabulce jsou i prázdná řádky, které obsahují skrytý text "-", ty nechceme brát v potaz
            # to se dá zjistit v prohlížeči přes inspect element
            if len(cells) > 2 and cells[1].get_text(strip=True) != "-":
                results.append(cells[2].get_text(strip=True))

    return [code, name, registered, envelopes, valid] + results # přidá výsledky pro strany k původním informacím o městě, odpovídá jednomu řádku ve výsledné tabulce .csv




def extract_towns_and_parties(region_url: str) -> tuple:
    """Hlavní funkce."""
    soup = get_html(region_url)
    towns = []
    parties = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")[2:] # hlavička nás nazajímá
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            town_code = cells[0].get_text(strip=True)
            town_name = cells[1].get_text(strip=True)

            link_tag = cells[0].find("a")
            # našli jsme odkaz v prvním sloupci? pokud ne , tak přeskoč
            if not link_tag or "href" not in link_tag.attrs:
                continue # přeskoč, vrátí se na další hodnotu for cyklu

            town_url = BASE_URL + link_tag["href"] # odkaz na město
            # pokud dosud nemám, tak yískám názvy stran
            if not parties:
                detail_soup = get_html(town_url)
                parties = get_parties(detail_soup) # vytvoř data pro hlavičku csv

            # vytvoř řádek s údaji o měste pro csv
            town_data = parse_town_detail(town_url, town_code, town_name)
            towns.append(town_data)

    return towns, parties


# tahle funkce je jen aby se vidělo, čeho se docílilo, ve výsledném kódu nebude použita
def print_region(hlavicka: list[str], towns: list[str]):
    """Pomocná funkce, která vytiskne vše co se uložilo."""
    print("    ".join(hlavicka))
    for town in towns:
        print("    ".join(town)) # "    ".join(town) udělá to, že udělá string ze všech položek listu a vloží mezi ně 4 mezery ( pro čitelnost )



if __name__ == "__main__":
    towns, parties = extract_towns_and_parties(URL)
    print_region(parties, towns)
