from flask import Flask, render_template, request, redirect, url_for, session #install
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message #install code
from werkzeug.datastructures import  FileStorage
from flask_mysqldb import MySQL #install
import MySQLdb.cursors #intsll
import re
from password_generator import PasswordGenerator #install
import datetime
import sql
app = Flask(__name__)
# Zmień to na swój tajny klucz (może być dowolny, to dla dodatkowej ochrony)
app.secret_key = 'testowany_klucz'
# Wprowadź poniżej szczegóły połączenia z bazą danych
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'
#Zainicjuj MySQL
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
       # Sprawdź, czy konto istnieje przy użyciu MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
       # Pobierz jeden rekord i zwróć wynik
        account = cursor.fetchone()
       # Jeśli konto istnieje w tabeli kont w naszej bazie danych
        if account:
            # Utwórz dane sesji, możemy uzyskać dostęp do tych danych na innych trasach
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Przekieruj na stronę główną
            #x = datetime.datetime.now()
            #ostatnie_logowanie=x.strftime("%d.%m.%Y %H:%M:%S")
            #cursor.execute('UPDATE accounts SET login_as=%s WHERE username=%s', (ostatnie_logowanie,username))
            #mysql.connection.commit()
            sql.login_as(username)
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
            sql.konto_add(username, password, email)
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
                sql.haslo_change(username,password)
                msg="Hasło zostało zmienione"
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
        if request.method == 'POST' and 'nazwa_produktu' in request.form and 'producent' in request.form:
            # Utwarza nowe wartości do sklepu
            nazwa_produktu = request.form['nazwa_produktu']
            producent = request.form['producent']
            kategoria = request.form['kategoria']
            typ= request.form['typ']
            cena = request.form['cena']
            indenfikator = request.form['indenfikator']
            sql.data(nazwa_produktu,producent,kategoria,typ,cena,indenfikator)
            msg="Dodano produkt bobra"
        elif request.method == 'POST':
            # Formularz jest pusty... (brak danych POST)
            msg = 'Proszę wypełnić formularz!'
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
                sql.haslo_change(username, password)
                haslo=sql.read_haslo()
                mail_settings = {
                "MAIL_SERVER": 'smtp.gmail.com',
                "MAIL_PORT": 465,
                "MAIL_USE_TLS": False,
                "MAIL_USE_SSL": True,
                "MAIL_USERNAME":  "olstows30@gmail.com",
                "MAIL_PASSWORD": f'{haslo}'
                }
                app.config.update(mail_settings)
                mail = Mail(app)
                with app.app_context():
                    msg = Message(subject="Hasło do konta",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[f"<{email}>"], # use your email for testing
                      body=f"Zmieniono twóje hasło do konta {username}. Nowe hasło do konta: {password}",)
                    mail.send(msg)
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
                #cursor.execute("SELECT cena FROM sklep where indenfikator= %s",(indenfikator,))
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
    
if __name__ == '__main__':
#zmień adres ip odowiedni dla swojej sieći
    app.run(host="192.168.0.220")