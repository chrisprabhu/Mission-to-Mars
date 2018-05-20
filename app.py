""" We start be defining all of the functions that our application will run without running them. 
Then we set up our Flask application which will call the functions it needs when needed.  """

# Imports
import os
import requests
import time
import pymongo
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver
from flask import Flask, jsonify, render_template

# Initialize the Mongo Database.
# To switch between Heroku deployment and local deployment comment the correct "conn" statement below.

#conn = 'mongodb://chrisprabhu:password@ds251548.mlab.com:51548/heroku_m4v9jtnm'
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
mars = client.marsDB


def init_browser():
    driver_path = os.environ.get('GOOGLE_CHROME_SHIM', None)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = driver_path
    chrome_options.add_argument('no-sandbox')
    chrome_options.add_argument('--headless')
    #The commented-out line below may be needed for Heroku deployment. 
    # executable_path = {'executable_path': driver_path}
    return Browser('chrome', executable_path="chromedriver", options=chrome_options, headless=True)




#Create the function which scrapes the web, stores data, and returns the data:
def scrape():
# Initialize the browser
    browser = init_browser()
# NASA Mars News
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    news_title = soup.find("div", class_="content_title").findChildren()[0].string.strip()
    news_p = soup.find("div", class_="rollover_description_inner").text.strip()
# JPL Mars Space Images - Featured Image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(3)
    browser.find_by_id('full_image')[0].click()
    time.sleep(2)
    browser.find_link_by_partial_text('more info')[0].click()
    time.sleep(5)
    soup = BeautifulSoup(browser.html, "html.parser")
    featured_image_url = "https://www.jpl.nasa.gov" + soup.find("img", class_="main_image")['src']
    featured_image_url
# Mars Weather
    url = "https://twitter.com/marswxreport?lang=en"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    mars_weather = soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    mars_weather = mars_weather.split(',')
    url = "https://space-facts.com/mars/"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    table = soup.find("table", id="tablepress-mars")
    table_string = str(table)
    data = pd.read_html(table_string)
    data = data[0]
    data = dict(zip(data[0].tolist(), data[1].tolist()))
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    hemisphere_list = ["Cerberus Hemisphere Enhanced", "Schiaparelli Hemisphere Enhanced", "Syrtis Major Hemisphere Enhanced", "Valles Marineris Hemisphere Enhanced"]
    img_url_list = []

    for hemisphere in hemisphere_list:
        browser.visit(url)
        browser.find_by_text(f"{hemisphere}")[0].click()
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        img_url = soup.find_all("a", text="Sample")[0]['href']
        img_url_list.append(img_url)

    hemisphere_image_urls = [
        {"title": "Cerberus Hemisphere", "img_url": "..."},
        {"title": "Schiaparelli Hemisphere", "img_url": "..."},
        {"title": "Syrtis Major Hemisphere", "img_url": "..."},
        {"title": "Valles Marineris Hemisphere", "img_url": "..."},
    ]

    for dictionary in hemisphere_image_urls:
        dictionary['img_url']

    for x in range(len(hemisphere_image_urls)):
        hemisphere_image_urls[x]['img_url'] = img_url_list[x]

    scraped_data = {
        "News Title": news_title,
        "News Paragraph": news_p,
        "Featured Image URL": featured_image_url,
        "Mars Weather": mars_weather,
        "Mars Data": data,
        "Hemisphere Image Urls": hemisphere_image_urls }

    try:
        item = mars.mission.find_one()
        item_id = item.get('_id')
        mars.mission.update_one({'_id': item_id}, {"$set": scraped_data}, upsert=True)
    except AttributeError: 
        mars.mission.insert_one(scraped_data)
    return scraped_data

def viewTable():
    results = mars.mission.find()[0]
    del results["_id"]
    return results

# Create the Flask application: 

app = Flask(__name__)

@app.route("/scrape")
def scraperoute():
    scraped_data = scrape()

    return jsonify(scraped_data)

@app.route("/")
def slashroute():
    scraped_data = scrape()
    mars_data = scraped_data["Mars Data"]

    return render_template("index.html", 
    featured_image_url=scraped_data["Featured Image URL"],
    mars_weather=scraped_data["Mars Weather"],
    hemisphere_image_urls=scraped_data["Hemisphere Image Urls"],
    news_p=scraped_data["News Paragraph"],
    news_title=scraped_data["News Title"],
    data=mars_data)

@app.route("/noscrape")
def no_scrape():
    database_data = viewTable()

    return jsonify(database_data)

if __name__ == '__main__':
    app.run(debug=True)