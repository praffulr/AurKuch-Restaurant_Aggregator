from flask import Flask, render_template, redirect, request
import psycopg2
# Connect to the database
db = 'host=127.0.0.1  dbname=project user=postgres password=postgres'
conn = psycopg2.connect(db)
cur = conn.cursor()

app = Flask(__name__)


@app.route("/")
def root():
    cur.execute(
    """
        SELECT name FROM restaurants
        ORDER BY random()
        LIMIT 25
    """)
    rows = cur.fetchall()

    return render_template("base.html", rows=rows)

@app.route("/locations", methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        loc = request.form.get('Id')
        cur.execute(
        """
            SELECT *  FROM locations
            WHERE location = \'{}\'
            LIMIT 25
        """.format(loc))
        rows = cur.fetchall()
    
        return render_template("base.html", rows=rows)

@app.route("/restaurants", methods=['GET', 'POST'])
def restaurantSearch():
    if request.method == 'POST':
        rest = request.form.get('Rest_Id')          #Change the name
        cur.execute(
            """
                SELECT dish_liked
                FROM dishes, restaurants, rest_dish_links
                WHERE rest_dish_links.rest_id = restaurants.restaurant_id
                    AND restaurants.name = \'{}\' 
                    AND rest_dish_links.dish_id = dishes.dish_id
                order by dish_liked asc;
            """.format(rest)
            )
        rows = cur.fetchall()
    
        return render_template("base.html", rows=rows)
if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)