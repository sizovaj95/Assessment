''''
Flask is a micro web framework written in Python and used for developing web applications. The task is to use it to build REST API
in Python. API is a way of communication between two softwares, which allows two pieces of codes to "interract" with each other. REST is 
a set of rules for building APIs, which makes it easy for softwares to communicate with each ither. 
''''

from flask import Flask, request, render_template, jsonify ##import neccessary modules from flask

app = Flask(__name__) ##initialize Flask object

##Application is ran on 5000th port of localhost (localhost:5000)
## The first two functions open html files with ingredients for apple pie and honey cake

@app.route('/applepie')## route to bind URL to the function. In a browser would type in localhost:5000/applepie 
def apple_pie(): ##define function to get information for apple pie
    return render_template('apple_pie.html') ## render_template to render html file with table to the browser. render_template
## searches for the required html file in the folder "templates" which should be located in the same folder where this script is present. 

@app.route('/honeycake')
def honey_cake(): ##define function to get information for honey cake
    return render_template('honey_cake.html') ## render_template to render html file with table to the browser 

###Simplified version of a task

##Create a list of dictionaries with some names of food, which is to be used in the rest of tasks
items=[{'Name':'Apple_pie'}, {'Name':'Honey_cake'},{'Name':'Carrot_cake'}]

## Code to return only one item from existing list, specified by user
@app.route('/item/<string:item>') ##parameter /<string:item> specifies title of food (which is string), 
## GET method is default, no need to include into "route"
def choose_one(item): ## define a funciton, with one parameter (name of food specified earlier)
    food=[food for food in items if food['Name']==item] # create a list of dictionaries with food items with the food title
    ##specified when calling the function (only one in this case, since name is unique)
    return jsonify({'Food':food[0]}) ##return dictionary of dictionaries with JSON representation (jsonify), which also looks like dictionary
    ## since the list contains only one dictionary we can return this dictionary by specifying index to the food list: food[0], which will
    ##return the first (and only) element of this list.
    
## Add new item to the existing list
@app.route('/newitem', methods=['POST'])## POST method is used
def new_item():
    new_item = {'Name': request.json['item']} ## create dictionary, with Name as a key and value set with the POST request
    items.append(new_item) ## append new dictionary to the list of old dictionaries
    return jsonify({'Food': items}) ##return dictionary of dictionaries with JSON representation

## Edit item in existing list 
@app.route('/edit/<string:item>',methods=['PUT']) ##PUT method is used
def edit_item(item): #define a function with one parameter, item to be edited
    food=[food for food in items if food['Name']==item] ## find all instances with the specified food name (only one in this case) which has to be edited 
    food[0]['Name']=request.json['name'] ## replace this food name with desired one
    return jsonify({'Food':food[0]}) ##return dictionary of dictionaries with JSON representation

## Delete item from the list
@app.route('/delete/<string:item>',methods=['DELETE']) ## DELETE method is used
def delete_item(item):#define a function with one parameter, item to be removed
    food=[food for food in items if food['Name']==item] ## find food item to be deleted, again we get list of only one dictionary
    items.remove(food[0]) ## remove this item from the list 
    return jsonify({'Food':items}) ##return dictionary of dictionaries with JSON representation
    
### Run the app in debug mode, so that don't have to restart the prompt after every change done in the script 
if __name__=='__main__':
    app.run(debug=True)
