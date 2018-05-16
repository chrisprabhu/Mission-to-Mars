from flask import Flask, jsonify
import pandas as pd
import mission_to_mars

app = Flask(__name__)

@app.route("/scrape")
def scraperoute():
    scraped_data = mission_to_mars.scrape()
    return jsonify(scraped_data)

@app.route("/")
def slashroute():
    scraped_data = mission_to_mars.scrape()
    data_table = pd.DataFrame(data=mission_to_mars.results_list).to_html()
    return data_table

app.run(debug=True)

