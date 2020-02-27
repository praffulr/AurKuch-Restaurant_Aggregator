from flask import Flask, render_template, redirect, request, session
# from flask.session import Session
import psycopg2
import datetime as dt
# import sys
# reload(sys)
# sys.setdefaultencoding('UTF8')
# Connect to the database
db = 'host=127.0.0.1  dbname=project user=admin password=admin'
conn = psycopg2.connect(db)
cur = conn.cursor()

app = Flask(__name__)
app.secret_key = "abc"
@app.route("/")
def root():
    if session.get('username') != None:
        return render_template("base.html")
    else:
        return render_template("users.html", message="")

@app.route("/homepage", methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':
        username = request.form.get("Username")
        password = request.form.get("Password")
        cur.execute(
            """
                SELECT * FROM users
                WHERE username=\'{}\' AND password=\'{}\';
            """.format(username, password)
            )
        if len(cur.fetchall()) > 0:
            session['username'] = username
            cur.execute(
            """
                CREATE VIEW current_user_details as
                select * from users
                where users.username = \'{}\' and users.password = \'{}\';
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
                SELECT name
                from restaurants INNER JOIN locs
                  on restaurants.location = locs.location
                ORDER BY restaurants.votes desc
                LIMIT 25;
            """
            )
            conn.commit()
            rows = cur.fetchall()
            return render_template("base.html", rows = rows)
        return render_template("users.html", message="Invalid Username or Password")
    else:
        try:
            cur.execute(
                """
                    WITH locs as
                    (
                        select distinct(locations.location) as location
                        from locations, current_user_details
                          where locations.listed_in_city = current_user_details.location
                    )
                    SELECT name
                    from restaurants INNER JOIN locs
                      on restaurants.location = locs.location
                    ORDER BY restaurants.votes desc
                    LIMIT 25;
                """
                )
            rows = cur.fetchall()
            return render_template("base.html", rows=rows)
        except :
            return render_template("users.html", message="")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastame = request.form['lastname']
            emailid = request.form['emailid']
            gender = request.form['gender']
            location = request.form['location']
            password = request.form['password']
            username = request.form['username']
            phonenum = request.form['phonenum']
            # print(type(request.form['dob']))
            dob = dt.datetime.strptime(request.form['dob'], "%Y-%m-%d")
            time = dt.datetime.now()
            cur.execute(
                """
                INSERT INTO users(first_name, last_name, email_id, gender, location, password, username, ph_no, dob, reg_time)
                VALUES
                    (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');
                """.format(firstname, lastame, emailid, gender, location, password, username, phonenum, dob, time)
                )
            conn.commit()
            return render_template('users.html')
        except:
            return render_template('register.html', message="Username might be taken (or) Invalid Credentials entered")
    else:
        return render_template('register.html', message="", )

@app.route("/userpage")
def userpage():
    cur.execute(
        """
            select username, first_name, last_name, email_id, gender, location, ph_no, dob from current_user_details;
        """
        )
    rows = cur.fetchall()
    rows = list(rows)
    rows[0] = list(rows[0])
    rows[0][-1] = rows[0][-1].strftime("%d-%m-%Y")
    rows[0] = tuple(rows[0])
    rows = tuple(rows)
    return render_template("userPage.html", message=rows)
    

@app.route("/locations", methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        loc = request.form.get('loc_Id')
        #city = request.form.get('City')
        cur.execute(
        """
            SELECT name  FROM RESTAURANTS
            where location = \'{}\'
        """.format(loc)
        )
        rows = cur.fetchall()
        # return format(loc)
        return render_template("locationsearch.html", rows=rows)

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

@app.route("/<name>/dishrestaurant",methods=['GET', 'POST'])
def dishrestaurant(name):
    if request.method == 'POST':
        searchdish=request.form.get("rest")
        cur.execute(
        """
            select dish_liked 
            from dishes, restaurants,rest_dish_links 
            where rest_id=restaurant_id and dishes.dish_id=rest_dish_links.link_id 
            and name=\'{}\'
        """.format(searchdish)
           )
        rows = cur.fetchall()
    return render_template("dishrestaurant.html",rows=rows, rest_name=name)

@app.route("/<rest_name>/cart",methods=['GET','POST'])
def cart(rest_name):
	if request.method == 'POST':
		result = request.form
		temp = {}
		for i in result.keys():
			if result[i] != '0':
				temp[i] = result[i]
#		for i in temp
#		cur.execute(
#			"""
#			""")
		return render_template("cart.html",result = temp)
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
