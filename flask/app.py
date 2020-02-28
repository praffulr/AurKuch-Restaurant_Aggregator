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

@app.route("/logout")
def logout():
    try:
        cur.execute(
            """
                DELETE FROM active_users
                WHERE username = \'{}\';
            """.format(session['username'])
            )
        conn.commit()
        session.pop('username', None)
        return render_template("users.html", message="logged out successfully")
    except:
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
            try:
                cur.execute(
                """
                    INSERT INTO active_users(first_name, last_name, email_id, gender, location, password, username, ph_no, dob, login_time)
                    SELECT first_name, last_name, email_id, gender, location, password, username, ph_no, dob, \'{}\' FROM users
                    WHERE username=\'{}\';
                """.format(dt.datetime.now(), username)
                )
            except:
                conn.commit()
                pass
            cur.execute(
            """
                WITH locs as
                (
                    select distinct(locations.location) as location
                    from locations, active_users
                      where locations.listed_in_city = active_users.location AND active_users.username = \'{}\'
                )
                SELECT name
                from restaurants INNER JOIN locs
                  on restaurants.location = locs.location
                ORDER BY restaurants.votes desc
                LIMIT 25;
            """.format(session['username'])
            )
            rows = cur.fetchall()
            conn.commit()
            return render_template("base.html", rows = rows)
        return render_template("users.html", message="Invalid Username or Password")
    else:
        try:
            cur.execute(
            """
                WITH locs as
                (
                    select distinct(locations.location) as location
                    from locations, active_users
                      where locations.listed_in_city = active_users.location AND active_users.username = \'{}\'
                )
                SELECT name
                from restaurants INNER JOIN locs
                  on restaurants.location = locs.location
                ORDER BY restaurants.votes desc
                LIMIT 25;
            """.format(session['username'])
            )
            rows = cur.fetchall()
            conn.commit()
            return render_template("base.html", rows = rows)
        except :
            conn.commit()
            return render_template("users.html", message="")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastame = request.form['lastname']
            emailid = request.form['emailid']
            gender = request.form['gender']
            location = request.form['location'].lower()
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
            select username, first_name, last_name, email_id, gender, location, ph_no, dob from active_users
            where username = \'{}\';
        """.format(session['username'])
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
        loc = request.form.get('loc_Id').lower()
        #city = request.form.get('City')
        cur.execute(
        """
            SELECT name, address, rate_5, approx_cost_for_two, restaurant_id  FROM RESTAURANTS
            where location = \'{}\'
        """.format(loc)
        )
        rows = cur.fetchall()
        # return format(loc)
        return render_template("locationsearch.html", rows=rows)

@app.route("/restaurants", methods=['GET', 'POST'])
def rests():
    if request.method == 'POST':
        rest = request.form.get('restaurant').lower()
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

@app.route("/<restaurant_id>/dishrestaurant",methods=['GET', 'POST'])
def dishrestaurant(restaurant_id):
    if request.method == 'POST':
        # rest_=request.form.get("rest").lower()
        cur.execute(
        """
            with temp_1 As
            (
                SELECT rest_dish_links.dish_id as id
                FROM restaurants INNER JOIN rest_dish_links ON restaurants.restaurant_id = rest_dish_links.rest_id
                where restaurants.restaurant_id = \'{}\'
            )
            select dish_liked
            from temp_1 INNER JOIN dishes ON dishes.dish_id = temp_1.id
        """.format(restaurant_id)
           )
        rows = cur.fetchall()
    return render_template("dishrestaurant.html",rows=rows, rest_name=restaurant_id)

@app.route("/<rest_id>/cart",methods=['GET','POST'])
def cart(rest_id):
    if request.method == 'POST':
        result = request.form
        temp = {}
        for i in result.keys():
            if result[i] != '0':
                temp[i] = result[i]
        for i in temp.keys():
            print(temp[i].lower(), session['username'], rest_id.lower(), i.lower())
            cur.execute(
    			"""
                   INSERT INTO cart_data(username, item_id, count)
                   SELECT active_users.username, rest_dish_links.link_id as item_id, \'{}\' as count
                   FROM active_users, rest_dish_links, restaurants, dishes
                   WHERE active_users.username = \'{}\'
                       AND rest_dish_links.rest_id = \'{}\'
                       AND rest_dish_links.dish_id = dishes.dish_id
                       AND dishes.dish_liked = \'{}\';
    			""".format(temp[i].lower(), session['username'], rest_id.lower(), i.lower())
                )
            conn.commit()
        return render_template("cart.html",result = temp)

@app.route("/<name>/order",methods=['GET','POST'])
def order(name):
    if request.method == 'POST':
        res = request.form
        temp = {}
        for i in res.keys():
            if res[i] != "order":
                temp[i] = res[i]
            cur.execute(
    			"""
                   INSERT INTO orders(order_time, username, item_id, count)
                   SELECT active_users.username, rest_dish_links.link_id as item_id, \'{}\' as count
                   FROM active_users, rest_dish_links, restaurants, dishes
                   WHERE active_users.username = \'{}\'
                       AND rest_dish_links.rest_id = \'{}\'
                       AND rest_dish_links.dish_id = dishes.dish_id
                       AND dishes.dish_liked = \'{}\';
    			""".format(temp[i].lower(), session['username'], name.lower(), i.lower())
                )
            # print(temp[i].lower(), session['username'], rest_name.lower(), i.lower())
            conn.commit()
        return render_template("order.html", result=temp)

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
