from flask import Flask, render_template, redirect, request
import psycopg2
# Connect to the database
db = 'host=127.0.0.1  dbname=project user=prafful password=pandu'
conn = psycopg2.connect(db)
cur = conn.cursor()

app = Flask(__name__)


@app.route("/")
def root():
    # cur.execute("""SELECT name FROM restaurantsORDER BY random()LIMIT 25""")
    # rows = cur.fetchall()

    return render_template("users.html")

@app.route("/homepage", methods = ['POST'])
def home():
    if request.method == 'POST':
        username = request.form.get("Username")
        password = request.form.get("Password")
        cur.execute(
        """
            CREATE VIEW current_user_details as
            select * from users
            where users.username = \'{}\' and users.password = \'{}\'
        """.format(username, password)
        )
        cur.execute(
        """
            WITH locs as
            (
                select distinct(locations.location) as location
                from locations, current_user_details
                  where locations.listed_in_city = current_user_details.location
            )
            SELECT *
            from restaurants LEFT OUTER JOIN locs
              on restaurants.location = locs.location
            ORDER BY restaurants.votes desc
            LIMIT 25
        """
        )
        rows = cur.fetchall()
        return render_template("base.html", rows = rows)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/locations", methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        loc = request.form.get('loc_Id')
        #city = request.form.get('City')
        cur.execute(
        """
            SELECT *  FROM RESTAURANTS
            where location = \'{}\'
            LIMIT 25
        """.format(loc)
        )
        rows = cur.fetchall()
        # return format(loc)
        return render_template("base.html", rows=rows)


@app.route("/restaurants", methods=['GET', 'POST'])
def rests():
    if request.method == 'POST':
        rest = request.form.get('restaurant')
        cur.execute(
        """
            SELECT *  FROM restaurants
            where restaurants.name =\'{}\'
            LIMIT 25
        """.format(rest)
        )
        rows = cur.fetchall()
        # return format(loc)
        return render_template("base.html", rows=rows)

# @app.route("/restaurants", methods=['GET', 'POST'])
# def restaurantSearch():
#     if request.method == 'POST':
#         rest = request.form.get('Rest_Id')          #Change the name
#         cur.execute(
#             """
#                 SELECT dish_liked
#                 FROM dishes, restaurants, rest_dish_links
#                 WHERE rest_dish_links.rest_id = restaurants.restaurant_id
#                     AND restaurants.name = \'{}\'
#                     AND rest_dish_links.dish_id = dishes.dish_id
#                 order by dish_liked asc;
#             """.format(rest)
#             )
#         rows = cur.fetchall()
#
#         return render_template("base.html", rows=rows)
if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
