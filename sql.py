from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
from pushbullet import pushbullet
mysql = MySQL()
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
def spr_account(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
    account = cursor.fetchone()
    return account
def konto_add(username,password,email):
    cena=0
    permisje='user'
    x = datetime.datetime.now()
    stworone_koto=x.strftime("%d.%m.%Y %H:%M:%S")
    ostatnie_logowanie=x.strftime("%d.%m.%Y %H:%M:%S")
    ostatnie_zmiana_hasla=x.strftime("%d.%m.%Y %H:%M:%S")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s,%s,%s,%s,%s,%s)', (username, password, email,stworone_koto,ostatnie_logowanie,ostatnie_zmiana_hasla,cena,permisje))
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
        "MAIL_SERVER": 'smtp.gmail.com',#serwis pocztowy do wysłania wiadomości
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME":  "olstows30@gmail.com",#wprowadź swój email do konta
        "MAIL_PASSWORD": f'{haslo}'
        }
    return mail_settings
def read_pushbullet_key():
    with open("key_pushbullet.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()
def api_key():
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
