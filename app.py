from flask import Flask, render_template, request, redirect  # import Flask tools for web pages and forms
import sqlite3  # import so we can store data in a database
import os # used for images

app = Flask(__name__)  # create the Flask application

def init_db():  # function to create the database and table
    conn = sqlite3.connect('database.db')  # connect to the database file
    c = conn.cursor()  # create a cursor 

    c.execute("""  
    CREATE TABLE IF NOT EXISTS items (  
        id INTEGER PRIMARY KEY AUTOINCREMENT,  
        name TEXT,  
        description TEXT,  
        location TEXT,  
        status TEXT  
    )
    """)  # create a table called items if it does not already exist

    try:
        c.execute("ALTER TABLE items ADD COLUMN photo TEXT")
    except:
        pass

    conn.commit()  # save the changes
    conn.close()  

init_db()  # run the database setup when the program starts

@app.route('/')  # define the home page route
def home():  
    return render_template('home.html')  # show the home.html page

@app.route('/report', methods=['GET', 'POST'])  # route for reporting an item
def report():

    if request.method == 'POST':  # check if the form was submitted

        name = request.form['name']  # get item name from the form
        description = request.form['description']  # get item description
        location = request.form['location']  # get location where item was found

        photo = request.files.get('photo')  # get uploaded photo file from the form

        filename = ""  # create empty filename in case no image is uploaded

        if photo and photo.filename != "":  # check if a photo was actually uploaded
            filename = photo.filename  # store file name
            photo.save(os.path.join("static/uploads", filename))  # save image

        conn = sqlite3.connect('database.db')  # connect to database
        c = conn.cursor()  # create cursor

        c.execute("""  
        INSERT INTO items (name, description, location, status, photo)  
        VALUES (?, ?, ?, 'Pending', ?)  
        """, (name, description, location, filename))  # insert item and photo name into database

        conn.commit()  # save changes
        conn.close()  # close database

        return redirect('/')  # return user to home page after submitting

    return render_template('report.html')  # show report form if page is opened normally

@app.route("/browse")
def browse():
    conn = sqlite3.connect("database.db")  # connect to database
    cursor = conn.cursor()  # create cursor

    cursor.execute("SELECT * FROM items WHERE status='Approved'")
    items = cursor.fetchall()  # get items

    cursor.execute("SELECT COUNT(*) FROM items WHERE status='Approved'")
    total = cursor.fetchone()[0]  # count items

    conn.close()  # close connection

    return render_template("browse.html", items=items, total=total)

@app.route('/admin')  # route for the admin panel
def admin():
    conn = sqlite3.connect('database.db')  # connect to the database
    c = conn.cursor()  # create a cursor

    c.execute("SELECT * FROM items")  # get all items
    items = c.fetchall()  # store them in a list

    conn.close()  # close the database

    return render_template('admin.html', items=items)  # show the admin page

@app.route('/approve/<int:item_id>')  # route to approve a specific item
def approve(item_id):
    conn = sqlite3.connect('database.db')  # connect to the database
    c = conn.cursor()  # create a cursor

    c.execute("UPDATE items SET status='Approved' WHERE id=?", (item_id,))  # change item status to Approved
    conn.commit()  # save the change
    conn.close()  # close the database

    return redirect('/admin')  # return to the admin page

@app.route("/request_return/<int:item_id>")  # runs when a user clicks "Request Return"
def request_return_route(item_id):

    connection = sqlite3.connect("database.db")  # connect to  SQLite database
    cursor = connection.cursor()  # creates a cursor so we can run SQL commands

    cursor.execute(
        "UPDATE items SET status = 'Return Requested' WHERE id = ?", 
        (item_id,)
    )  # change the item's status to "Return Requested" in the database

    connection.commit()  # save changes to the database
    connection.close()  # close database connection

    return redirect("/browse")  # sends the user to the browse page


@app.route("/approve_return/<int:item_id>")  # used by the admin to approve the return
def approve_return_route(item_id):

    connection = sqlite3.connect("database.db")  # connects to the database
    cursor = connection.cursor()  # creates cursor

    cursor.execute(
        "UPDATE items SET status = 'Returned' WHERE id = ?", 
        (item_id,)
    )  # updates the item status to "Returned" after the admin confirms it

    connection.commit()  # saves the update
    connection.close()  # closes the database

    return redirect("/admin")  # returns the admin back to the admin panel

@app.route("/deny_return/<int:item_id>")  # route for denying a return request
def deny_return(item_id):

    connection = sqlite3.connect("database.db")  # connects to database
    cursor = connection.cursor()  # creates cursor

    cursor.execute(
        "UPDATE items SET status = 'Approved' WHERE id = ?", 
        (item_id,)
    )  # changes status back to Approved

    connection.commit()  # saves change
    connection.close()  # closes database

    return redirect("/admin")  # returns to admin page

if __name__ == '__main__':  # checks if this file is being run directly
    app.run(debug=True)  # start the server in debug mode