import psycopg2
import bcrypt

connection = psycopg2.connect("dbname=project_2")
cursor = connection.cursor()

# insert some sample food
cursor.execute("""
    INSERT INTO restaurants (user_id, restaurant_name, suburb, city, favourite_menu_item, price_pp, rating_out_of_five) VALUES
    (%s, %s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s, %s)
""",
    (
        'joe', 'emmas snack bar', 'enmore', 'sydney', 'moorish chicken', 61, 4,
        'gabriel', 'jumbo jumbo', 'glebe', 'sydney', 'injera', 35, 5,
        'elise', 'restaurant hubert', 'sydney', 'sydney', 'mille feuille', 200, 5
    )
)
connection.commit()

# insert some user with hashed passwords
# hashed passwords make it harder for hackers to gain access to our web application should they somehow can read our users table
cursor.execute("""
    INSERT INTO users (username, password_hash) VALUES
    (%s, %s),
    (%s, %s),
    (%s, %s)
""",
    (
      "joe", bcrypt.hashpw(b"letmein", bcrypt.gensalt()).decode(),
      "gabriel", bcrypt.hashpw(b"letmein", bcrypt.gensalt()).decode(),
      "elise", bcrypt.hashpw(b"letmein", bcrypt.gensalt()).decode()
    )
)
connection.commit()