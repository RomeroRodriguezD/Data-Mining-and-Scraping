from flask import Flask, render_template, make_response, session, jsonify, send_file
from flask_session import Session
import pandas as pd
import xlsxwriter
from config import get_secret_key
from scrapers_spanish_nextpage import ScrapZon, ScrapAli, get_scraper
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = get_secret_key()  # Clave secreta para la sesión
app.config['SESSION_TYPE'] = 'filesystem' # Almacenar la sesión en el sistema de archivos
app.config['SESSION_PERMANENT'] = False

Session(app)

@app.route("/")
def search():
    """Generates the landing page that will show our scraped results"""
    session['amazon_products'] = amazon_products
    session['ali_products'] = ali_products
    session['keyword'] = keyword.title()
    return render_template('results.html', amazon_products = session['amazon_products'], ali_products = session['ali_products'], keyword=session['keyword'])

@app.route('/download_json')
def download_json():
    # Getting session scraped data
    amazon_products = session.get('amazon_products')
    ali_products = session.get('ali_products')
    keywords = session.get('keyword')
    if amazon_products is None and ali_products is None:
        # If there's no data at all
        return render_template('no_products.html')

    # List to store the incoming results

    result = {
        'Amazon': [],
        'AliExpress': []
    }

    for i in range(len(ali_products[0])):
        new_product = {'nombre': ali_products[0][i],
        'precio': ali_products[1][i],
        'review': ali_products[2][i],
        'enlace': ali_products[3][i]}

        result['AliExpress'].append(new_product)

    for i in range(len(amazon_products[0])):
        new_product = {'nombre': amazon_products[0][i],
                       'precio': amazon_products[1][i],
                       'review': amazon_products[2][i],
                       'enlace': amazon_products[3][i]}

        result['Amazon'].append(new_product)

    # Data to JSON and send the response

    json_data = json.dumps(result, indent=4, ensure_ascii=False)
    response = make_response(json_data)

    # Send file to download, with its respective headers
    response.headers['Content-Disposition'] = f'attachment; filename={keywords}_data.json'
    response.headers['Content-type'] = 'application/json'

    return response

@app.route('/download_csv')
def download_excel():
    # Getting gathered data from our session
    amazon_products = session.get('amazon_products')
    ali_products = session.get('ali_products')
    keywords = session.get('keyword')

    if amazon_products is None and ali_products is None:
        # If no data gathered at all
        return render_template('no_products.html')

    # One dataframe from each website
    df_amazon = pd.DataFrame({
        'nombre': amazon_products[0],
        'precio': amazon_products[1],
        'review': amazon_products[2],
        'enlace': amazon_products[3]
    })

    df_aliexpress = pd.DataFrame({
        'nombre': ali_products[0],
        'precio': ali_products[1],
        'review': ali_products[2],
        'enlace': ali_products[3]
    })

    # Creating an Excel file with one page for each site
    filename = f'{keywords}_data.xlsx'

    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df_amazon.to_excel(writer, sheet_name='Amazon', index=False)
        df_aliexpress.to_excel(writer, sheet_name='AliExpress', index=False)

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    keyword = str(input('Introduce space-separated keywords: '))
    browser = get_scraper()
    ali_scraper = ScrapAli(browser=browser)
    amazon_scraper = ScrapZon(browser=browser)
    ali_products = ali_scraper.get_products_info(keyword=keyword, review_sort=True, max_pages=4)
    amazon_products = amazon_scraper.get_products(keyword=keyword, review_rank=True, max_pages=4)
    app.run()


