from flask import Flask, render_template
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

app = Flask(__name__)

# Definim o functie care sa preia datele dintr-un XML
def fetch_xml_data(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch XML data from {url}")

def parse_xml(xml_string):
    root = ET.fromstring(xml_string)
    
    # Definim un dictionar in care vom salva cursul BNR
    currencies = {}

    # Cautam si preluam Data cursului BNR
    cube_element = root.find(".//{http://www.bnr.ro/xsd}Body//{http://www.bnr.ro/xsd}Cube[@date]")
    date = cube_element.get("date") if cube_element is not None else None

    # Verificam
    if cube_element is not None:
        # Iteram
        for rate_element in cube_element.findall(".//{http://www.bnr.ro/xsd}Rate"):
            currency_code = rate_element.get("currency")
            rate = float(rate_element.text)
            currencies[currency_code] = rate

    # Returnam data si cursul valutar BNR
    return date, currencies
 

# Link catre steagurile tarilor
base_flag_url = "https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/2.9.0/flags/4x3/"

# Preluam datele din JSON intr-un dictionar
with open('currency_data.json', 'r') as json_file:
    currency_data = json.load(json_file)

# Definim pagina noastra de index in Flask unde vom afisa informatiile
@app.route('/')
def index():

    # Acesta este URL-ul de unde preluam cursul valutar BNR
    url = "https://www.bnr.ro/nbrfxrates.xml"
    
    xml_data = fetch_xml_data(url)
    date, currency_rates = parse_xml(xml_data)

    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")

    currency_rates_with_data = {
        code: {"rate": rate, **currency_data.get(code, {})} for code, rate in currency_rates.items()
    }

    author = 'SoftDesk'

    return render_template('index.html', date=formatted_date, currency_rates=currency_rates_with_data, base_flag_url=base_flag_url, author=author)

if __name__ == "__main__":
    app.run(debug=True)