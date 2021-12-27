from flask import Blueprint, render_template
import requests
from bs4 import BeautifulSoup
from wine_scraper.db import get_db, reset_db


bp = Blueprint('scrape_it', __name__)
# Show single button for beginning the web scrape
@bp.route('/')
def begin_scrape_page():
    return render_template('begin_scrape_page.html')

def parse_waitrose_wine_html(): 
    """
    Generate list of tuples of waitrose wine names and corresponding 
    links.
    """
    # By finding the XHR/Fetch data on the Waitrose site, we can find the 
    # CategoryNavigationResultsView, which allows us to change the 'pagesize'
    # in the URL. Changing this to 470 (the amount of wines that Waitrose
    # currently stock) allows us to view all 470 wines on one page, rather than 
    # having to navigate through button presses to scrape each page 
    # individually. 
    URL = 'https://www.waitrosecellar.com/webapp/wcs/stores/servlet/CategoryNavigationResultsView?pageSize=470&manufacturer=&searchType=&resultCatEntryType=&catalogId=10551&categoryId=1073016&langId=-1&storeId=10701&sType=SimpleSearch&filterFacet=&metaData=aXNDb3Jwb3JhdGVXaW5lOiJOIg=='
    # Pass a user agent so access is not denied by site.
    page = requests.get(URL, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'})
    soup = BeautifulSoup(page.content, "html.parser")
    # productName is class name used by Waitrose for their links, which also
    # includes plain text with the wine name.
    wine_cards = soup.find_all("div", class_="productCard")


    # Return error if wine names not found.
    if len(wine_cards) == 0:
        error_msg = f"Could not find any wine names. Please check if"
        "the Waitrose website has been changed."
        return error_msg
    else:
        wine_list = []
        for item in wine_cards:
            product_name_div = item.find("div", class_="productName")
            link = product_name_div.find('a')
            link = link['href']
            item_name = product_name_div.get_text().strip()
            
            item_price_div = item.find("div", class_="productCurrentPrice")
            item_price = item_price_div.get_text()

            # Change price to correct format.
            chars_to_remove = "Now£"
            for char in chars_to_remove:
                item_price = item_price.replace(char, "")

            wine_list.append((item_name, link, item_price))

        return wine_list

def save_scraped_data_to_db():
    """
    Save wine information to db.
    """

    # Flush the database.
    reset_db()
    wine_list = parse_waitrose_wine_html()

    # Unpack tuple list. 
    for tuple in wine_list:
        item_name = tuple[0]
        link = tuple[1]
        price = tuple[2]

        db = get_db()
        db.execute(
            "INSERT INTO wine_table (wine_name, waitrose_link, price) VALUES (?, ?, ?)", 
            (item_name, link, price))
    db.commit()


def get_wine_names_for_search():
    """Queries database for the names of stored wine names for use in vivino 
    search."""
    db = get_db()
    wine_names = db.execute(
        'SELECT wine_name FROM wine_table'
    ).fetchall()

    return wine_names


def search_vivino_for_wine_names():
    """
    Search vivino for each wine name in list from waitrose, look for exact 
    matches.
    """

    # We're going to have to do something about Waitrose listings being 
    # slightly different from Vivino's for the same wine. Perhaps percentage
    # match? 

    base_URL = "https://www.vivino.com/search/wines?q="

    # Loop through wine_names and create a list of URL's by adding the wine 
    # name search to base url. 
    wine_names = get_wine_names_for_search()
    wines_for_querying = []
    for wine in wine_names:
        formatted_wine_name = wine[0].rstrip().replace(" ", "+")
        wines_for_querying.append(formatted_wine_name)
    
    
    for item in wines_for_querying:
        full_URL = base_URL + item


    return wines_for_querying

    

def get_wine_info_for_display():
    """Queries database for the names of stored wine names."""
    db = get_db()
    wine_info = db.execute(
        'SELECT wine_name, waitrose_link, price FROM wine_table'
    ).fetchall()

    return wine_info

@bp.route('/scrape')
def show_scraped_data(): 
    """
    Save scraped data after navigation to the page and show scraped 
    data for troubleshooting purposes.
    """

    save_scraped_data_to_db()

    wines = search_vivino_for_wine_names()
    
    return render_template('show_data.html', wines = wines)
 