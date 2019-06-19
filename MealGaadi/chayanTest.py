# Version  2.0
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from urllib.request import urlopen
app = Flask(__name__)


class Menu:

    def __init__(self):
        self.urlMenu = "http://www.mealgaadi.in/Meal_API/products_api.php?query=product_category"
        self.jsonData = json.load(urlopen(self.urlMenu))
        self.urlCategory = "http://www.mealgaadi.in/Meal_API/products_api.php?query=product_menus_all"
        self.categoryId = ""
        self.subCatData = json.load(urlopen(self.urlCategory))
        self.cart = []
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
        # self.urlCategory += self.categoryId
        print(self.urlCategory)
    def getdata(self):
        subCatItem = []
        for menuObject in self.subCatData:
            if menuObject == 'result':
                for block in self.subCatData[menuObject]:
                    for property in block:
                        if property == "name" and block['category_Id'] == self.categoryId:
                            subCatItem.append(block[property])
        return (subCatItem)

class Items(Menu):

    def exploreItem(self,item):
        halfPlate = "Not Available"
        fullPlate = "Not Available"
        flag = False
        for menuObject in self.subCatData:
            if menuObject == 'result':
                for block in self.subCatData[menuObject]:
                    for property in block:
                        if property == "name" and block[property] == item:
                            if block['Half']:
                                halfPlate =  u"\u20B9" + block['Half']
                                fullPlate =  u"\u20B9" + block['Full']
                                flag = True
                            else:
                                fullPlate =  u"\u20B9" + block['single_Price']
        return [halfPlate,fullPlate]

@app.route('/webhook',methods = ['POST'])
def webhook():
    req = request.get_json(silent=True,force=True)
    res = makeWebhookResult(req)
    res = json.dumps(res,indent = 4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    menu = Me
    if req['queryResult']['action'] == 'showMenuAction':
        menu = Menu()
        speech = "The details you asked are : \n\n " + ",".join([str(i) for i in list(menu.extractMenu())])
        return makeSpeech(speech)
    elif req['queryResult']['action'] == 'expandMenuAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        category = parameters.get('categoryEntity')
        cat = Category()
        cat.extractCatergoryId(category)
        speech = "The details you asked are : \n\n " + ",".join([str(i) for i in list(cat.getdata())])
        return makeSpeech(speech)
    elif req['queryResult']['action'] == 'exploreItemAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        item = parameters.get('items')
        it = Items()
        plateDetails = it.exploreItem(item)
        speech = "Price for " + str(item) + "\n\n" + "for half plate: " + plateDetails[0] +  " full plate: " + plateDetails[1]
        return makeSpeech(speech)
    elif req['queryResult']['action'] == 'addThisToCartAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        quantity = parameters.get('quantity')
        platesize = parameters.get("plateSize")
        if quantity and platesize:
            item_name = req['queryResult']['outputContexts'][0]['parameters']['items']
            it1 = Items()
            price_both = it1.exploreItem(item_name)
            if platesize == "full":
                price = price_both[1]
            else:
                price = price_both[0]
            temp_dict = {'item_name':item_name,'quantity':quantity,'price':int(quantity)*int(price[1:]),'plate_size':platesize}
            menu.cart.append(temp_dict)
            print(menu.cart)
            speech = "Cart Updated Successfully !"
            return makeSpeech(speech)
    elif req['queryResult']['action'] == 'showCartAction':
        result = req['queryResult']
        print(menu.cart)
        temp = []
        j = 0
        for menudict in menu.cart:
            menudict.replace("{","")
            menudict.replace("}","")
            value = menudict.split(',')
            print("Item " +str(j) + "\n " + "\n".join(str(i) for i in value))

def makeSpeech(speech):
    print(speech)
    return {'textToSpeech': speech,'displayText': speech,'fulfillmentText': speech}
 #############################################################################
if __name__ == "__main__":
    port = int(os.getenv('PORT',80))
    app.run(debug=True,port = port,host = '0.0.0.0')
