import pyodbc
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from urllib.request import urlopen
app = Flask(__name__)

class Menu:
    def __init__(self):
        self.urlMenu = "https://www.mealgaadi.in/Meal_API/products_api.php?query=product_category"
        self.jsonData = json.load(urlopen(self.urlMenu))
        self.urlCategory = "https://www.mealgaadi.in/Meal_API/products_api.php?query=product_menus&category_Id="
        self.categoryId = ""
    def extractMenu(self):
        menuItems = []
        for menuObject in self.jsonData:
            if menuObject == 'result':
                for block in self.jsonData[menuObject]:
                    for property in block:
                        if property == "name":
                            menuItems.append(block[property])
        return (menuItems)
class Category(Menu):
    def extractCatergoryId(self,category):
        for menuObject in self.jsonData:
            if menuObject == 'result':
                for block in self.jsonData[menuObject]:
                    for property in block:
                        if property == "name" and block[property] == category:
                            self.categoryId = block['category_Id']
        self.urlCategory += self.categoryId
        print(self.urlCategory)
    def getdata(self):
        subCatData = json.load(urlopen(self.urlCategory))
        subCatItem = []
        for menuObject in subCatData:
            if menuObject == 'result':
                for block in subCatData[menuObject]:
                    for property in block:
                        if property == "name":
                            subCatItem.append(block[property])
        return (subCatItem)


@app.route('/webhook',methods = ['POST'])
def webhook():
    req = request.get_json(silent=True,force=True)
    res = makeWebhookResult(req)
    res = json.dumps(res,indent = 4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeSpeech(result):
    speech = "The details you asked are : \n\n " + ",".join([str(i) for i in list(result)])
    print(speech)
    return {'textToSpeech': speech,'displayText': speech,'fulfillmentText': speech}

def makeWebhookResult(req):
    if req['queryResult']['action'] == 'showMenuAction':
        menu = Menu()
        return makeSpeech( menu.extractMenu())
    elif req['queryResult']['action'] == 'expandMenuAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        category = parameters.get('categoryEntity')
        cat = Category()
        cat.extractCatergoryId(category)
        return makeSpeech(cat.getdata())



if __name__ == "__main__":
    port = int(os.getenv('PORT',80))
    app.run(debug=True,port = port,host = '0.0.0.0')
