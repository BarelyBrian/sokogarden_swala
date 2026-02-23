from flask import*
import pymysql
import pymysql.cursors
import os# allows python code to work with various Operating Systems
app=Flask(__name__)
# Configure your upload folder
app.config['UPLOAD_FOLDER']= 'static/images'


@app.route('/api/signup',methods=['POST'])
def signup():
    # extract values posted and we store them in a variable
    username= request.form['username']
    password= request.form['password']
    email= request.form['email']    
    phone= request.form['phone']
    # connection to database
    connection= pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_swala')
# cursor object= initialize connection/manipulation of the database
    cursor=connection.cursor()
    sql='INSERT INTO users(username,password,email,phone)values(%s,%s,%s,%s)'
    # Prepare data to replace the placeholder
    data= (username,password,email,phone)
    # we use the cursor to execute the sql under the data
    cursor.execute(sql,data)
    # save the changes
    connection.commit()
    return jsonify({"success":"Thanks for joining"})

# SIGN IN ROUTE
@app.route('/api/signin')
def signin():
    # extract post data
    username= request.form['username']
    password= request.form['password']
    # connect to 
    connection= pymysql.connect(host='localhost', user='root', password='',database='dailyyoghurt_swala')
    # inserting cursor
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    # do the sql query.
    sql='select*from users where username=%s and password=%s'
    data= (username,password)
    # execute data
    cursor.execute(sql,data)
    # check if there were rows that were occupied
    count= cursor.rowcount
    if count==0:
        return jsonify({'message':"Login failed"})
    else:
        user=cursor.fetchone()
        return jsonify({'message':'Log in successful','user':user})

# Adding a product
@app.route('/api/add_product',methods=['POST'])
def add_product():
    product_name= request.form['product_name']
    product_description=request.form['product_description']
    product_cost=request.form['product_cost']
    product_photo=request.files['product_photo']
    # extract the file name
    filename=product_photo.filename
    print('the filename is',filename)
    # specify the computer path where image will be saved(static/images)
    photo_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    product_photo.save(photo_path)
    # setting up connection
    connection=pymysql.connect(host='localhost', user='root', password='', database='dailyyoghurt_swala')
    # inserting cursor
    cursor=connection.cursor()
    sql= 'INSERT INTO product_details(product_name,product_description,product_cost,product_photo)values(%s,%s,%s,%s)'
    # prepare data to replace the place holder
    data=(product_name,product_description,product_cost,filename)
    # a cursor will execute the data
    cursor.execute(sql,data)
    # save the changes
    connection.commit()

    return jsonify({'message':"Product added succesfully"})

# get products
@app.route('/api/get_product_details')
def get_products():
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_swala')
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    sql='SELECT * FROM product_details'
    cursor.execute(sql)
    # fetch all records in a dictionary format
    product_details= cursor.fetchall()
    connection.commit()
    return jsonify(product_details)

if __name__=='__main__':
    app.run(debug=True)