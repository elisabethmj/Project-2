from flask import Flask, request, redirect, render_template, session
import psycopg2
import bcrypt
import os



# setup cookie encryption as per
# https://flask.palletsprojects.com/en/2.1.x/quickstart/#sessions
DATABASE_URL = os.environ.get("DATABASE_URL", 'dbname=project_2')
SECRET_KEY = os.environ.get("SECRET_KEY", "restaurants-backup")

app = Flask(__name__)
app.secret_key = SECRET_KEY.encode()

@app.route("/")
def index():
    # using the cookie given to us by the browser
    # look up username in our DB
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    user_id_from_encrypted_cookie = session.get("user_id")
    if user_id_from_encrypted_cookie:
        cursor.execute("""
            SELECT username
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (user_id_from_encrypted_cookie,))
        result = cursor.fetchone()
    else:
        result = None

    if result:
        username = result[0]
    else:
        username = None

    # get restaurant from  restaurant database
    
    cursor.execute(f"""
        SELECT *
        FROM restaurants
        LIMIT 100
    """)
    results = cursor.fetchall()
    

    restaurants = []

    for row in results:
        restaurants.append({
            'id': row[0],
            'user_id': row[1], 
            'restaurant_name': row[2], 
            'suburb': row[3], 
            'city': row[4], 
            'favourite_menu_item': row[5], 
            'price_pp': row[6], 
            'rating_out_of_five': row[7]
        })

    

    return render_template("index.html", restaurants=restaurants, username=username)

@app.route("/restaurant/new")
def restaurant_new():
    return render_template("restaurant_new.html")

@app.route("/restaurant/create", methods=["POST"])
def restaurant_create():
    # get data from submitted form
    user_id = request.form.get("user_id")
    restaurant_name = request.form.get("restaurant_name")
    suburb = request.form.get("suburb")
    city = request.form.get("city")
    favourite_menu_item = request.form.get("favourite_menu_item")
    price_pp = request.form.get("price_pp")
    rating_out_of_five = request.form.get("rating_out_of_five")

    # insert restaurant into restaurant_truck database
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO restaurants (user_id, restaurant_name, suburb, city, favourite_menu_item, price_pp, rating_out_of_five)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, restaurant_name, suburb, city, favourite_menu_item, price_pp, rating_out_of_five))
    connection.commit()

    return redirect("/")

@app.route("/update_restaurant")
def update_food():
    #get id from the query instead of the form
    id = request.args.get('id')

    #get food by id
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('SELECT id, user_id, restaurant_name, suburb, city, favourite_menu_item, price_pp, rating_out_of_five FROM restaurants WHERE id=%s', [id])
    results = cursor.fetchall()
    row = results[0]

    restaurant = {
            'id': row[0],
            'user_id': row[1], 
            'restaurant_name': row[2], 
            'suburb': row[3], 
            'city': row[4], 
            'favourite_menu_item': row[5], 
            'price_pp': row[6], 
            'rating_out_of_five': row[7]
    }

    #render an update page template
    return render_template('edit_restaurant.html', restaurant=restaurant)

@app.route('/update_restaurant_action', methods=['POST'])
def update_restaurant_action():
    # retrieve data from request form
    id = request.form.get("id")
    user_id = request.form.get("user_id")
    restaurant_name = request.form.get("restaurant_name")
    suburb = request.form.get("suburb")
    city = request.form.get("city")
    favourite_menu_item = request.form.get("favourite_menu_item")
    price_pp = request.form.get("price_pp")
    rating_out_of_five = request.form.get("rating_out_of_five")

    # get food by id and update values
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('UPDATE restaurants SET user_id=%s, restaurant_name=%s, suburb=%s, city=%s, favourite_menu_item=%s, price_pp=%s, rating_out_of_five=%s WHERE id=%s', [user_id, restaurant_name, suburb, city, favourite_menu_item, price_pp, rating_out_of_five, id])
    conn.commit()
    conn.close()


    return redirect("/")

@app.route("/delete_restaurant_action", methods=["POST"])
def delete_restaurant_action():
    # get data from submitted form
    id = request.form.get("id")

    # connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM restaurants WHERE id=%s', [id])
    conn.commit()
    conn.close()

    return redirect("/")

# Authentication workflow:
#   1. user visits /login
#   2. flask renders login page with a form to capture username and password
#   3. user fills in username and password in the form of step 2 and submits to flask
#   4. flask looks up user in DB 
#      a. if user exists and password matches,
#         flask set a cookie where the name of the cookie is session.
#         On future requests, the browser would send the session cookie to flask.
#      b. if user does NOT exists and/or password does NOT match
#         then flask redirects user to login page without setting the session cookie

# this route handles step 2 of the authentication workflow
@app.route("/login")
def login_page():
    # plumbing code for us to query DB
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    # using the cookie given to us by the browser
    # look up username in our DB
    user_id_from_encrypted_cookie = session.get("user_id")
    if user_id_from_encrypted_cookie:
        cursor.execute("""
            SELECT username
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (user_id_from_encrypted_cookie,))
        result = cursor.fetchone()
    else:
        result = None
    if result:
        username, = result
    else:
        username = None

    return render_template("login.html", username=username)

# this route handle step 4 of the authentication workflow
@app.route("/login", methods=["POST"])
def process_login_form():
    # plumbing code for us to query DB
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    # create our redirect to homepage response
    response = redirect("/")

    # find user row in users table that matches the submitted username
    cursor.execute("""
        SELECT id, password_hash
        FROM users
        WHERE username = %s
        LIMIT 1
    """, (request.form.get("username"),))
    user = cursor.fetchone()
    if not user:
        return response

    # verify that the password submitted by the user matches
    # the one in our DB
    encoded_password = request.form.get("password").encode()
    user_id, hashed_password = user
    if bcrypt.checkpw(encoded_password, hashed_password.encode()):
        session["user_id"] = user_id

    return response

@app.route("/logout")
def logout():
    # ask the browser to delete the session cookie
    # after which the browser will NOT send cookie to flask
    # hence flask cannot lookup the user in our DB
    session.pop("user_id", None)

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def process_register_form():
    # plumbing code for us to query DB
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    # create our redirect to login response
    response = redirect("/login")

    # find user row in users table that matches the submitted username
    cursor.execute("""
        SELECT id, password_hash
        FROM users
        WHERE username = %s
        LIMIT 1
    """, (request.form.get("username"),))
    user = cursor.fetchone()
    if user:
        return response
    else:
        user_id = request.form.get("username")
        password = request.form.get("password")
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (user_id, hashed_password))
        connection.commit()
        connection.close()
        return response