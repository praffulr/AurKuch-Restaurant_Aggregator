-----------------------------------------------------FLASK---------------------------------------------------

                                                              app.py

from flask import Flask, render_template, redirect

# Connect to the database
db = 'host=10.17.xx.xxx  dbname=test_0 user=test_0 password=NeverShareYourPassword'
conn = psycopg2.connect(db)
cur = conn.cursor()

app = Flask(__name__)


@app.route("/")
def root():
    cur.execute(
    """
        SELECT * FROM badges
        ORDER BY random()
        LIMIT 25
    """)
    rows = cur.fetchall()

    return render_template("base.html", rows=rows)


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)



---------------------------------------------------------------------------------------------------------



Base.html uses *rows*  returned from flask to create a HTML table with the result

-----------------------------------------------Base.html----------------------------------------------



        <div class="container">
            <h2 class="mt-5 ">Info of Badges</h1>
            <p class="lead">Showing the results of: SELECT * FROM badges ORDER BY random() LIMIT 25</p>


            <table class="mt-5 table table-bordered">
                <thead>
                    <tr>
                        <th scope="col">id</th>
                        <th scope="col">name</th>
                        <th scope="col">userID</th>
                        <th scope="col">date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td scope="row">{{row[0]}}</td>
                        <td scope="row">{{row[1]}}</td>
                        <td scope="row">{{row[2]}}</td>
                        <td scope="row">{{row[3]}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

        </div>

---------------------------------------------------------------------------------------------------------------
