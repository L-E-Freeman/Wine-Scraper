from flask import Blueprint, render_template
import requests
from bs4 import BeautifulSoup
from wine_scraper.db import get_db, reset_db

# Creates blueprint named 'auth'. 
bp = Blueprint('scrape_it', __name__)

# Show single button for beginning the web scrape
@bp.route('/')
def begin_scrape_page():
    return render_template('begin_scrape_page.html')

# Scrape data and return that data in a template. Currently used as a test 
# to see if this will work.

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
    wine_names = soup.find_all("div", class_="productName")

    wine_list = []
    for item in wine_names: 
        # Selecting only the link.
        link = item.find('a')
        link = link['href']
        # Get only plain text (the wine name), and add tuple of 
        # (wine name, wine link) to names list.
        item_name = item.get_text()
        wine_list.append((item_name, link))
        
    return wine_list

def save_scraped_data_to_db():
    """
    Save wine names and links to db.
    """

    # Flush the database.
    reset_db()

    wine_list = parse_waitrose_wine_html()

    # Unpack tuple list. 
    for tuple in wine_list:
        item_name = tuple[0]
        link = tuple[1]

        db = get_db()
        db.execute(
            "INSERT INTO wine_table (wine_name, waitrose_link) VALUES (?, ?)", 
            (item_name, link))
    db.commit()

@bp.route('/scrape')
def show_scraped_data(): 
    """
    Save scraped data after navigation to the page and show scraped 
    data for troubleshooting purposes.
    """

    save_scraped_data_to_db()

    wine_list = parse_waitrose_wine_html()

    return render_template('show_data.html', result=wine_list)


