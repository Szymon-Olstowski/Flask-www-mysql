from html.entities import html5
from flask import Flask, render_template, request, redirect, url_for, session,jsonify #install
from flask_mail_sendgrid import MailSendGrid
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message #install code
from werkzeug.datastructures import  FileStorage
from flask_mysqldb import MySQL #install
import MySQLdb.cursors #intsll
import re
from password_generator import PasswordGenerator #install
import datetime
import sql 
from pushbullet import Pushbullet #install
import subprocess as sp
import bcrypt
app = Flask(__name__)
# Zmień to na swój tajny klucz (może być dowolny, to dla dodatkowej ochrony)
app.secret_key = 'testowany_klucz'
# Wprowadź poniżej szczegóły połączenia z bazą danych
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'
#Zainicjuj MySQL
salt=bcrypt.gensalt()
mysql = MySQL(app)
@app.route("/")
def hello():
    return redirect(url_for('home'))
# http://localhost:5000/pythonlogin/ - poniżej będzie nasza strona logowania, która będzie używać zarówno żądań GET, jak i POST
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg=""
    # Sprawdź, czy istnieją żądania POST „nazwa użytkownika” i „hasło” (formularz przesłany przez użytkownika)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        account=sql.accountl(username)
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT password FROM accounts WHERE username = %s ', (username,))
        testp=cursor.fetchone()
       # Jeśli konto istnieje w tabeli kont w naszej bazie danych
        if bcrypt.checkpw(password.encode("utf-8"),testp[0].encode("utf-8")):
            # Utwórz dane sesji, możemy uzyskać dostęp do tych danych na innych trasach
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            sql.login_as(username)
            ip=request.remote_addr
            sql.login_ip(username,ip)
            #powiadomienie
            API_KEY = sql.api_key()
            text = f"Zalogowano: {username} pomyślnie do serwisu z adresu ip: {ip} "
            pb = Pushbullet(API_KEY)
            push = pb.push_note("Logowanie", text)
            #powiadomienie dla 2 użytkownika 
            API_KEY = sql.api_key1()
            text = f"Zalogowano: {username} pomyślnie do serwisu z adresu ip: {ip} "
            pb = Pushbullet(API_KEY)
            push = pb.push_note("Logowanie", text)
            return redirect(url_for('home'))
        else:
            # Konto nie istnieje lub niepoprawna nazwa użytkownika/hasło
            msg = 'Błędna nazwa użytkownika/hasło!'
    # Pokaż formularz logowania z wiadomością (jeśli istnieje)
    return render_template('index.html', msg=msg)
# http://localhost:5000/python/logout - to będzie strona wylogowania
@app.route('/pythonlogin/logout')
def logout():   
  # Usuń dane sesji, spowoduje to wylogowanie użytkownika
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   ip=request.remote_addr
   #powiadomienie
   API_KEY = sql.api_key()
   text = f"Wylogowamo użytkonika pomyślnie z serwisu z adresu ip: {ip} "
   pb = Pushbullet(API_KEY)
   push = pb.push_note("Wylogowano", text)
   #powiadomienie dla 2 użytkownika
   API_KEY = sql.api_key1()
   text = f"Wylogowamo użytkonika pomyślnie z serwisu z adresu ip: {ip} "
   pb = Pushbullet(API_KEY)
   push = pb.push_note("Wylogowano", text)
   # Redirect to login page
   return redirect(url_for('login'))
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg=""
    # Sprawdź, czy istnieją żądania POST „nazwa użytkownika” i „hasło” (formularz przesłany przez użytkownika)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Sprawdź, czy konto istnieje przy użyciu MySQL
        account=sql.spr_account(username)
       # Jeśli konto istnieje, pokaż błędy i sprawdzanie poprawności
        if account:
            msg = 'Konto już istnieje!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Nazwa użytkownika musi zawierać tylko znaki i cyfry!'
        elif not username or not password or not email:
            msg = 'Proszę wypełnić formularz!'
        else:
            app.config["MAIL_SENDGRID_API_KEY"] = sql.message_token()
            mail = MailSendGrid(app)
            with app.app_context():
                msg = Message(subject="Nowe konto",
                    sender=sql.message_username(),
                    recipients=[f"<{email}>"], # użyje emaila wprowadzonego w formularzu
                    html=f"Utworzono nowe konto na ten email. <br> Dane konta <br> Nazwa użytkownika: {username}<br> Hasło: {password}<br> Email: {email}",)
            mail.send(msg)
            ip=request.remote_addr
            #powiadomienie
            API_KEY = sql.api_key()
            text = f"Dodano konto {username} do serwisu z adrsu ip: {ip} "
            pb = Pushbullet(API_KEY)
            push = pb.push_note("Rejestracja", text)
            #powiadomienie dla 2 użytkownika
            API_KEY = sql.api_key1()
            text = f"Dodano konto {username} do serwisu z adrsu ip: {ip} "
            pb = Pushbullet(API_KEY)
            push = pb.push_note("Rejestracja", text)
            hashed=bcrypt.hashpw(password.encode("utf-8"),salt)
            #hasło zakodowane
            sql.konto_add(username, hashed, email,ip)
            msg = 'Konto zostało zarejestrowanie!'
    elif request.method == 'POST':
       # Formularz jest pusty... (brak danych POST)
        msg = 'Proszę wypełnić formularz!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
@app.route('/pythonlogin/home')
def home():
    msg=""
    # Sprawdź, czy użytkownik jest zalogowany
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
@app.route('/pythonlogin/profile')
def profile():
    msg=""
    # Sprawdź, czy użytkownik jest zalogowany
    if 'loggedin' in session:
        account = sql.profile_account(session)
        
        return render_template('profile.html', account=account)
       # Użytkownik nie jest zalogowany przekierowanie do strony logowania
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if request.method == 'POST':
        f =request.files['file']
        f.save(secure_filename(f.filename))
        ip=request.remote_addr
        #powiadomienie
        API_KEY = sql.api_key()
        text = f"Dodano plik do serwisu z adrsu ip: {ip} "
        pb = Pushbullet(API_KEY)
        push = pb.push_note("Pliki", text)
        return render_template('home.html')
@app.route('/pythonlogin/haslo',methods=['GET', 'POST'])
def haslo():
    msg=''
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            # Sprawdź, czy konto istnieje przy użyciu MySQL
            account = sql.spr_account(username)
            if account:
                hashed=bcrypt.hashpw(password.encode("utf-8"),salt)
                #hasło zakodowane
                sql.haslo_change(username,hashed)
                msg="Hasło zostało zmienione"
                ip=request.remote_addr
                #powiadomienie
                API_KEY = sql.api_key()
                text = f"Zmieniono hasło dla konta {username} do serwisu z adrsu ip: {ip} "
                pb = Pushbullet(API_KEY)
                push = pb.push_note("Zmiana hasła", text)
                #powiadomienie dla 2 użytkownika
                API_KEY = sql.api_key1()
                text = f"Zmieniono hasło dla konta {username} do serwisu z adrsu ip: {ip} "
                pb = Pushbullet(API_KEY)
                push = pb.push_note("Zmiana hasła", text)
        elif request.method == 'POST':
            # Formularz jest pusty... (brak danych POST)
            msg = 'Proszę wypełnić formularz!'
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
    # Show registration form with message (if any)
    return render_template('haslo.html', msg=msg)
@app.route("/pythonlogin/sklep")
def sklep():
    if 'loggedin' in session:
        sklepDetalis=sql.sklep()
        return render_template('sklep.html',sklepDetalis=sklepDetalis)
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
@app.route('/sklep_a', methods=['GET','POST'])
def sklep_a():
    msg=""
    if 'loggedin' in session:
        if request.method == 'POST' and 'indenfikator' in request.form and "ilosc" in request.form:
            indenfikator=request.form["indenfikator"]
            ilosc=request.form['ilosc']
            spr=sql.items_inf(indenfikator)
            if spr:
                cursor = mysql.connection.cursor()
                account = sql.account(session)
                cursor.execute("SELECT * FROM sklep where indenfikator= %s",(indenfikator,))
                cena=cursor.fetchone()
                print(cena[5])
                cena_cal=cena[5]*int(ilosc)
                cursor.execute("SELECT nazwa_produktu FROM sklep where indenfikator= %s",(indenfikator,))
                nazwa=cursor.fetchone()
                #doawanie produtu do bazy danych
                cursor.execute("INSERT INTO items VALUES (NULL, %s, %s,%s,%s,%s)",(indenfikator,ilosc,cena_cal,account[1],nazwa))
                mysql.connection.commit()
                akt=account[7]+cena_cal
                sql.money(akt,account[1])
            else:
                return redirect(url_for('sklep'))
    else:
        return redirect(url_for('login'))
    return redirect(url_for('koszyk'))
@app.route('/pythonlogin/data',methods=['GET', 'POST'])
def data():
    msg=''
    if 'loggedin' in session:
        account = sql.account(session)
        if account[8]=="admin":
            if request.method == 'POST' and 'nazwa_produktu' in request.form and 'producent' in request.form:
                # Utwarza nowe wartości do sklepu
                nazwa_produktu = request.form['nazwa_produktu']
                producent = request.form['producent']
                kategoria = request.form['kategoria']
                typ= request.form['typ']
                cena = request.form['cena']
                indenfikator = request.form['indenfikator']
                data=sql.data_spr(nazwa_produktu)
                data1=sql.data_spr1(indenfikator)
                if data==None and data1==None:
                    sql.data(nazwa_produktu,producent,kategoria,typ,cena,indenfikator)
                    msg="Dodano produkt do sklepu"
                    ip=request.remote_addr
                    #powiadomienie
                    API_KEY = sql.api_key()
                    text = f"Dodano produkt {nazwa_produktu} do sklepu z adrsu ip: {ip} przez {account[1]} "
                    pb = Pushbullet(API_KEY)
                    push = pb.push_note("Sklep", text)
                    #powiadomienie dla 2 użytkownika
                    API_KEY = sql.api_key1()
                    text = f"Dodano produkt {nazwa_produktu} do sklepu z adrsu ip: {ip} przez {account[1]} "
                    pb = Pushbullet(API_KEY)
                    push = pb.push_note("Sklep", text)
                else:
                    if data!=None and data1!=None:
                        msg="Nazwa proddukru i indenfikator istnieją się w sklepie"
                    if data:
                        msg="Ta nazwa produktu istenieje w sklepie"
                    if data1:
                        msg="Ten indenfikator istnieje w sklepie"
            elif request.method == 'POST':
                # Formularz jest pusty... (brak danych POST)
                msg = 'Proszę wypełnić formularz!'
        else:
           msg="Nie masz dostępu do dowawania produktów"
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
    # Show registration form with message (if any)
    return render_template('data.html', msg=msg)
@app.route('/pythonlogin/password_resert',methods=['GET', 'POST'])
def password_resert():
    msg=""
    if request.method == 'POST' and 'username' in request.form and "email":
        username = request.form['username']
        email = request.form['email']
        # Sprawdź, czy konto istnieje przy użyciu MySQL
        account = sql.spr_account(username)
        email_check = sql.spr_email(username,email)
        if account:
            if email_check:
                pwo = PasswordGenerator()
                pwo.minlen = 5 
                pwo.maxlen = 16
                password=pwo.generate()
                hashed=bcrypt.hashpw(password.encode("utf-8"),salt)
                #hasło zakodowane
                sql.haslo_change(username, hashed)
                app.config["MAIL_SENDGRID_API_KEY"] = sql.message_token()
                mail = MailSendGrid(app)
                with app.app_context():
                    msg = Message(subject="Hasło do konta",
                      sender=sql.message_username(),
                      recipients=[f"<{email}>"], # użyje emaila wprowadzonego w formularzu
                      body=f"Zmieniono twóje hasło do konta {username}. Nowe hasło do konta: {password}",)
                    mail.send(msg)
                ip=request.remote_addr
                #powiadomienie
                API_KEY = sql.api_key()
                text = f"Zmieniono hasło dla konta {username} do serwisu z adrsu ip: {ip} "
                pb = Pushbullet(API_KEY)
                push = pb.push_note("Zmiana hasła", text)
                msg="Ustawiono hasło na:  ",password
                #powiadomienie dla 2 użytkownika
                API_KEY = sql.api_key1()
                text = f"Zmieniono hasło dla konta {username} do serwisu z adrsu ip: {ip} "
                pb = Pushbullet(API_KEY)
                push = pb.push_note("Zmiana hasła", text)
                msg="Ustawiono hasło na:  ",password
            else:
                msg="Nieprawidłowy adres email"
        else:
            msg="Nie ma takiego konta"
    else:
        "Proszę wypełnić folmurarz"
    # Show registration form with message (if any)
    return render_template('password_resert.html', msg=msg)
@app.route('/pythonlogin/koszyk',methods=['GET', 'POST'])
def koszyk():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        account = sql.account(session)
        sklep=cursor.execute("SELECT * FROM items WHERE konto=%s",(account[1],))
        if sklep>0:
            sklepDetalis=cursor.fetchall()
        else:
            return redirect(url_for('sklep'))
        return render_template('koszyk.html',sklepDetalis=sklepDetalis,account=account)
@app.route('/items_change',methods=['GET', 'POST'])
def items_change():
    if 'loggedin' in session:
        if request.method == 'POST' and 'indenfikator' in request.form and "id" in request.form and "ilosc" in request.form and "usun":
            indenfikator=request.form["indenfikator"]
            id=request.form["id"]
            ilosc=request.form['ilosc']
            usun=request.form['usun']
            cursor = mysql.connection.cursor()
            spr=sql.items_inf(indenfikator)
            if spr:
                account = sql.account(session)
                cena=sql.cena_pr(indenfikator)
                cursor.execute("SELECT * FROM items where id=%s",(id))
                t=cursor.fetchone()
                if t:
                    t_b=int(t[2])
                    if usun=="TAK":
                        akt=int(account[7])-int(t[3])
                        cursor = mysql.connection.cursor()
                        sql.money(akt,account[1])
                        cursor.execute("DELETE FROM items where id=%s",(id,))
                        mysql.connection.commit()
                    else:
                        if t_b<int(ilosc):
                            cena_cal=cena[0]*int(ilosc)
                            print(cena_cal)
                            sql.koszyk_cena(cena_cal,id)
                            sql.koszyk_ilosc(ilosc,id)
                            test=cena_cal-int(t[3])
                            akt=int(account[7])+test
                            sql.money(akt,account[1])
                        if t_b>int(ilosc):
                            cena_cal=cena[0]*int(ilosc)
                            sql.koszyk_cena(cena_cal,id)
                            sql.koszyk_ilosc(ilosc,id)
                            test=int(t[3])-cena_cal
                            akt=int(account[7])-test
                            sql.money(akt,account[1])
            else:
                return redirect(url_for('koszyk'))
    else:
        return redirect(url_for('login'))
    return redirect(url_for('koszyk'))
@app.route('/admin',methods=['GET', 'POST'])
def admin():
    msg=''
    if 'loggedin' in session:
        account = sql.account(session)
        if account[8]=="admin":
            msg="Witaj"
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    return render_template('admin.html',msg=msg,username=session['username'])
@app.route('/permisje',methods=['GET', 'POST'])
def permisje():
    msg=''
    if 'loggedin' in session:
        account = sql.account(session)
        if account[8]=="admin":
            if request.method == 'POST' and 'username' in request.form and "permisje" in request.form:
                username= request.form['username']
                permisje= request.form['permisje']
                test=sql.spr_account(username)
                if test:
                    sql.permisje(permisje,username)
                    ip=request.remote_addr
                    #powiadomienie
                    API_KEY = sql.api_key()
                    text = f"Dla konta {username} zmieniono permisje z adresu ip: {ip} "
                    pb = Pushbullet(API_KEY)
                    push = pb.push_note("Permisje", text)
                    msg="Zmiana permisji została wykonana"
                    #powiadomienie dla w 2 użytkownika
                    API_KEY = sql.api_key1()
                    text = f"Dla konta {username} zmieniono permisje z adresu ip: {ip} "
                    pb = Pushbullet(API_KEY)
                    push = pb.push_note("Permisje", text)
                    msg="Zmiana permisji została wykonana"
                else:
                    msg="Nie ma takiego użytkownika"
            else:
                msg='Proszę wypełnić formularz!'
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    return render_template('permisje.html',msg=msg)
@app.route("/user")
def user():
    if 'loggedin' in session:
        account = sql.account(session)
        if account[8]=="admin":
            users=sql.user()
            return render_template('users.html',users=users)
        else:
            return redirect(url_for('home'))
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
@app.route('/koszyk_user')
def koszyk_user():
    msg=''
    if 'loggedin' in session:
        account = sql.account(session)
        if account[8]=="admin":
            users=sql.user1()
            if users==None:
                msg="Brak przediotów w koszyku"
            else:
                msg="Działa"
                return render_template('koszyk_users.html',users=users,msg=msg)
        else:
            return redirect(url_for('home'))
    else:
        #Użytkownik nie jest zalogowany przekierowanie do strony logowania
        return redirect(url_for('login'))
@app.route('/sklep_edit',methods=['GET', 'POST'])
def sklep_edit():
    if 'loggedin' in session:
        account = sql.account(session)
        if account[8]=="admin":
            if request.method == 'POST' and 'indenfikator' in request.form and "usun" in request.form and "cena_t" in request.form:
                indenfikator=request.form["indenfikator"]
                usun=request.form['usun']
                cena_t=request.form['cena_t']
                cursor = mysql.connection.cursor()
                spr=sql.items_inf(indenfikator)
                ip=request.remote_addr
                if spr:
                    account = sql.account(session)
                    cena=sql.cena_pr(indenfikator)
                    cursor.execute("SELECT * FROM items where indenfikator=%s",(indenfikator,))
                    t=cursor.fetchall()
                    if t:
                        if usun=="TAK":
                            for t in t:
                                print(t)
                                cursor.execute("SELECT * FROM accounts where username=%s",(t[4],))
                                konto=cursor.fetchone()
                                akt=int(konto[7])-int(t[3])
                                cursor = mysql.connection.cursor()
                                sql.money(akt,konto[1])
                                cursor.execute("DELETE FROM items where indenfikator=%s",(indenfikator,))
                                mysql.connection.commit()
                            cursor.execute("DELETE FROM Sklep WHERE indenfikator=%s",(indenfikator,))
                            mysql.connection.commit()
                            #powiadomienie
                            API_KEY = sql.api_key()
                            text = f"Admin {account[1]} usunął produkt z sklepu z adresu ip: {ip} "
                            pb = Pushbullet(API_KEY)
                            push = pb.push_note("Sklep", text)
                            #powiadomienie dla 2 użytkownika
                            API_KEY = sql.api_key1()
                            text = f"Admin {account[1]} usunął produkt z sklepu z adresu ip: {ip} "
                            pb = Pushbullet(API_KEY)
                            push = pb.push_note("Sklep", text)
                        else:
                            if cena[0]<int(cena_t):
                                for t in t:
                                    cursor.execute("SELECT * FROM accounts where username=%s",(t[4],))
                                    konto=cursor.fetchone()
                                    cena_cal=int(cena_t)*t[2]
                                    print(cena_cal)
                                    sql.koszyk_cena_2(cena_cal,konto[1])
                                    test=cena_cal-int(t[3])
                                    print(test)
                                    akt=int(konto[7])+test
                                    sql.money(akt,konto[1])
                                sql.sklep_update(int(cena_t),indenfikator)
                                #powiadomienie
                                API_KEY = sql.api_key()
                                text = f"Admin {account[1]} zwiększył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                                #powiadomienie dla 2 użytkownika
                                API_KEY = sql.api_key1()
                                text = f"Admin {account[1]} zwiększył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                            if cena[0]>int(cena_t):
                                for t in t:
                                    cursor.execute("SELECT * FROM accounts where username=%s",(t[4],))
                                    konto=cursor.fetchone()
                                    cena_cal=int(cena_t)*t[2]
                                    print(cena_cal)
                                    sql.koszyk_cena_2(cena_cal,konto[1])
                                    test=int(t[3])-cena_cal
                                    print(test)
                                    akt=int(konto[7])-test
                                    sql.money(akt,konto[1])
                                sql.sklep_update(int(cena_t),indenfikator)
                                #powiadomienie
                                API_KEY = sql.api_key()
                                text = f"Admin {account[1]} zmiejszył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                                #powiadomienie dla 2 użytkownika
                                API_KEY = sql.api_key()
                                text = f"Admin {account[1]} zmiejszył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                    else:
                        if usun=="TAK":
                            cursor.execute("DELETE FROM Sklep WHERE indenfikator=%s",(indenfikator,))
                            mysql.connection.commit()
                            #powiadomienie
                            API_KEY = sql.api_key()
                            text = f"Admin {account[1]} usunął produkt z sklepu z adresu ip: {ip} "
                            pb = Pushbullet(API_KEY)
                            push = pb.push_note("Sklep", text)
                            #powiadomienie dla 2 użytkownika
                            API_KEY = sql.api_key1()
                            text = f"Admin {account[1]} usunął produkt z sklepu z adresu ip: {ip} "
                            pb = Pushbullet(API_KEY)
                            push = pb.push_note("Sklep", text)
                        else:
                            if cena[0]<int(cena_t):
                                sql.sklep_update(int(cena_t),indenfikator)
                                #powiadomienie
                                API_KEY = sql.api_key()
                                text = f"Admin {account[1]} zwiększył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                                #powiadomienie dla 2 użytkownika
                                API_KEY = sql.api_key1()
                                text = f"Admin {account[1]} zwiększył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                            if cena[0]>int(cena_t):
                                sql.sklep_update(int(cena_t),indenfikator)
                                #powiadomienie
                                API_KEY = sql.api_key()
                                text = f"Admin {account[1]} zmniejszył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
                                #powiadomienie dla 2 użytkownika
                                API_KEY = sql.api_key1()
                                text = f"Admin {account[1]} zmniejszył cenę produktu do sklepu z adresu ip: {ip} "
                                pb = Pushbullet(API_KEY)
                                push = pb.push_note("Sklep", text)
            else:   
                return redirect(url_for('koszyk_user'))
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    return redirect(url_for('koszyk_user'))
@app.route('/pytania')
def pytania():
    if 'loggedin' in session:
        account = sql.account(session)
        ilosc_pytania=sql.spr_ilosc()
        ilosc_spr_username=sql.spr_ilosc_username(account[1])
        if ilosc_spr_username[0]==ilosc_pytania[0]:
            return redirect(url_for('odp'))
        else:
            pytanie=sql.pytania()
    else:
        return redirect(url_for('login'))
    return render_template('pytania.html',pytanie=pytanie)
@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST' and 'numer':
        ilosc_spr=sql.spr_ilosc()
        account = sql.account(session)
        id=request.form["numer"]
        mucha=request.form.getlist('mycheckbox')
        test=sql.pytania_pr(id)
        if test:
            if mucha[0]==test[2]:
                wmg="Tak"
                ilosc=account[10]+1
                sql.add_wynik(account[1],id,wmg,mucha[0])
                sql.wynik(ilosc,account[1])
            if mucha[0]!=test[2]:
                wmg="Nie"
                ilosc=account[10]
                sql.add_wynik(account[1],id,wmg,mucha[0])
                sql.wynik(ilosc,account[1])
        if ilosc_spr[0]==ilosc:
            return redirect(url_for('odp'))
    else:
        return redirect(url_for('login'))
    return redirect(url_for('pytania'))
@app.route('/odp')
def odp():
    if 'loggedin' in session:
        account = sql.account(session)
        pytanie=sql.pytania()
        ceck=sql.odp(account[1])
        ilosc=sql.spr_ilosc()
        suma=round(account[10]/ilosc[0],2)*100
        if suma==1.0:
            suma=100
    else:
        return redirect(url_for('login'))
    return render_template('odp.html',pytanie=pytanie,ceck=ceck,suma=suma,ilosc=ilosc,account=account)
@app.route('/button_odp' ,methods=['GET', 'POST'])
def button_odp():
    if request.method == 'POST':
        account = sql.account(session)
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM odp WHERE username=%s",(account[1],))
        mysql.connection.commit()
        ilosc=0
        sql.wynik(ilosc,account[1])
        ip=request.remote_addr
        #powiadomienie
        API_KEY = sql.api_key()
        text = f"Użytkownik {account[1]} wyczysćił własne odpowiedżi z adresu ip: {ip} "
        pb = Pushbullet(API_KEY)
        push = pb.push_note("Pytania", text)
        #powiadomienie dla 2 użytkownika
        API_KEY = sql.api_key1()
        text = f"Użytkownik {account[1]} wyczysćił własne odpowiedżi z adresu ip: {ip}"
        pb = Pushbullet(API_KEY)
        push = pb.push_note("Pytania", text)
    return redirect(url_for('pytania'))

"""
def is_mucha():
    if request.method == 'POST' and 
            'numer_pytania' in request.form and 
            "odp_tak" in request.form and "a" in request.form  and "b" in request.form and "c" in request.form and "d" in request.form and "tresc" in request.form and "wyczyc" in request.form:
"""

@app.route("/pytanie_add",methods=["GET", "POST"])
def pytanie_add():
    msg=""
    if 'loggedin' in session:
        account = sql.account(session)
        print(account[8])
        if account[8]=="admin":
            print("mucha13")
            print(request.form)
            if request.method == 'POST' and 'numer_pytania' in request.form and "odp_tak" in request.form and "a" in request.form  and "b" in request.form and "c" in request.form and "d" in request.form and "tresc" in request.form and "wyczyc" in request.form:
                print("mudewf4")
                numer_pytania=request.form['numer_pytania']
                odp_tak=request.form['odp_tak']
                a=request.form['a']
                b=request.form['b']
                c=request.form['c']
                d=request.form['d']
                tresc=request.form['tresc']
                wyczyc=request.form['wyczyc']
                print(numer_pytania,odp_tak,a,b,c,d,tresc,wyczyc)
                ip=request.remote_addr
                if wyczyc=="Tak":
                    print("Tak")
                    cursor = mysql.connection.cursor()
                    cursor.execute("DELETE FROM odp")
                    mysql.connection.commit()
                    ilosc=0
                    cursor.execute("UPDATE account SET odp_yes=%s",(ilosc,))
                    mysql.connection.commit()
                    sql.pytania_add(numer_pytania,odp_tak,a,b,c,d,tresc)
                    #powiadomienie
                    API_KEY = sql.api_key()
                    text = f"Administrator {account[1]} wyczysćił wszytkie pytania dodawając nowe pytania z adresu ip: {ip} "
                    pb = Pushbullet(API_KEY)
                    push = pb.push_note("Pytania", text)
                    #powiadomienie dla 2 użytkownika
                    API_KEY = sql.api_key1()
                    text = f"Administrator {account[1]} wyczysćił wszytkie pytania dodawając nowe pytania z adresu ip: {ip} "
                    pb = Pushbullet(API_KEY)
                    push = pb.push_note("Pytania", text)
                    msg="dodano pytanie"
                else:
                    print("nie")
                    pytanie=sql.pytania_pr(numer_pytania)
                    print(pytanie)
                    if pytanie:
                        msg="Podany numer pytania jest zajęty"
                    else:
                        sql.pytania_add(numer_pytania,odp_tak,a,b,c,d,tresc)
                        #powiadomienie
                        API_KEY = sql.api_key()
                        text = f"Administrator {account[1]} dodał nowe pytanie z adresu ip: {ip} "
                        pb = Pushbullet(API_KEY)
                        push = pb.push_note("Pytania", text)
                        #powiadomienie dla 2 użytkownika
                        API_KEY = sql.api_key1()
                        text = f"Administrator {account[1]} dodawł nowe pytania z adresu ip: {ip} "
                        pb = Pushbullet(API_KEY)
                        push = pb.push_note("Pytania", text) 
                        msg="dodano pytanie"   
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    return render_template('pytanie_add.html',msg=msg)

#zmień adres ip odowiedni dla swojej sieći
if __name__=="__main__":
    app.run(host="192.168.0.220")