from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from itertools import zip_longest
import pymysql.cursors
import json
import cryptography

app = Flask(__name__)

# MySQL configurations
app.config['APP_HOST'] = 'localhost'
app.config['DB_USER'] = 'kill'
app.config['DB_PASSWORD'] = '1'
app.config['APP_DB'] = 'CrimeTracker2023'
app.config['CHARSET'] = 'utf8mb4'
app.config['SECRET_KEY'] = 'IwantToKillMyself'

# mysql = MySQL(app)

conn = pymysql.connect(host=app.config['APP_HOST'],
                        user=app.config['DB_USER'],
                        port = 8889,
                        password=app.config['DB_PASSWORD'],
                        db=app.config['APP_DB'],
                        charset=app.config['CHARSET'],
                        cursorclass = pymysql.cursors.DictCursor)


def check():
    cursor = conn.cursor()
    cursor.execute(f''' SELECT * FROM CrimeTracker2023.Criminal;''')
    vals = cursor.fetchall()
    print(json.dumps(vals, indent=4, default = str))
    cursor.close()
    return json.dumps(vals, indent=4, default = str)

# def check_db_connection():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT DATABASE()")
#     result = cur.fetchone()
#     if result:
#         print("Database connected successfully!")
#     else:
#         print("Failed to connect to database!")


@app.context_processor
def utility_processor():
    def my_zip_longest(*args, **kwargs):
        return zip_longest(*args, **kwargs, fillvalue='')
    return dict(zip_longest=my_zip_longest)

# PAGE RENDERERS
@app.route('/')
def index():
    # check_db_connection()  # Call the check_db_connection function before running the route function
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('registration.html')

@app.route('/criminal')
def criminal():
    cur = conn.cursor()
    cur.execute("SELECT criminal_ID, cr_last, cr_first, cr_city, cr_state FROM Criminal")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return render_template('criminal.html', data=data, columns=columns)



@app.route('/crime')
def crime():
    cur = conn.cursor()
    cur.execute("SELECT * FROM Crime")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return render_template('crime.html', data=data, columns=columns)

@app.route('/officer')
def officer():
    cur = conn.cursor()
    cur.execute("SELECT * FROM Officer")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return render_template('officer.html', data=data, columns=columns)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/details')
def details():
    card_id = request.args.get('id')
    # Use the card ID to fetch the data for the selected card
    cur = conn.cursor()
    cur.execute("SELECT * FROM Criminal WHERE criminal_ID = %s", (card_id,))
    que = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

 # Make another select query
    cur.execute("SELECT alias FROM Alias WHERE criminal_ID = %s", (card_id,))
    que2 = cur.fetchall()
    columns2 = [desc[0] for desc in cur.description]

    # All crimes commited by criminal
    cur.execute("SELECT sentence_ID, type, prob_ID, start_date, end_date, violations FROM Sentences WHERE criminal_ID = %s", (card_id,))
    que3 = cur.fetchall()
    columns3 = [desc[0] for desc in cur.description]

    # All APPEALS FILED by criminal
    cur.execute("SELECT a.appeal_ID, a.crime_ID, a.filing_date, a.hearing_date, a.a_status FROM Appeal a, Crime c, Criminal cr WHERE c.criminal_ID = %s AND a.crime_ID = c.crime_ID AND cr.criminal_ID = c.criminal_ID", (card_id,))
    que4 = cur.fetchall()
    columns4 = [desc[0] for desc in cur.description]

    return render_template('details.html', data_for_selected_card=card_id, data=que, columns=columns, data2=que2, columns2=columns2, data3=que3, columns3=columns3, data4=que4, columns4=columns4)


@app.route('/crimeSelected')
def crimeSelected():
    card_id = request.args.get('id')
    # Use the card ID to fetch the data for the selected card
    cur = conn.cursor()
    cur.execute("SELECT * FROM Crime WHERE crime_ID = %s", (card_id,))
    que = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    cur.execute("SELECT * FROM Crime_charges cr, Crime_codes cc WHERE crime_ID = %s AND cr.crime_code = cc.crime_code", (card_id,))
    que2 = cur.fetchall()
    columns2 = [desc[0] for desc in cur.description]

    cur.execute("SELECT DISTINCT cr_first, cr_last, cr.criminal_id FROM Criminal cr, Crime c, Crime_charges cc WHERE c.crime_ID = %s AND cc.crime_ID = c.crime_ID AND cr.criminal_ID = c.criminal_ID", (card_id,))
    que3 = cur.fetchall()
    columns3 = [desc[0] for desc in cur.description]

    cur.execute("SELECT o_first, o_last, o.officer_ID FROM Officer o, Crime c, Crime_Officer co WHERE c.crime_ID = %s AND co.crime_ID = c.crime_ID AND co.officer_ID = o.officer_ID;", (card_id,))
    que4 = cur.fetchall()
    columns4 = [desc[0] for desc in cur.description]

    return render_template('crimeSelected.html', data_for_selected_card=card_id, data=que, columns=columns, data2=que2, columns2=columns2, data3 = que3, columns3 = columns3, data4=que4, columns4=columns4)

@app.route('/officerSelected')
def officerSelected():
    card_id = request.args.get('id')
    # Use the card ID to fetch the data for the selected card
    cur = conn.cursor()
    cur.execute("SELECT * FROM Officer WHERE officer_ID = %s", (card_id,))
    que = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    cur = conn.cursor()
    cur.execute("SELECT c.crime_ID, date_charged, hearing_date, appeal_cut_date FROM Crime c, Crime_officer co WHERE co.officer_ID = %s AND c.crime_ID = co.crime_ID", (card_id,))
    que2 = cur.fetchall()
    columns2 = [desc[0] for desc in cur.description]

    return render_template('officerSelected.html', data_for_selected_card=card_id, data=que, columns=columns, data2=que2, columns2=columns2)



# ADD / DELETE QUERIES
@app.route('/add', methods=['POST'])
def add():
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['createEmail']
    password = request.form['pwd']
    cur = conn.cursor()
    # check_db_connection()  # Call the check_db_connection function before executing the SQL query
    cur.execute("INSERT INTO users (firstname, lastname, user_email, password) VALUES (%s, %s, %s, %s)", (fname, lname, email, password))
    conn.commit()
    cur.close()
    return redirect(url_for('index'))


# SELECT QUERIES
@app.route("/catselect", methods=["POST"])
def catselect():
    category = request.form["category"]
    return redirect(url_for(category))

@app.route('/authenticate', methods=['POST'])
def authenticate():
    uemail = request.form['InputEmail'];
    upass = request.form['passwordIn'];
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_email = %s AND password = %s", (uemail, upass))
    result = cur.fetchone()
    cur.close()
    if result is None:
        # If the user does not exist or the password is incorrect, show an error message and redirect back to the login page
        flash('Invalid email or password')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
