import requests
from bs4 import BeautifulSoup

from flask import Blueprint, render_template


from wine_scraper.db import get_db

# Creates blueprint named 'auth'. 
bp = Blueprint('scrape_it', __name__)

# Show single button for beginning the web scrape
@bp.route('/')
def begin_scrape_page():
    return render_template('begin_scrape_page.html')

# Scrape data and return that data in a template. Currently used as a test 
# to see if this will work.
@bp.route('/scrape')
def manipulate_and_show_scraped_data(): 
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
    results = soup.find_all("div", class_="productName")

    # Get only human readable text from each productName div (ie, the name of
    # the wine.)
    names = []
    for item in results: 
        # Selecting only the link.
        link = item.find('a')
        link = link['href']
        # Get only plain text (the wine name)
        item_name = item.get_text()
        # Add tuple of (wine name, wine link) to names list.
        names.append((item_name, link))
        # Open database and add wine names to the correct column. 
        db = get_db()
        db.execute(
            "INSERT INTO wine_list (wine_name, waitrose_link) VALUES (?, ?)", 
            (item_name, link))
    db.commit()


    


    return render_template('show_data.html', result=names)



