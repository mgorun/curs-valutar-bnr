import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)

# --- Helper Functions ---

def fetch_xml_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch XML data from {url}")

def parse_xml(xml_string):
    root = ET.fromstring(xml_string)
    currencies = {}
    
    # Namespace for BNR XML
    namespace = {'bnr': 'http://www.bnr.ro/xsd'}
    
    cube_element = root.find(".//bnr:Cube[@date]", namespace)
    date = cube_element.get("date") if cube_element is not None else None

    if cube_element is not None:
        for rate_element in cube_element.findall(".//bnr:Rate", namespace):
            currency_code = rate_element.get("currency")
            try:
                rate = float(rate_element.text)
                currencies[currency_code] = rate
            except (ValueError, TypeError):
                continue

    return date, currencies

# --- Routes ---

@app.route('/')
def index():
    # 1. Define paths safely using os
    basedir = os.path.abspath(os.path.dirname(__file__))
    json_path = os.path.join(basedir, 'currency_data.json')
    
    # 2. Load JSON data safely
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            currency_data = json.load(json_file)
    except FileNotFoundError:
        currency_data = {} # Fallback if file is missing

    # 3. Fetch and parse BNR data
    url = "https://www.bnr.ro/nbrfxrates.xml"
    base_flag_url = "https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/2.9.0/flags/4x3/"
    
    try:
        xml_data = fetch_xml_data(url)
        date, currency_rates = parse_xml(xml_data)
        
        if date:
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        else:
            formatted_date = "N/A"

        # 4. Merge data
        currency_rates_with_data = {
            code: {"rate": rate, **currency_data.get(code, {})} 
            for code, rate in currency_rates.items()
        }

        return render_template('index.html', 
                               date=formatted_date, 
                               currency_rates=currency_rates_with_data, 
                               base_flag_url=base_flag_url, 
                               author='SoftDesk')
    
    except Exception as e:
        return f"Error fetching data: {str(e)}", 500

# Required for local testing, Vercel ignores this
if __name__ == "__main__":
    app.run(debug=True)