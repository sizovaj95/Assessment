from flask import Flask, render_template, request, redirect, abort
from flask_mysqldb import MySQL

app = Flask(__name__)##initialize Flask object

### Configure data base for using within Flask 
app.config['MYSQL_HOST'] = 'localhost' #name of the host to conncet to
app.config['MYSQL_USER'] = 'root' #user name to authenticate as
app.config['MYSQL_PASSWORD'] = 'some_password' # authentication password
app.config['MYSQL_DB'] = 'recipies_database' #data base to use

mysql = MySQL(app) #create MySQL instance

'''
Get all recipies ids and names. A function to return all existing recipies with their ids using corresponding SQL query. If the resulting table is empty, a status code 404 returned.
'''
@app.route('/recipies') # route to bind URL to the function. In a browser would type in localhost:5000/recipies
def all_recipies():
    cur = mysql.connection.cursor() #instantiate cursor object to perform data base operations. Cursor object interacts with MySQL server
    resultValue = cur.execute("SELECT * FROM recipe ORDER BY recipe_id")# execute SQL query to select everything from recipe table ordered by ID
    if resultValue > 0: # check if resulting table has at least one row
        recipeDetails = cur.fetchall() # if condition is satisfied, get all rows resulting from the query
        return  render_template('table.html',recipeDetails=recipeDetails) # return resulting table using html template,found in templates folder
    else:
        abort(404) # if condition is not satisfied, return 'Not found' page.

'''
Get all existing ingredients' names and ids. Works in a similar manner to the previous function, with different SQL query.  
'''
@app.route('/ingredients')
def all_ingredients():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM ingredient ORDER BY ingred_id")#select everything from ingredients table, ordered by ingredient ID
    if resultValue > 0:
        recipeDetails = cur.fetchall()
        return  render_template('table.html',recipeDetails=recipeDetails)
    else:
        abort(404)
        
'''
Get a table with recipies and ingredients names and corresponding amounts. Works in a similar manner to previous parts.
'''
@app.route('/amounts')
def all_amounts():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT recipe_name, ingred_name, amount FROM recipe_ingred LEFT JOIN ingredient ON ing_id=ingred_id LEFT JOIN recipe ON rec_id=recipe_id")
    if resultValue > 0:
        recipeDetails = cur.fetchall()
        return  render_template('amounts.html',recipeDetails=recipeDetails)
    else:
        abort(404)
    
'''
Get a specific recipe ingredients with their amounts by recipe name. Specify in the URL for which recipe you would like to get ingredients and their amounts (for example "http://localhost:5000/recipies/Apple pie" will show all the ingredients and amounts needed for apple pie). If a non-existing recipe is requested a status code 404 will be shown. To avoid mistakes in food titles, food items IDs could be used in the URL.
'''
@app.route('/recipies/<string:recipe>')#route with parameter
def recipies(recipe): #define funciton with parameter corresponding to the name of the recipe
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT ingred_name, amount FROM recipe_ingred LEFT JOIN ingredient ON ing_id=ingred_id WHERE rec_id in (SELECT recipe_id FROM recipe WHERE recipe_name= %s)",[recipe]) #execute SQL query. Insert a parameter value (recipe name) as a string into SQL query (%s)
    if resultValue > 0:
        recipeDetails = cur.fetchall()
        return  render_template('table.html',recipeDetails=recipeDetails)
    else:
        abort(404)
       
    
'''
Get recipe name and ID by ingredient name. In URL specify the name of the ingredient and get all recipies which contain that ingredient. If non-existing ingredient is requested, a 'Not found' error will be returned.
'''
@app.route('/<string:ingred_name>')
def recipe_by_ingred(ingred_name):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM recipe WHERE recipe_id in (SELECT rec_id FROM recipe_ingred WHERE ing_id in (SELECT ingred_id FROM ingredient WHERE ingred_name=%s))",[ingred_name])
    if resultValue > 0:
        recipeDetails = cur.fetchall()
        return render_template('table.html',recipeDetails=recipeDetails)
    else:
        abort(404)
  
'''
Get recipe name and ID by ingredient ID. The same as above, except has to specify ingredient ID in the URL and hence, an SQL query is slightly different too. This way is less prone to typos since ID is an integer. 
'''
@app.route('/<int:ingred_id>')
def recipe_by_ingred_id(ingred_id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM recipe WHERE recipe_id in (SELECT rec_id FROM recipe_ingred WHERE ing_id= %s )",[ingred_id])
    if resultValue > 0:
        recipeDetails = cur.fetchall()
        return render_template('table.html',recipeDetails=recipeDetails)
    else:
        return abort(404)
    
'''
Add new recipe into recipe table. Type 'add_recipe' followed by a name of the new recipe into the URL and it will be added into the recipe table. Since recipe ID has AUTO_INCREMENT feature, a new ID will be added automatically. This helps to avoid primary key constraint, since this ensures that no ID is repeated. 
A possible problem is entering repeating names, since recipe name must be unique. Currently an error message which says 'This recipe already exists' appears when already existing name is attempted to be input. Need a way to inform users about prohibited names (which are alredy in the table)
If the operation is successful (the name entered does not exist already) the program redirects you to the page with all recipies names and IDs. A new recipe will appear there as well.
'''
@app.route('/add_recipe/<string:new_recipe>')# enter a URL with new recipe name
def add_recipe(new_recipe):
    try: #try to execute SQL query. If no exceptions occured continue to redirect line
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO recipe(recipe_name) VALUES(%s)",[new_recipe])# an SQL query for inserting new item (only name, ID is generated automatically)
        mysql.connection.commit()# commit changes in the data base to MySQL server
        cur.close() #close cursor object
    except Exception: # if exception noticed, print the message (exception can be any mistake or inconsistency, but the message only handles one case)
        return 'This recipe already exists'
    return redirect('/recipies')  # redirect to the page with recipies name and IDs

'''
Add new ingredient to the ingredients table. Similar to the previous part, with the same problem of repeating names and similar error message. Here a new ingredient name is specified in the URL and this new ingredient is added to the existing table, with ID generated automatically as well. A successful operation redirects to the page with all ingredients and new ingredient appears there too.
'''

@app.route('/add_ingredient/<string:new_ingredient>')
def add_ingredient(new_ingredient):
    try:       
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO ingredient(ingred_name) VALUES(%s)",[new_ingredient])
        mysql.connection.commit()
        cur.close()
    except Exception: 
        return 'This ingredient already exists'        
    return redirect('/ingredients')

'''
Add amount needed for new recipe and new ingredient into the recipe_ingred table. This table references two other tables with information about recipies and ingredients. To avoid breaking referential integrity constraint, firstly have to create new recipe in recipe table and add ingredients for this recipe to the ingredient table and only then combine them in the child table with amounts. Otherwise an error message will be raised, asking to check if recipe and ingredient exist. This situation has to be handled, so that it is not possible to input non-existing IDs (or names).
Here POST method is used along with GET. When a neccessary URL is typed in, a user gets a form to fill in asking to specify an ID of the recipe, an ID of the ingredient and the amount of the ingredient for this recipe. This information is then inserted into recipe_ingred table. When this is done, the user is redirected to the page showing all recipies names with corresponding ingredient names and amounts needed for the recipe.
'''

@app.route('/add_amount', methods=['GET', 'POST'])
def add_amount(): 
    #firstly receive a form to fill in 
    if request.method == 'POST': #use post method since the form with information is submitted
        # Fetch form data
        recipeDetails = request.form #call the form to retrieve information from it
        recipe_id = recipeDetails['recipe_id'] #extract recipe ID from the form
        ingred_id = recipeDetails['ingred_id'] #extract ingredient ID from the form
        amount=recipeDetails['amount'] #extract amount from the form
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO recipe_ingred VALUES (%s,%s,%s)",(recipe_id, ingred_id,amount))#insert extracted information to the recipe_ingred table
            mysql.connection.commit()
            cur.close()
        except Exception:
            return 'Check if recipe and ingredient you are trying to use exist in corresponding tables'
        return redirect('/amounts') #redirect to the page with amounts of ingredients for all recipies
    return render_template('new_amount.html')#show the form to be filled in
    
'''
Edit existing amounts in the recipe_ingred table. This program asks a user to fill in a form again. Here the name of the recipe, the name of the ingredient and the new amount to replace the old one are filled in. The UPDATE query is used to replace amount in the table. To avoid typos, IDs could be used instead of names again. After completing the form the program redirects to page with ingredients for the recipe specified. It either returns a table with ingredients or 'Not found page' if names of recipe or ingredient are non-existing (or there was a typo).
The code is similar to the previous part, with differnet form and SQL query.
'''

### Edit amounts
@app.route('/edit', methods=['GET', 'POST'])
def edit_amount():
    if request.method == 'POST':
        # Fetch form data
        recipeDetails = request.form
        recipe_name = recipeDetails['recipe_name']
        ingred_name = recipeDetails['ingred_name']
        new_amount=recipeDetails['new_amount']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE recipe_ingred SET amount=%s WHERE rec_id = (SELECT recipe_id FROM recipe WHERE recipe_name=%s) AND ing_id = (SELECT ingred_id FROM ingredient WHERE ingred_name=%s)",(new_amount, recipe_name,ingred_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/recipies/{}'.format(recipe_name))
    return render_template('edit_amount.html')

'''
Removes a recipe from the recipe table and corresponding entries from recipe_ingred table (ON DELETE CASCADE). Specify a recipe to delete in the URL and it will be removed from all tables where it was mentioned. However ingredients for that recipe (if there were any new) will stay in the ingredient table. After executing SQL query, the user is redirected to the page showing all remaining recipies. 
The program does not return any error if the item to be removed does not exist in the recipe table.
Works similarly to adding recipe, only SQL query is different.
'''
    
@app.route('/remove/<string:recipe_to_remove>')
def remove_recipe(recipe_to_remove):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM recipe WHERE recipe_name=%s",[recipe_to_remove]) # DELETE query
    mysql.connection.commit()
    cur.close()
    return redirect('/recipies')
  

if __name__ == '__main__':
    app.run(debug=True)
