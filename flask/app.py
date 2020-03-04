from flask import Flask, render_template, redirect, request, session, url_for
# from flask.session import Session
import psycopg2
import datetime as dt
# import sys
# reload(sys)
# sys.setdefaultencoding('UTF8')
# Connect to the database
db = 'host=127.0.0.1  dbname=group_30 user=group_30 password=776-302-579'
conn = psycopg2.connect(db)
cur = conn.cursor()

app = Flask(__name__)
app.secret_key = "abc"
@app.route("/")
def root():
    if session.get('username') != None:
        print(session['username'])
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
                SELECT restaurant_id,Name,rest_type,address,phone,rate_5
                from restaurants INNER JOIN locs
                  on restaurants.location = locs.location
                ORDER BY restaurants.rate_5 desc
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
                SELECT restaurant_id,Name,rest_type,address,phone,rate_5
                from restaurants INNER JOIN locs
                  on restaurants.location = locs.location
                ORDER BY restaurants.rate_5 desc
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
        except Exception as e:
            print(e)
            conn.commit()
            cur.execute(
            """
                SELECT * from cities;
            """
            )
            result = cur.fetchall()
            return render_template('register.html', message="Unable to register. Please try again!", locations=result)
    else:
        cur.execute(
            """
                SELECT * from cities;
            """
            )
        result = cur.fetchall()
        return render_template('register.html', message="", locations=result)

@app.route("/userpage")
def userpage():
    cur.execute(
        """
            select username, first_name, last_name, email_id, gender, location, ph_no, dob from active_users
            where username = \'{}\';
        """.format(session['username'])
        )
    rows = cur.fetchall()
    cur.execute(
            """
                SELECT * from cities;
            """
            )
    locations = cur.fetchall()
    rows = list(rows)
    rows[0] = list(rows[0])
    rows[0][-1] = rows[0][-1].strftime("%d-%m-%Y")
    rows[0] = tuple(rows[0])
    rows = tuple(rows)
    cur.execute(
        """
            SELECT restaurants.name, dishes.dish_liked, price, cart_data.count, price*cart_data.count, restaurants.restaurant_id
            FROM cart_data, restaurants, dishes, rest_dish_links
            WHERE rest_dish_links.link_id = cart_data.item_id
                AND cart_data.username = \'{}\'
                AND rest_dish_links.rest_id = restaurants.restaurant_id
                AND rest_dish_links.dish_id = dishes.dish_id;
        """.format(session['username'])
        )
    cart = cur.fetchall()
    cur.execute(
        """
            SELECT restaurants.name, dishes.dish_liked, price, orders.count, price*orders.count, orders.order_time, restaurants.restaurant_id
            FROM orders, restaurants, dishes, rest_dish_links
            WHERE rest_dish_links.link_id = orders.item_id
                AND orders.username = \'{}\'
                AND rest_dish_links.rest_id = restaurants.restaurant_id
                AND rest_dish_links.dish_id = dishes.dish_id
            ORDER BY orders.order_time desc;
        """.format(session['username'])
        )
    orders = cur.fetchall()
    temp = []
    for i in orders:
        temp.append(list(i))
    for i in range(len(temp)):
       temp[i][-2] = temp[i][-2].strftime("%H:%M %d-%m-%Y")
       temp[i] = tuple(temp[i])
    orders = tuple(temp)
    
    cur.execute(
        """SELECT distinct(restaurants.name), restaurants.restaurant_id, sum(price*count)
            FROM cart_data, restaurants, dishes, rest_dish_links
            WHERE rest_dish_links.link_id = cart_data.item_id
                AND cart_data.username = \'{}\'
                AND rest_dish_links.rest_id = restaurants.restaurant_id
                AND rest_dish_links.dish_id = dishes.dish_id
            group by restaurants.name, restaurants.restaurant_id;
        """.format(session['username'])
        )
    todo=cur.fetchall()
        
    #return redirect(url_for('userpage'))
    return render_template("userPage.html", message=rows, cart=cart, orders=orders, locations=locations,todo=todo)
    # return render_template("userPage.html", message=rows, cart=cart, orders=orders, locations=locations)


@app.route("/locations", methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        loc = request.form.get('loc_Id').lower()
        #city = request.form.get('City')
        cur.execute(
        """
            SELECT name, address, rate_5, approx_cost_for_two, restaurant_id  FROM RESTAURANTS
            where location = \'{}\'
            order by rate_5 desc
        """.format(loc)
        )
        rows = cur.fetchall()
        # return format(loc)
        return render_template("locationsearch.html", rows=rows)

# @app.route("/restaurants", methods=['GET', 'POST'])
# def rests():
#     if request.method == 'POST':
#         rest = request.form.get('restaurant').lower()
#         cur.execute(
#         """
#             SELECT *  FROM restaurants
#             where restaurants.name =\'{}\'
#             LIMIT 25
#         """.format(rest)
#         )
#         rows = cur.fetchall()
#         # return format(loc)
#         return render_template("base.html", rows=rows)

@app.route("/<restaurant_id>/dishrestaurant",methods=['GET', 'POST'])
def dishrestaurant(restaurant_id):
    if request.method == 'POST':
        # rest_=request.form.get("rest").lower()
        cur.execute(
        """
            with temp_1 As
            (
                SELECT rest_dish_links.dish_id as id, rest_dish_links.price as price
                FROM restaurants INNER JOIN rest_dish_links ON restaurants.restaurant_id = rest_dish_links.rest_id
                where restaurants.restaurant_id = \'{}\'
            )
            select dish_liked, price
            from temp_1 INNER JOIN dishes ON dishes.dish_id = temp_1.id
        """.format(restaurant_id)
           )
        rows = cur.fetchall()
    return render_template("dishrestaurant.html",rows=rows, rest_name=restaurant_id)

@app.route("/updatelocation", methods=['POST'])
def loc_update():
    if request.method == 'POST':
        loc = request.form['location']
        cur.execute(
            """
                select update_user_loc(\'{}\', \'{}\');
            """.format(session['username'], loc)
            )
        return redirect(url_for('userpage'))
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
                   SELECT update_cart(\'{}\',
                    (
                        SELECT link_id(\'{}\', \'{}\')
                    ),
                    \'{}\');
    			""".format(session['username'], rest_id, i.lower(), temp[i])
                )
            conn.commit()
        return render_template("cart.html",result = temp, restid=rest_id)

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
                
                   select ordering(\'{}\', link_id(\'{}\', \'{}\'), {});
    			""".format(session['username'], name, i.lower(), temp[i])
                )
            # print(temp[i].lower(), session['username'], rest_name.lower(), i.lower())
                conn.commit()
        return redirect(url_for('home'))
    else:
        cur.execute("""
            select item_id,count 
            from cart_data, rest_dish_links
            where cart_data.item_id=rest_dish_links.link_id and rest_dish_links.rest_id={}
            """.format(name)
            )
        temp=cur.fetchall()
        for i in temp:
            cur.execute(
                """
                select ordering(\'{}\',{},{});
                """.format(session['username'],i[0],i[1])
                )
            conn.commit()
        return redirect(url_for('userpage'))
    
@app.route("/removeitem/<rest_id>/<dish_name>")
def removeitem(rest_id, dish_name):
        cur.execute(
            """
                select update_cart(\'{}\', link_id(\'{}\', \'{}\'), 0);
            """.format( session['username'], rest_id, dish_name)
            )
        conn.commit()
        return redirect(url_for('userpage'))

@app.route("/search",methods=['GET','POST'])
def search():
    if request.method == 'POST':
        text = request.form.get('search').lower()
        mode = request.form.get('searchby').lower()
        order = request.form.get('orderby').lower()
        fil = request.form.get('filter').lower()
        lim=1000
        if order=='true':
            if mode == '1':
                cur.execute(
				"""
                    select restaurant_id,Name,rest_type,address, phone,rate_5 from restaurants where  name=\'{}\' order by {} DESC limit {}
				""".format(text,fil,lim)
				)
            else:
                cur.execute(
    				"""
                        select restaurant_id,s.Name,s.rest_type,s.address, s.phone_number,s.rating_5 from search_rests({},\'{}\',\'{}\',{},{}) as s inner join restaurants on restaurants.name=s.Name and restaurants.address=s.address order by {} DESC
    				""".format(mode,text,fil,order,lim, fil)
    				)
        else :
            if mode == '1':
                cur.execute(
				"""
                    select restaurant_id,Name,rest_type,address, phone,rate_5 from restaurants where  name=\'{}\' order by {} limit {}
				""".format(text,fil,lim)
				)
            else:
                cur.execute(
    				"""
    				select restaurant_id,s.Name,s.rest_type,s.address, s.phone_number,s.rating_5 from search_rests({},\'{}\',\'{}\',{},{}) as s inner join restaurants on restaurants.name=s.Name and restaurants.address=s.address order by {}
                    """.format(mode,text,fil,order,lim, fil) 
    				)
        rows=cur.fetchall()
        #y=[x[0] for x in rows]
        #y=[]
        #for x in rows:
        #	y.append(list(x))
#        rows = list(rows)
#        for i in range(len(rows)):
#    		rows[i]=list(rows[i])

#    	for i in range(len(rows)):
    		#rows[i]=list(rows[i])
#    		for j in range(len(rows[i])):
#    			rows[i][j]=str(rows[i][j])
    		#rows[i]=tuple(rows[i])

#    	for i in range(len(rows)):
#    		rows[i]=tuple(rows[i])
#    	rows = tuple(rows)
    return render_template("search.html",messages=rows)

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
    app.run(host="localhost", port=5002, debug=True)
