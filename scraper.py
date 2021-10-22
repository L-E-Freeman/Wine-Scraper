from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def scrape_sites():
    URL = "https://www.waitrosecellar.com/all-wines/wine-type/red-wine"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    return print(page.text)