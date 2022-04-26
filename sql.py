from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
from pushbullet import pushbullet
mysql = MySQL()
def accountl(username):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accounts WHERE username = %s ',(username,))
    # Pobierz jeden rekord i zwróć wynik
    account = cursor.fetchone()
    return account
def account(session):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (session["id"],))
    account = cursor.fetchone()
    return account
def profile_account(session):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (session["id"],))
    account = cursor.fetchone()
    return account
def login_as(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    x = datetime.datetime.now()
    ostatnie_logowanie=x.strftime("%d.%m.%Y %H:%M:%S")
    cursor.execute('UPDATE accounts SET login_as=%s WHERE username=%s', (ostatnie_logowanie,username))
    mysql.connection.commit()
def login_ip(username,ip):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE accounts SET adres_ip=%s WHERE username=%s', (ip,username))
    mysql.connection.commit()

def spr_account(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
    account = cursor.fetchone()
    return account
def konto_add(username,password,email,ip):
    cena=0
    permisje='user'
    x = datetime.datetime.now()
    stworone_koto=x.strftime("%d.%m.%Y %H:%M:%S")
    ostatnie_logowanie=x.strftime("%d.%m.%Y %H:%M:%S")
    ostatnie_zmiana_hasla=x.strftime("%d.%m.%Y %H:%M:%S")
    ilosc_odp=0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)', (username, password, email,stworone_koto,ostatnie_logowanie,ostatnie_zmiana_hasla,cena,permisje,ip,ilosc_odp))
    mysql.connection.commit()
def haslo_change(username,password):
    x = datetime.datetime.now()
    ostatnie_zmiana_hasla=x.strftime("%d.%m.%Y %H:%M:%S")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE accounts SET password=%s WHERE username=%s', (password,username))
    mysql.connection.commit()
    cursor.execute('UPDATE accounts SET haslo_change=%s WHERE username=%s', (ostatnie_zmiana_hasla,username))
    mysql.connection.commit()
def sklep():
    cursor=mysql.connection.cursor()
    sklep=cursor.execute("SELECT * FROM SKLEP")
    if sklep >0:
        sklepDetalis=cursor.fetchall()
    return sklepDetalis
def data(nazwa_produktu,producent,kategoria,typ,cena,indenfikator):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO sklep VALUES (NULL, %s, %s,%s,%s,%s,%s)', (nazwa_produktu,producent,kategoria,typ,cena,indenfikator))
    mysql.connection.commit()
def data_spr(nazwa_produktu):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM sklep WHERE nazwa_produktu=%s', (nazwa_produktu,))
    data = cursor.fetchone()
    return data
def data_spr1(indenfikator):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM sklep WHERE indenfikator=%s', (indenfikator,))
    data1 = cursor.fetchone()
    return data1
def spr_email(username,email):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT username=%s FROM accounts WHERE email = %s', (username,email))
    email_check = cursor.fetchone()
    return email_check
def items_inf(indenfikator):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sklep where indenfikator= %s",(indenfikator,))
    spr = cursor.fetchone()
    return spr
def koszyk_cena(cena_cal,id):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE items set cena=%s WHERE id=%s",(cena_cal,id))
    mysql.connection.commit()
def koszyk_cena_2(cena_cal,konto):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE items set cena=%s WHERE konto=%s",(cena_cal,konto))
    mysql.connection.commit()
def koszyk_ilosc(ilosc,id):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE items set ilosc=%s WHERE id=%s",(ilosc,id))
    mysql.connection.commit()
def money(akt,account):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE accounts SET money=%s WHERE username=%s', (akt,account,))
    mysql.connection.commit()
def cena_pr(indenfikator):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT cena FROM sklep where indenfikator= %s",(indenfikator,))
    cena=cursor.fetchone()
    return cena
def read_haslo():
    with open("haslo_konta.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()
def mail_settings():
    haslo=read_haslo()
    mail_settings = {
        "MAIL_SERVER": 'smtp.gamil.com',#serwis pocztowy do wysłania wiadomości
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME":  "",#wprowadź swój email do konta
        "MAIL_PASSWORD": f'{haslo}'
        }
    return mail_settings
def api_key():
    API_KEY = ""#Weź kod z strony Pushbullet
    return API_KEY
def api_key1():
    API_KEY = ""#Weź kod z strony Pushbullet
    return API_KEY
def permisje(permisje,username):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE accounts SET permisje=%s WHERE username=%s', (permisje,username))
    mysql.connection.commit()
def user():
    cursor=mysql.connection.cursor()
    sklep=cursor.execute("SELECT * FROM accounts")
    if sklep >0:
        users=cursor.fetchall()
    return users
def user1():
    cursor=mysql.connection.cursor()
    sklep=cursor.execute("SELECT * FROM items")
    if sklep >0:
        users=cursor.fetchall()
    else:
        users=cursor.fetchall()
    return users
def sklep_update(cena,indenfikator):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE sklep SET cena=%s WHERE indenfikator=%s', (cena,indenfikator))
    mysql.connection.commit()
def pytania():
    cursor=mysql.connection.cursor()
    pytanie=cursor.execute("SELECT * FROM pytania")
    if pytanie >0:
        pytanie=cursor.fetchall()
    else:
        pytanie=cursor.fetchall()
    return pytanie
def pytania_pr(numer_pytania):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pytania where numer_pytania= %s",(numer_pytania,))
    cena=cursor.fetchone()
    return cena
def add_wynik(username,numer_pytania,odp,wybrana_odp):
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO odp VALUES(NULL,%s,%s,%s,%s)',(username,numer_pytania,odp,wybrana_odp))
    mysql.connection.commit()
def wynik(ilosc,username):
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE accounts SET odp_yes=%s WHERE username=%s',(ilosc,username))
    mysql.connection.commit()
def spr_ilosc():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM pytania')
    ilosc=cursor.fetchone()
    return ilosc
def spr_ilosc_username(username):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM odp WHERE username=%s',(username,))
    ilosc=cursor.fetchone()
    return ilosc
def odp(username):
    cursor = mysql.connection.cursor()
    odp=cursor.execute('SELECT * FROM odp WHERE username=%s',(username,))
    if odp >0:
        odp=cursor.fetchall()
    else:
        odp=cursor.fetchall()
    return odp