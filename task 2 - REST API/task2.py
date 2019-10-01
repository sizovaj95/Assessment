from flask import Flask, request, render_template, jsonify ##import neccessary modules from flask

app = Flask(__name__) ##initialize Flask object

## The first two functions open html files with ingredients for apple pie and honey cake
@app.route('/applepie')## route to bind URL to the function
def apple_pie(): ##define function to get information for apple pie
    return render_template('apple_pie.html') ## render_template to render html file with table to the browser

@app.route('/honeycake')
def honey_cake(): ##define function to get information for honey cake
    return render_template('honey_cake.html') ## render_template to render html file with table to the browser 

###Simplified version of a task

##Create a list of dictionaries with some names of food
items=[{'Name':'Apple_pie'}, {'Name':'Honey_cake'},{'Name':'Carrot_cake'}]

## Code to return a specific item, to be specified when calling a function
@app.route('/item/<string:item>') ##/<string:item> specify title of food (which is string), GET method is default, no need to include into "route"
def choose_one(item): ## define a funciton, with one parameter (name of food specified earlier)
    food=[food for food in items if food['Name']==item] # create a list of food items with the food title specified when calling the function (only one in this case, since name is unique)
    return jsonify({'Food':food[0]}) ##return dictionary of dictionaries with JSON representation

## Add new item to the existing list
@app.route('/newitem', methods=['POST'])## POST method is used
def new_item():
    new_item = {'Name': request.json['item']} ## create dictionary, with Name as a key and value set with the POST request
    items.append(new_item) ## append new dictionary to the list of old dictionaries
    return jsonify({'Food': items}) ##return dictionary of dictionaries with JSON representation

## Edit item in existing list 
@app.route('/edit/<string:item>',methods=['PUT']) ##PUT method is used
def edit_item(item):
    food=[food for food in items if food['Name']==item] ## find all instances with the specified food name (only one in this case) which has to be edited 
    food[0]['Name']=request.json['name'] ## replace this food name with desired one
    return jsonify({'Food':food[0]}) ##return dictionary of dictionaries with JSON representation

## Delete item from the list
@app.route('/delete/<string:item>',methods=['DELETE']) ## DELETE method is used
def delete_item(item):
    food=[food for food in items if food['Name']==item] ## find food item to be deleted
    items.remove(food[0]) ## remove this item from the list 
    return jsonify({'Food':items}) ##return dictionary of dictionaries with JSON representation
    
### Run the app in debug mode, so that don't have to restart the prompt after every change done in the script 
if __name__=='__main__':
    app.run(debug=True)
