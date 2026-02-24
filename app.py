from flask import*
import pymysql
import pymysql.cursors
from flask_cors import CORS
import os# allows python code to work with various Operating Systems
app=Flask(__name__)
# allows requests from external origins
CORS(app)
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

# mpesa payment
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret 
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
        # Create a POST Request to above url, providing headers, payload 
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) # 
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})

if __name__=='__main__':
    app.run(debug=True)