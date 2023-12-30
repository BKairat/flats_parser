from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import sql
import os
from config import db_name, db_user, db_password, db_host, db_port
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm

def parse_links(url: str, flats: int = 1):
    print("flats -----", flats)
    data = []
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    # conn = psycopg2.connect(
    #     dbname=os.environ.get("POSTGRES_DB"),
    #     user=os.environ.get("POSTGRES_USER"),
    #     password=os.environ.get("POSTGRES_PASSWORD"),
    #     host=os.environ.get("POSTGRES_HOST"),
    #     port=os.environ.get("POSTGRES_PORT")
    # )
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS example_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR,
            image_url VARCHAR
        )
    ''')

    # before writing new elements we need to delete old ones.
    # if the ad is removed from the site, an error may occur that we will not be able to find the photo.
    table_name = "example_table"
    delete_query = sql.SQL("DELETE FROM {}").format(sql.Identifier(table_name))
    cur.execute(delete_query)
    if flats < 0:
        flats = 1

    chrome_options = Options()
    chrome_options.add_argument('--headless')


    page = 0
    for itms in tqdm(range(0, flats, 20)):
        page += 1

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url+str(page))
        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'name')))

        html_content = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html_content, 'html.parser')

        titles = soup.find_all('span', class_="name")
        div_imgs = soup.find_all('div', class_="property ng-scope")

        elements = len(div_imgs)
        if itms + len(div_imgs) > flats:
            elements = flats - itms
        for i in range(elements):
            data.append((titles[i].text, div_imgs[i].find('img').get('src')))
            cur.execute('''
                    INSERT INTO example_table (name, image_url)
                    VALUES (%s, %s)
                ''', (titles[i].text, div_imgs[i].find('img').get('src')))

    conn.commit()
    cur.close()
    conn.close()
    return data
