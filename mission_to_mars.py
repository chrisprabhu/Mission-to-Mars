
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import time
import pymongo
from splinter import Browser
import pandas as pd

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
mars = client.marsDB

# In[27]:





# In[2]:
def scrape():

# NASA Mars News
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"


# In[3]:


    html = requests.get(url)


# In[4]:


    soup = BeautifulSoup(html.text, 'html.parser')


# In[5]:


    news_title = soup.find("div", class_="content_title").findChildren()[0].string.strip()
    news_p = soup.find("div", class_="rollover_description_inner").text.strip()


# In[6]:


# JPL Mars Space Images - Featured Image


# In[7]:


    browser = Browser('chrome', headless=False)


# In[8]:


    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(3)


# In[9]:


    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(2)
    browser.click_link_by_partial_text('more info')
    time.sleep(5)


# In[10]:


    soup = BeautifulSoup(html.text, 'html.parser')


# In[11]:


    featured_image_url = soup.find_all("img", class_="main_image")
    featured_image_url


# In[12]:


# Mars Weather


# In[13]:


    url = "https://twitter.com/marswxreport?lang=en"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')


# In[14]:


    mars_weather = soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text


# In[15]:


    url = "https://space-facts.com/mars/"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    table = soup.find("table", id="tablepress-mars")


# In[16]:


    table_string = str(table)


# In[17]:


    data = pd.read_html(table_string)
    data = data[0]


# In[18]:


    data = dict(zip(data[0].tolist(), data[1].tolist()))


# In[19]:


    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)


# In[20]:


    hemisphere_list = ["Cerberus", "Schiaparelli", "Syrtis", "Valles"]
    img_url_list = []
    for hemisphere in hemisphere_list:
        browser.visit(url)
        browser.click_link_by_partial_text(f"{hemisphere}")
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        img_url = soup.find_all("a", text="Sample")[0]['href']
        img_url_list.append(img_url)


# In[21]:


    hemisphere_image_urls = [
        {"title": "Cerberus Hemisphere", "img_url": "..."},
        {"title": "Schiaparelli Hemisphere", "img_url": "..."},
        {"title": "Syrtis Major Hemisphere", "img_url": "..."},
        {"title": "Valles Marineris Hemisphere", "img_url": "..."},
    ]


# In[22]:


    for dictionary in hemisphere_image_urls:
        dictionary['img_url']


# In[23]:


    for x in range(len(hemisphere_image_urls)):
        hemisphere_image_urls[x]['img_url'] = img_url_list[x]


# In[24]:



    scraped_data = {
        "News Title": news_title,
        "News Paragraph": news_p,
        "Featured Image URL": featured_image_url,
        "Mars Weather": mars_weather,
        "Mars Data": data,
        "Hemisphere Image Urls": hemisphere_image_urls }


    mars.mission.insert_one(scraped_data)
    return scraped_data

# In[25]:







# In[26]:





# In[28]:

def viewTable():


# In[29]:

    results = mars.mission.find()
    results_list = []
    for row in results:
        results_list.append(row)
    return results_list
# In[30]:

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/scrape")
def scraperoute():
    scraped_data = scrape()
    return jsonify(scraped_data)

@app.route("/")
def slashroute():
    results_list = viewTable()
    data_table = pd.DataFrame(data=results_list).to_html()
    return data_table

app.run(debug=True)


# In[31]:


    

