from flask import Flask, request, jsonify
import requests
from model import *
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

@app.route("/final-prod", methods=["GET", "POST"])
def final_p():
    if request.method == "POST":
        category = request.form.get("category")
        product = request.form.get("product_name")
        all_ing = request.form.get("ingredients").split("; ")
        sub_category = request.form.get("sub_category")
        if product is None:
            return "product name not found"
        try:
            if category == "cosmetics":
                sub_category = str(get_cluster(category, product))
            else:
                sub_category = str(get_cluster(category, sub_category))
            ingredients, exempts = generate_ings_exempts(all_ing)
            compounds, left = get_compounds(ingredients)
            summary = get_summary(compounds, exempts, left)
            summary['sub_category'] = sub_category
            return jsonify(summary)

        except Exception as e:
            return str(e)




@app.route("/cosmetics", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        product = request.form.get("product_name")
        if product is None:
            return "product name not found"
        try:
            # cosmetics
            url = "https://incidecoder.com/"
            res = requests.get(url + "search?query={}".format(product))
            soup_data = BeautifulSoup(res.text, "html.parser")

            links = soup_data.find_all("a", class_="klavika simpletextlistitem")
            count = len(links)
          
            top_5_list={}
            
            while len(top_5_list)<5:
                i=len(top_5_list)
                if i+1 > count :
                    break
                specific = links[i]["href"]
                prod_name=links[i].text
                    # print(final_prod_name)
                    
                details = requests.get(url + specific[1:])
                soup = BeautifulSoup(details.text, "html.parser")
                if prod_name not in top_5_list:
                    top_5_list[prod_name]=[]
                
                # all_ing = ()
                for li in soup.find_all("a", class_="ingred-link black"):
                    top_5_list[prod_name].append(li.text.lower())
            
            return jsonify(top_5_list)
        except Exception as e:
            return str(e)


@app.route("/food",methods=["GET","POST"])
def foodie():
    if request.method == "POST":
        product = request.form.get("product_name")
        if product is None:
            return "product name not found"
        try:
        # food
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
            'api_key': os.environ.get('api_key'),  # Replace with your API key
            'query': product,  # Replace with any other required parameters
            }

            
            r = requests.get(url, params=params)
      
            if r.status_code == 200: 
                data = r.json()  
           
                items = data['foods']  
                top_5_list={}
            
                while len(top_5_list) < 5:
                    item=items[len(top_5_list)]
                    item_name= item['description'] 
                    if item_name not in top_5_list:
                        top_5_list[item_name]=item['ingredients'].lower()
                
                return jsonify(top_5_list)
                
            else:
                return 'API request failed: ' + str(r.status_code) + str(os.environ.get('api_key'))
        except Exception as e:
            return str(e)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

