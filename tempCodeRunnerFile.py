@app.route("/form_login", methods=["POST", "GET"])
def login():
    
    
    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="login_info"
    )

    mycursor = mydb.cursor();

    name = request.form['username']
    passw = request.form['password']
    mycursor.execute("select * from main where Username= '"+name+"' and password = '"+passw+"'" )
    r = mycursor.fetchall()
    count = mycursor.rowcount
    if count == 1:
         return render_template("home.html", name = name) 
    else:
         return render_template("login.html", info= "Invalid Credentials")
    

    mycursor.commit()
    mycursor.close()