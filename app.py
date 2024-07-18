from flask import Flask, render_template, request, session
import cv2
import pickle
import cvzone
import numpy as np
import ibm_db
import re

app = Flask(__name__)
app.secret_key = 'a'
print("AI Enabled Car Parking Using OpenCV project")
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=rrn90477;PWD=QbybMVP8YjYVwZT8","", "")
print("connected")


@app.route('/')
def project():
    return render_template('index.html')


@app.route('/hero')
def home():
    return render_template('index.html')


@app.route('/model')
def model():
    return render_template('model.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route("/reg", methods=['POST', 'GET'])
def signup():
    msg = ''
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE EMAIL? AND PASSWORD-?"  # from db2 sal table
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            return render_template('login.html', error=True)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid Email Address!"
        else:
            insert_sql = "INSERT INTO REGISTER VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            # this username and password
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 2, password)
            ibm_db.execute(prep_stmt)
            msg = "you have sucessfully registered !"
    return render_template('login.html', msg=msg)


@app.route("/log", methods=['POST', 'GET'])
def login1():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE EMAIL? AND PASSWORD-?"  # from db2 sql table
        stmt = ibm_db.prepare(conn, sql)
        # this username & password should be same as cb-2 details & order also
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['EMAIL']
            session['email'] = account['EMAIL']
            return render_template('model.html')
        else:
            msg = "Incorrect Email/password"
            return render_template('Login.html', msg=msg)
    else:
        return render_template('Login.html')


@app.route('/predict_live')
def liv_pred():
    # Video feed
    cap = cv2.VideoCapture('carPark.mp4')
    with open('parkingslotPosition', 'rb') as f:
        posList = pickle.load(f)
    width, height = 107, 45

    def checkParkingspace(imgPro):
        spacecounter = 0
        for pos in posList:
            x, y = pos
            imgcrop = imgPro[y:y + height, x:x + width]
            # cv2.imshow(str(x * 0, imgcrop)
            count = cv2.countNonzero(imgcrop)
            if count < 900:
                color = (0, 255, 0)
                thickness = 5
                spacecounter += 1
            else:
                color = (0, 0, 255)
                thickness = 2
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)

        cvzone.putTextRect(img, f'Free: {spacecounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0, 200, 0))

    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         CV2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    Kernel = np.ones((3, 3), np.vint8)
    imgDilate = cv2.ditate(imgMedian, kernel, iterations=1)
    checkParkingspace(imgDilate)
    cv2.imshow("Image", img)

    if cv2.waitkey(1) & 0xFF == ord('q'):
        sys.exit()


if __name__ == "__main__":
    app.run(debug=True)
