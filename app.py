from flask import Flask, request, render_template, session
import csv
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = 'SPORTSMANAGEMENTDATA'
@app.route("/")
def firstpage():
    return render_template("login.html")

@app.route("/home", methods=["POST", "GET"])
def login():

    if request.method == 'GET':
        return render_template("homepage.html")

    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="faculty_info"
    )
        
    mycursor = mydb.cursor();

#     global name
    name = request.form['username']
    passw = request.form['password']


    mycursor.execute("select * from main where Username= '"+name+"' and password = '"+passw+"'" )
    r = mycursor.fetchall()
    count = mycursor.rowcount
    if count == 1:
        return render_template("homepage.html", name = name)
    else:
         return render_template("login.html", info= "Invalid Credentials")
    mycursor.commit()
    mycursor.close()


@app.route("/issueItem", methods=["POST", "GET"])
def issued():
    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="issue_return"
    )

    sdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="student_info"
    )

    invdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="inventory_info"
    )

    mycursor = mydb.cursor();
    mycursor2 = sdb.cursor(); #cursor to student INFO
    mycursor3 = invdb.cursor(); #cursor to inventory INFO

    query1 = "SELECT ITEMID FROM MAIN ORDER BY ITEMID"
    mycursor3.execute(query1)
    itemids = [row[0] for row in mycursor3.fetchall()]

    query2 = "SELECT SPORTSNAME FROM MAIN ORDER BY ITEMID"
    mycursor3.execute(query2)
    sportsnames = [row[0] for row in mycursor3.fetchall()]
    # itemid = mycursor3.fetchall()

    if request.method == 'POST':
        dictt = request.form.to_dict()
        a = dictt["studentid"]
        b = dictt["itemid"]
        c= dictt["sportsname"]

        mycursor2.execute("select * from main where SID= '"+a+"'" )
        r1 = mycursor2.fetchall()
        count1 = mycursor2.rowcount
        # mycursor.execute("insert into main(ID,SID,SCODE) values(%s,%s,%s))",(a,b,c))
        mycursor3.execute("select * from main where ITEMID= '"+b+"' and SPORTSNAME='"+c+"'" )
        r2 = mycursor3.fetchall()
        count2 = mycursor3.rowcount

        status1 = "ISSUED"
        status2 = "RETURNED"
        mycursor.execute("select * from main where SID= '"+a+"' and STATUS = '"+status1+"'" )
        x1 = mycursor.fetchall()
        issueCount = mycursor.rowcount
        mycursor.execute("select * from main where SID= '"+a+"' and STATUS = '"+status2+"'" )
        x2 = mycursor.fetchall()
        returnCount = mycursor.rowcount

        # Flow ->->
        # STUDENT VALIDATION
        # ITEM VALIDATION
        # QUANTITY CHECK
        # UPDATE
        #
        if count1>0 and count2>0: #STudent id and ITEm ID exists
            #INVENTORY QUANTITY DECREMENT
            mycursor3.execute("select QUANTITY from main where ITEMID= '"+b+"' and SPORTSNAME='"+c+"'" )
            x = list(mycursor3.fetchone())
            quantity = int(x[0])


            mycursor2.execute("select DUE from main where SID='"+a+"'")
            x = list(mycursor2.fetchone())
            dues = int(x[0])



            if dues>0:
                return render_template("issueItem.html", info="CLEAR DUE AND RETURN THE {} ITEM".format(itemid), itemids=itemids, sportsnames = sportsnames)

            if quantity>0:
                quantity = str(quantity - 1)
                mycursor3.execute("update main set QUANTITY = '"+quantity+"'  where ITEMID= '"+b+"' and SPORTSNAME='"+c+"'")
            else:
                return render_template("issueItem.html", info="ITEM NOT AVAILABLE", itemids=itemids, sportsnames = sportsnames)

            #
            if issueCount==returnCount:
                status = "ISSUED"
                now = datetime.datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")
                mycursor.execute("insert into main(SID,ITEMID,SPORTSNAME,STATUS,DATE,TIME) values('"+a+"','"+b+"','"+c+"','"+status+"','"+current_date+"','"+current_time+"')")
                mydb.commit()
                mycursor.close()
                sdb.commit()
                mycursor2.close()
                invdb.commit()
                mycursor3.close()
                return render_template("issueItem.html", info="ITEM ISSUED SUCCESSFULLY", itemid = b, itemids=itemids, sportsnames = sportsnames)
            else:
                #checking which item was already issued
                mycursor.execute("select ITEMID from main where SID= '"+a+"'" )
                x = list(mycursor.fetchone())
                itemid= x[0]
                return render_template("issueItem.html", info="ITEM ALREADY ISSUED ON THIS ID", itemid=itemid, itemids=itemids, sportsnames = sportsnames)
        else:
            if count1<0 or count1==0:
                return render_template("issueItem.html", info="STUDENT INFO DOESN'T EXIST", itemids=itemids, sportsnames = sportsnames)
            # elif count2<0 or count2==0:
            else:
                return render_template("issueItem.html", info="ITEM INFO DOESN'T EXIST", itemids=itemids, sportsnames = sportsnames)
    return render_template("issueItem.html", itemids=itemids, sportsnames = sportsnames)

@app.route("/returnItem", methods=["POST", "GET"])
def returnItem():

    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="issue_return"
    )

    sdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="student_info"
    )

    invdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="inventory_info"
    )

    mycursor = mydb.cursor();
    mycursor2 = sdb.cursor(); #cursor to student INFO
    mycursor3 = invdb.cursor(); #cursor to inventory INFO

    query1 = "SELECT ITEMID FROM MAIN ORDER BY ITEMID"
    mycursor3.execute(query1)
    itemids = [row[0] for row in mycursor3.fetchall()]

    query2 = "SELECT SPORTSNAME FROM MAIN ORDER BY ITEMID"
    mycursor3.execute(query2)
    sportsnames = [row[0] for row in mycursor3.fetchall()]
    # Post method and the declaration of connections are the default ones#
    if request.method == 'POST':
        dictt = request.form.to_dict()
        a = dictt["studentid"]
        b = dictt["itemid"]
        c = dictt["sportsname"]

        session['sid'] = a
        session['itemid'] = b
        session['sportsname'] = c

        mycursor2.execute("select * from main where SID= '"+a+"'" )
        r1 = mycursor2.fetchall()
        count1 = mycursor2.rowcount
        # mycursor.execute("insert into main(ID,SID,SCODE) values(%s,%s,%s))",(a,b,c))
        mycursor3.execute("select * from main where ITEMID = '"+b+"' and SPORTSNAME='"+c+"'")
        r2 = mycursor3.fetchall()
        count2 = mycursor3.rowcount

        status1 = "ISSUED"
        status2 = "RETURNED"
        mycursor.execute("select * from main where SID= '"+a+"' and STATUS = '"+status1+"' " )
        x1 = mycursor.fetchall()
        issueCount = mycursor.rowcount
        mycursor.execute("select * from main where SID= '"+a+"' and STATUS = '"+status2+"' " )
        x2 = mycursor.fetchall()
        returnCount = mycursor.rowcount

        # Flow ->->
        # STUDENT VALIDATION
        # ITEM VALIDATION
        # QUANTITY CHECK
        # UPDATE
        #


        if count1>0 and count2>0: #STudent id and ITEm ID exists
            #INVENTORY QUANTITY DECREMENT

            #
            if issueCount>returnCount:

                #Retrieving the last issued item from database, irrespective of the input.
                mycursor.execute("SELECT ITEMID FROM main where SID='"+a+"' ORDER BY SID DESC LIMIT 1")
                issuedItem = mycursor.fetchone()[0]

                if(issuedItem!=b):
                    return render_template("returnItem.html", info="{m} ALREADY ISSUED. {n} CAN'T BE RETURNED".format(m=issuedItem, n=b), itemids=itemids, sportsnames = sportsnames)

                mycursor2.execute("select DUE from main where SID='"+a+"'")
                x = list(mycursor2.fetchone())
                dues = int(x[0])

                if dues>0:
                    mycursor3.execute("select QUANTITY from main where ITEMID= '"+b+"' and SPORTSNAME='"+c+"'" )
                    x = list(mycursor3.fetchone())
                    quantity = int(x[0])
                    #
                    mycursor.execute("SELECT DATE FROM main where SID='"+a+"' and ITEMID='"+b+"' and SPORTSNAME='"+c+"'")
                    results = mycursor.fetchall()

                    for result in results:
                        year = result[0].year
                        month = result[0].month
                        day = result[0].day

                    current_date = datetime.datetime.now()
                    given_date = datetime.datetime(year, month, day)

                    difference = current_date - given_date
                    difference_in_days = abs(difference.days)


                    flag= False
                    if difference_in_days>0:
                        flag = True
                        calculated_due = 100*difference_in_days
                        now  = datetime.datetime.now()
                        date = now.date()
                        return render_template("returnItem.html", flag=flag, calculated_due=calculated_due, current_date=date, itemids=itemids, sportsnames = sportsnames)


                mycursor3.execute("select QUANTITY from main where ITEMID= '"+b+"' and SPORTSNAME='"+c+"' " )
                x = list(mycursor3.fetchone())
                quantity = int(x[0])
                quantity = str(quantity + 1)
                mycursor3.execute("update main set QUANTITY = '"+quantity+"'  where ITEMID= '"+b+"' and SPORTSNAME='"+c+"'")

                status = "RETURNED"
                now = datetime.datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")
                mycursor.execute("insert into main(SID,ITEMID,SPORTSNAME,STATUS,DATE,TIME) values('"+a+"','"+b+"','"+c+"','"+status+"','"+current_date+"','"+current_time+"')")
                mydb.commit()
                mycursor.close()
                sdb.commit()
                mycursor2.close()
                invdb.commit()
                mycursor3.close()
                return render_template("returnItem.html", info="ITEM RETURNED SUCCESSFULLY", itemid=b, itemids=itemids, sportsnames = sportsnames)
            else:
                return render_template("returnItem.html", info="NO ITEMS ISSUED ON THIS ID", itemids=itemids, sportsnames = sportsnames)
        else:
            if count1<0 or count1==0:
                return render_template("returnItem.html", info="STUDENT INFO DOESN'T EXIST", itemids=itemids, sportsnames = sportsnames)
            # elif count2<0 or count2==0:
            else:
                return render_template("returnItem.html", info="ITEM INFO DOESN'T EXIST", itemids=itemids, sportsnames = sportsnames)
    return render_template("returnItem.html", itemids=itemids, sportsnames = sportsnames)

@app.route("/returned", methods=['GET', 'POST'])
def returned():

    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="issue_return"
    )

    sdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="student_info"
    )

    invdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="inventory_info"
    )

    mycursor = mydb.cursor();
    mycursor2 = sdb.cursor();   #cursor to student INFO
    mycursor3 = invdb.cursor();   #cursor to inventory INFO

    if request.method =='POST':
        sid = session.get('sid')
        itemid = session.get('itemid')
        sportsname = session.get('sportsname')
        calculatedDue = 0

        #checking which item was already issued
        mycursor.execute("select ITEMID from main where SID= '"+sid+"' and SPORTSNAME='"+sportsname+"'" )
        x = mycursor.fetchall()
        print(x)
        # itemid= x[0]

        mycursor.close()
        #passing to the second query
        # while mycursor.nextset():
        #     pass
        mycursor = mydb.cursor();
        mycursor3.execute("select QUANTITY from main where ITEMID= '"+itemid+"' and SPORTSNAME='"+sportsname+"'" )
        x = list(mycursor3.fetchone())
        quantity = int(x[0])

        mycursor2.execute("update main set DUE='"+str(calculatedDue)+"' where SID='"+sid+"'")

        quantity = str(quantity + 1)
        mycursor3.execute("update main set QUANTITY = '"+quantity+"'  where ITEMID= '"+itemid+"' and SPORTSNAME='"+sportsname+"'")

        status = "RETURNED"
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        #second query
        mycursor.execute("insert into main(SID,ITEMID,SPORTSNAME,STATUS,DATE,TIME) values('"+sid+"','"+itemid+"','"+sportsname+"','"+status+"','"+current_date+"','"+current_time+"')")
        mydb.commit()
        mycursor.close()
        sdb.commit()
        mycursor2.close()
        invdb.commit()
        mycursor3.close()
        booldues = True

        return render_template("returnItem.html", booldues = booldues, info="DUE CLEARED AND {id} ITEM RETURNED SUCCESSFULLY".format(id=itemid))

@app.route("/reportgeneration")
def reportGeneration():

    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="issue_return" # SID ITEMID SPORTSNAME STATUS DATE TIME
    )

    sdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="student_info" # SID NAME COURSE YEAR
    )

    mycursor2 = sdb.cursor();
    mycursor3 = mydb.cursor();

    query = '''
        SELECT main.SID, main2.NAME, main2.COURSE, main2.YEAR, main.ITEMID, main.SPORTSNAME, main.STATUS, main.DATE, main.TIME
        FROM issue_return.main AS main
        INNER JOIN student_info.main AS main2
        ON main.SID = main2.SID ORDER BY main.DATE DESC, main.TIME DESC
    '''
    mycursor3.execute(query)
    records = mycursor3.fetchall()

    # mycursor3.execute("SELECT * FROM main")
    # records = mycursor3.fetchall()
    # mycursor2.execute("SELECT * FROM main")
    # records2 = mycursor2.fetchall()
    mydb.commit()
    mycursor3.close()
    return render_template("rGeneration.html", records=records)

@app.route("/inventory")
def inventory():

    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="inventory_info"
    )

    mycursor3 = mydb.cursor();

    mycursor3.execute("SELECT * FROM main where TOTALQUANTITY !=0")
    records = mycursor3.fetchall()

    mydb.commit()
    mycursor3.close()
    return render_template("inventory.html", records=records)


@app.route("/addItem", methods=["GET", "POST"])
def addItem():

    invdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="inventory_info"
    )

    mycursor3 = invdb.cursor(); #cursor to inventory INFO

    if request.method == 'POST':
        dictt = request.form.to_dict()
        a = dictt["sportsname"]
        b = dictt["itemid"]
        c= dictt["quantity"]

        mycursor3.execute("select * from main where ITEMID = '"+b+"' and SPORTSNAME='"+a+"'")
        r2 = mycursor3.fetchall()
        itemCount = mycursor3.rowcount
        if itemCount==0:
            mycursor3.execute("insert into main(SPORTSNAME,ITEMID,QUANTITY,TOTALQUANTITY) values('"+a+"','"+b+"','"+c+"','"+c+"')")
            invdb.commit()
            mycursor3.close()
            return render_template("addItem.html", info=" New Item '"+b+"' with quantity '"+c+"' added successfully under '"+a+"'.")
        elif itemCount>0:
            mycursor3.execute("select QUANTITY from main where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"' ")
            x = list(mycursor3.fetchone())
            quantity = int(x[0])
            givenQ = int(c)
            quantity = str(quantity + givenQ )
            mycursor3.execute("update main set TOTALQUANTITY = '"+quantity+"'  where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"'")
            mycursor3.execute("update main set QUANTITY = '"+quantity+"'  where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"'")
            invdb.commit()
            mycursor3.close()
            return render_template("addItem.html", info=" "+c+" '"+b+"' item added successfully under '"+a+"' category.")
        else:
            return render_template("addItem.html")

    return render_template("addItem.html")


@app.route("/deleteItem", methods=["GET", "POST"])
def deleteItem():

    invdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="inventory_info"
    )

    mycursor3 = invdb.cursor(); #cursor to inventory INFO

    query1 = "SELECT ITEMID FROM MAIN ORDER BY ITEMID"
    mycursor3.execute(query1)
    itemids = [row[0] for row in mycursor3.fetchall()]

    query2 = "SELECT SPORTSNAME FROM MAIN ORDER BY ITEMID"
    mycursor3.execute(query2)
    sportsnames = [row[0] for row in mycursor3.fetchall()]


    if request.method == 'POST':
        dictt = request.form.to_dict()
        a = dictt["sportsname"]
        b = dictt["itemid"]
        c= dictt["quantity"]

        mycursor3.execute("select * from main where ITEMID = '"+b+"' and SPORTSNAME='"+a+"'")
        r2 = mycursor3.fetchall()
        itemCount = mycursor3.rowcount
        if itemCount==0:
            # mycursor3.execute("insert into main(SPORTSNAME,ITEMID,QUANTITY) values('"+a+"','"+b+"','"+c+"')")
            # invdb.commit()
            # mycursor3.close()
            return render_template("deleteItem.html", info="No item exists to delete.")
        elif itemCount>0:

            #jab saare delete karne ho
            # mycursor3.execute("select TOTALQUANTITY from main where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"' ")


            #jab available hi delete karne ho
            mycursor3.execute("select QUANTITY from main where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"' ")
            x = list(mycursor3.fetchone())
            quantity = int(x[0])

            givenQ = int(c)
            checkDiff = quantity-givenQ

            if checkDiff>0:
                quantity = str(quantity - givenQ)
                mycursor3.execute("update main set QUANTITY = '"+quantity+"'  where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"'")
                mycursor3.execute("update main set TOTALQUANTITY = '"+quantity+"'  where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"'")
                invdb.commit()
                mycursor3.close()
                return render_template("deleteItem.html", info=" "+c+" '"+b+"' item deleted successfully under '"+a+"' category.")

            elif checkDiff==0:
                mycursor3.execute("delete from main where ITEMID= '"+b+"' and SPORTSNAME= '"+a+"'")
                invdb.commit()
                mycursor3.close()
                return render_template("deleteItem.html", info="Item Deleted Successfully.")
            else:
                return render_template("deleteItem.html", info="Invalid quantity, Try Again!")
        else:
            return render_template("deleteItem.html", itemids=itemids, sportsnames=sportsnames)

    return render_template("deleteItem.html", itemids=itemids, sportsnames=sportsnames)


@app.route("/addStudentData", methods=["GET", "POST"])
def addStudentData():
    sdb = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="student_info" # SID NAME COURSE YEAR DUE
    )

    mycursor2 = sdb.cursor();

    if request.method == 'POST':
        f = request.files['file']
        if f:
            f.save('sheets/' + f.filename)
            data =  csv.reader(open('sheets/{}'.format(f.filename)))
            for rows in data:
                mycursor2.execute("INSERT INTO MAIN(SID, NAME, COURSE, YEAR, DUE) VALUES(%s,%s,%s,%s,%s)", rows)

            sdb.commit()
            mycursor2.close()
            return render_template('addStudentData.html', info="File Uploaded and Data inserted Successfully")
        else:
            return render_template('addStudentData.html', info="No File Uploaded")
    return render_template('addStudentData.html')

app.run(debug=True)
