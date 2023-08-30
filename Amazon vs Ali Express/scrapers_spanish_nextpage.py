from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import quote
import time
import re
import random

def get_scraper():
    """Creates a webdriver object. Brave path should be adapted for each case. However
        other browsers could be used as well, with a few modifications.
    """
    brave_path = 'C:\Program Files\BraveSoftware\Brave-Browser\Application\\brave.exe'
    brave_driver = 'C:\\Users\\Usuario\Desktop\Programación\FotoCasa scraper\AmazonScraper\chromedriver.exe'
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    option.add_argument("--start-maximized")
    option.binary_location = brave_path
    browser = webdriver.Chrome(executable_path=brave_driver, options=option)

    return browser

class ScrapAli:

    def __init__(self, browser):

        self.browser = browser
        self.actions = ActionChains(self.browser)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36"
                        }
        self.current_page = 1
    def get_products_info(self, keyword, price_sort=False, review_sort=False, max_pages = 1):
        """Gets products information based on keywords and filters"""
        self.browser.get('https://www.aliexpress.com/')
        time.sleep(4)  # Pause as an attempt to avoid some random "product not found" AliExpress sometimes throw.
        BASE_URL = 'https://www.aliexpress.com/w/wholesale-'
        self.words = str(keyword).split()
        self.joining = ''.join([f'{word}-' for word in self.words])
        self.joining = self.joining[:-1]  # Removes last "-". Not strictly needed, but could help with "product not found" issues.
        self.final_url = BASE_URL + self.joining + '.html'  # Creates the final query.

        ##### Filters #####

        # Prices, ascendant way.
        if price_sort:
            self.final_url += """?&sortType=price_asc"""
        # Reviews, descendant way. Can stack, which isn't the case for Amazon.
        if review_sort:
            if price_sort:
                self.final_url += """&isFavorite=y"""
            else:
                self.final_url += """?&isFavorite=y"""

        web = self.browser.get(self.final_url)
        time.sleep(3)
        print('Starting AliExpress scraping...')

        names_ali = []
        prices_ali = []
        img_paths_ali = []
        reviews_ali = []
        links_ali = []

        for i in range(max_pages):
            # Scrolls down, twice, in order to get all the products and images.
            self.actions.send_keys(Keys.END).perform()
            time.sleep(1)
            self.actions.send_keys(Keys.END).perform()
            time.sleep(4)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            count = 0

            # Gets all the item boxes.

            divs = soup.find_all('a', class_='manhattan--container--1lP57Ag')

            for elem in divs:
                # Each product feature will default to None, unless we find each of them.
                name = None
                price = None
                img_path = None
                review = None
                link = None

                # Gets product name. The try-except is here because there's some stuff with no name, specially very cheap products.
                name = elem.find(lambda tag: tag.name == 'div' and tag.has_attr('title'))
                try:
                    name = name.text
                except:
                    name = 'Not named, check product link.'
                # Gets price, if any.
                price_elem = elem.find('div', class_='manhattan--price-sale--1CCSZfK')

                if price_elem:
                    text_parts = price_elem.find_all('span')
                    price = ''.join([part.get_text() for part in text_parts])

                # Gets review values.

                review_elem = elem.find('span', class_='manhattan--evaluation--3cSMntr')
                if review_elem is not None:
                    review = review_elem.text

                # Gets link to the item webpage.
                link = elem['href']

                # Gets image.
                img_element = elem.find('img', class_='manhattan--img--36QXbtQ')
                if img_element is not None:
                    img_src = 'https:' + str(img_element['src'])
                    # Codifies URL, to avoid ASCII errors.
                    img_src = quote(img_src, safe=':/')
                    # Open and save image
                    req = urllib.request.Request(url=img_src, headers=self.headers)
                    response = urllib.request.urlopen(req)
                    image_content = response.read()
                    img_path = f'./static/images/ali_{count}.jpg'

                    with open(img_path, "wb") as file:
                        file.write(image_content)

                    count += 1

                    names_ali.append(name)
                    prices_ali.append(price)
                    reviews_ali.append(review)
                    links_ali.append(link)
                    img_paths_ali.append(img_path)
            next_page = self.next_page_ali(soup=soup)
            # Changes page
            if self.current_page > max_pages:
                break
            if next_page is None:
                break
            else:
                self.browser.get(next_page)

            time.sleep(random.uniform(3,5))

        print('Scraping from AliExpress done.')
        return [names_ali, prices_ali, reviews_ali, links_ali, img_paths_ali]

    def next_page_ali(self, soup):
        """Swaps to next page. Stops if there's no more."""
        # class de next page: pagination--paginationLink--2ucXUo6 next-next

        end_search_pattern = r"""No se han encontrado resultados para tu búsqueda de (.*). Inténtalo de nuevo.</span>"""
        no_more_results = re.search(end_search_pattern, str(soup))
        if no_more_results:
            return None
        else:
            self.current_page += 1
            new_url = self.final_url + f"""&page={self.current_page}"""
            return new_url

class ScrapZon:

    def __init__(self, browser):

        self.browser = browser
        self.actions = ActionChains(self.browser)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36",
        }

    def get_products(self, keyword, price_sort=False, review_rank=False, max_pages = 1):
        """Starts the search with a given browser. Returns a list of product features found on page
            Note: Amazon only provides 1 filter at a time. This means that you can filter by price
            or review stars, but not both.

        """
        BASE_URL = r'https://www.amazon.es/s?k='
        self.words = str(keyword).split()
        self.final_url = BASE_URL + ''.join([f'{word}+' for word in
                                             self.words])  # + '&language=en_US' # It should create the query. Last + shouldn't matter
        # Sorts by price.
        if price_sort:
            self.final_url += """&s=price-asc-rank"""
        # Sorts by review. Remember that there's no point on mixing filters.
        if review_rank:
            self.final_url += """&s=review-rank"""

        self.browser.get(self.final_url)
        print('Starting Amazon scraping...')
        time.sleep(4)
        # Patterns
        link_pattern = r'<a class="a-size-base a-link-normal s-no-hover s-underline-text s-underline-link-text s-link-style a-text-normal" href="(.*?)">'
        price_pattern_int = r'<span class="a-price-whole">[\d,]+</span'
        price_pattern_flo = r'class="a-price-fraction">([\d]+)</span>'
        review_pattern = r'class="a-icon-alt">(.*) de 5 estrellas</'

        img_count = 0

        prices_list = []
        img_list = []
        review_list = []
        links_list = []
        names_list = []

        # Soup & product boxes -> Here starts the iteration for each page
        total_pages = 1

        clean_names = []
        clean_links = []
        clean_reviews = []
        clean_prices = []
        clean_img = []

        for page in range(max_pages):

            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            divs = soup.find_all(lambda tag: tag.name == 'div' and tag.has_attr('data-index') and tag.has_attr('data-uuid'))

            for element in divs:
                # Product features. Defaults to none.

                name = None
                price = None
                review = None
                link = None
                img_url = None

                # Discards soponsored products that may produces bias in our search.

                if 'Sponsored' in str(element):
                    continue

                # Gets name.

                name_tag = element.find('h2')

                if name_tag:
                    name = name_tag.text

                # Gets price. Amazon webpage divides in various "div" tags.

                price_elem = element.find('span', class_='a-price-whole')

                #price_match_int = re.search(price_pattern_int, str(element))

                if price_elem:
                    price = price_elem.text
                    try:
                        price_match_flo = re.search(price_pattern_flo, str(element))
                        if price_match_flo:
                            price_frac = element.find('span', class_='a-price-fraction')
                            price = price + '.' + price_frac.text
                    except:
                        pass

                # Get reviews.

                review_match = re.search(review_pattern, str(element))
                if review_match:
                    review = review_match.group(1)

                # Get link to the product.

                link_match = re.search(link_pattern, str(element))

                if link_match:
                    link = link_match.group(1)

                # Gets images. Attempt to discard products without image -> Spanish web error approach

                img_elements = element.find_all('img', class_='s-image')

                for img in img_elements[:1]:
                    img_url = img['src']
                    if img_url != 'https://m.media-amazon.com/images/I/111mHoVK0kL._SS200_.png' and img_url != 'https://m.media-amazon.com/images/I/111pigi1ylL.png':
                        img_name = f'./Searchs/images/{[word + "_" for word in self.words]}_{img_count}.jpg'
                        urllib.request.urlretrieve(img_url, filename=img_name)
                        img_count += 1

                img_list.append(img_url)

                names_list.append(name)
                links_list.append(link)
                review_list.append(review)
                prices_list.append(price)

            # Second filter, to clean priceless products and/or other sponsored/not wanted product links.

            for i in range(len(names_list)):
                # Iterates through list, base on names lenght.
                price = prices_list[i]
                img_path = img_list[i]
                review = review_list[i]
                link = links_list[i]
                name = names_list[i]
                # Discard without price
                if price is None:
                    continue
                # Discard unwanted
                if link is not None:
                    if 'sspa/' in link:
                        continue
                # Discards without image:

                clean_names.append(name)
                clean_links.append(link)
                clean_reviews.append(review)
                clean_prices.append(price)
                clean_img.append(img_path)

            next_page = self.next_page_ama(soup=soup)

            if total_pages >= max_pages:
                break

            if next_page:
                self.browser.get(next_page)
                total_pages += 1
                time.sleep(random.uniform(3,5))
            else:
                break

        print('Scraping from Amazon done.')
        return [clean_names, clean_prices, clean_reviews, clean_links, clean_img]

    def next_page_ama(self, soup):
        """Swaps to next page. Stops if there's no more."""
        self.actions.send_keys(Keys.END).perform()
        time.sleep(2)
        # Finds the element <a> that includes "next page":
        next_page_element = soup.find('a', {'aria-label': re.compile(r'Ir a la página siguiente', re.IGNORECASE)})
        # Extrae el atributo "href" del elemento encontrado
        if next_page_element:
            next_page_url = next_page_element.get('href')
            return f'https://www.amazon.es' + next_page_url
def generate_html_report(keyword, aliexpress_data, amazon_data):
    """Generates the HTML report comparing products. Based on keyword.
       AliExpress' products will be placed at left column, while Amazon ones at
       the right one.
    """
    base_html = """<!DOCTYPE html>
                    <html>
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            * {
                              box-sizing: border-box;
                              background-color: #d1ebf7;
                            }

                            /* Create two equal columns that floats next to each other */
                            .column {
                              float: left;
                              width: 50%;
                              padding: 10px;
                              /* height: 300px; /* Should be removed. Only for demonstration */
                              border-radius: 5px;
                              background-color: #aaa;
                            }

                            .row {

                            background-color: #aaa;

                            }

                            /* Clear floats after the columns */
                            .row:after {
                              content: "";
                              display: table;
                              clear: both;
                            }

                            .product-details {
                                float: left;
                                width: 70%;
                                background-color: #aaa;
                            }

                            .product-image {
                                float: right;
                                width: 30%;
                            }

                            .product-header {

                                  margin: auto;
                                  width: 100%;
                                  padding: 10px;
                                  text-align: center;

                            }

                            .product-feature {

                            font-size: 20px;
                            background-color: #aaa;
                            }

                            .title-shop {

                            background-color:#00FFFF;
                            text-align: center;
                            color: red;
                            font-size: 35 px;

                            }

                            /* Responsive layout - makes the two columns stack on top of each other instead of next to each other */
                            @media screen and (max-width: 600px) {
                              .column {
                                width: 100%;
                              }
                            }
                        </style>
                        </head>
                        <body>
                        <div class="product-header">

    """ + f'<p style="font-weight: bold; font-size: 30px;">Product searched: <div style="font-style: italic;font-weight: bold; font-size: 30px;">' \
          f'{keyword.title()}</div></p> </div>'

    base_html += """<div class="row">
                          <div class="column title-shop">
                            <h2 class="title-shop">AliExpress</h2>
                          </div>
                          <div class="column title-shop">
                            <h2 class="title-shop">Amazon</h2>
                          </div>
                </div>"""
    amazon_names, amazon_prices, amazon_reviews, amazon_clean_links, amazon_clean_img = amazon_data
    aliexpress_names, aliexpress_prices, aliexpress_reviews, aliexpress_links, aliexpress_img_paths = aliexpress_data

    # Sets iteration limit. It will last as long as we have some product on any of the sources. If there's no
    # more items in one of the sources, it will just leave an empty column, to keep html structure.

    longest_len = max(len(amazon_names), len(aliexpress_names))

    for i in range(longest_len):

        # Filtering Ali Express products first

        base_html += """<div class="row">"""

        ali_name = None
        ali_price = None
        ali_review = None
        ali_link = None
        ali_img = None

        try:
            ali_name = aliexpress_names[i]
            ali_price = aliexpress_prices[i]
            ali_review = aliexpress_reviews[i]
            ali_link = aliexpress_links[i]
            ali_img = aliexpress_img_paths[i]

            base_html += f"""<div class="row">
                                      <div class="column" style="background-color:#aaa;">
                                        <h2 class="product-feature">{ali_name}</h2>
                                          <div class="product-details">                                                
                                                <br>
                                                <p class="product-feature">Price: {ali_price}</p>
                                                <p class="product-feature">Review: {ali_review}</p>
                                                <a class="product-feature" href="https:{ali_link}">Check the product</a>
                                            </div>
                                         <img src="{ali_img}" class="product-image" width="242" height="227">
                                      </div>"""

        except:
            # Empty column if no product.
            base_html += """<div class="row">
                          <div class="column" style="background-color:#aaa;">
                          </div>"""

        # Filtering Amazon Products

        amazon_name = None
        amazon_price = None
        amazon_review = None
        amazon_link = None
        amazon_img = None

        try:

            amazon_name = amazon_names[i]
            amazon_price = amazon_prices[i]
            amazon_review = amazon_reviews[i]
            amazon_link = amazon_clean_links[i]
            amazon_img = amazon_clean_img[i]

            base_html += f"""<div class="row">
                                          <div class="column" style="background-color:#aaa;">
                                            <h2 class="product-feature">{amazon_name}</h2>
                                            <div class="product-details">
                                                <br>
                                                <p class="product-feature">Price: {amazon_price}€</p>
                                                <p class="product-feature">Review: {amazon_review}</p>
                                                <a class="product-feature" href="https://www.amazon.es/{amazon_link}">Check the product</a>
                                            </div>
                                            <img src="{amazon_img}" class="product-image" width="242" height="227">
                                          </div>
                                    </div>"""
        except:
            # Empty column if no product.
            base_html += """<div class="column" style="background-color:#aaa;">
                              </div>
                            </div>"""

    base_html += '''
            </body>
                </html>
                '''

    # Save html:

    with open(f'./Searchs/{keyword}_comparison.html', 'w', encoding='utf-8') as file:
        file.write(base_html)
    print('HTML report done!')


if __name__ == "__main__":
    brave_path = 'C:\Program Files\BraveSoftware\Brave-Browser\Application\\brave.exe'
    brave_driver = 'C:\\Users\\Usuario\Desktop\Programación\FotoCasa scraper\AmazonScraper\chromedriver.exe'
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    option.add_argument("--start-maximized")
    option.binary_location = brave_path

    browser = webdriver.Chrome(executable_path=brave_driver, options=option)
    keyword = 'camion juguete'
    ali_express = ScrapAli(browser=browser)
    sunglasses_ali = ali_express.get_products_info(keyword=keyword, price_sort=False, review_sort=True, max_pages=3)
    amazon_scrap = ScrapZon(browser=browser)
    sunglasses_ama = amazon_scrap.get_products(keyword=keyword, review_rank=True, price_sort=False, max_pages=3)
    generate_html_report(keyword=keyword, amazon_data=sunglasses_ama, aliexpress_data=sunglasses_ali)
    print('Scrap from AliExpress & Amazon done!')
