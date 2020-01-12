import requests
import re
from bs4 import BeautifulSoup
import sqlite3
import smtplib
import time
import mysql.connector
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def recorre(id_link):


    try:
        link = id_link
    
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
        pagina = requests.get(URL, headers=headers)
        soup = BeautifulSoup(pagina.content, 'html.parser')

        sku = soup.find_all("a", {"class": "thumb-link js-product-layer"})
        titulo = soup.find_all("span", {"class": "ellipsis_text", "itemprop": "name"})
        precio = soup.find_all("div", {
                "class": ["item-price offer-price price-tc cencosud-price", "item-price offer-price price-tc default-price"]})

        for i in range(len(sku)):
            sku[i] = str(re.findall(r"(\d+).html", sku[i]['href'])[0])

        for i in range(len(titulo)):
            titulo[i] = re.findall(r'>(.*?)<', str(titulo[i]))
            titulo[i] = titulo[i][0]

        for i in range(len(precio)):
            precio[i] = re.findall(r'[$][0-9]+.+', str(precio[i]))
            print(precio[i])
            if not precio[i]:
                precio[i]=0

            else:
                precio[i] = precio[i][0]
                print(precio[i])
                precio[i] = precio[i].replace("$", "")
                precio[i] = precio[i].replace(".", "")

        if (len(sku) == len(titulo) == len(precio)):
            for i in range(len(sku)):
                producto.insert(i, [sku[i], titulo[i], precio[i]])
        
    except:
        recorre(x[0]) 


def manda_correo():
 

    msg = MIMEMultipart()
    message = ''
    
    for di in diferencia:
        message += "Hay diferencia en %s %s %s \n" % (str(di[0]),str(di[1]),str(di[2]))

    print(message)
    # setup the parameters of the message
    password = "kbvdoyvjwgffhtqk"
    msg['From'] = "mail@gmail.com"
    msg['To'] = "me@gmail.com"
    msg['Subject'] = "Algo bajó de precio en Paris"
    
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    server.starttls()
    
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    
    
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    server.quit()
    
    print ("successfully sent email to %s:" % (msg['To']))


def guarda(id_link):
    link = id_link  
    cnx = mysql.connector.connect(host='localhost',database='mydb',user='root',password='password')
    try:
        cursor = cnx.cursor()

        for x in producto:        
            inserta = 'REPLACE INTO producto(sku,descripcion,precio,link_id)VALUES(%s, %s, %s, %s)'
            args=(x[0],x[1],x[2],link)
            cursor.execute(inserta,args)

            cnx.commit() 
    finally:
        cnx.close()


def verifica(LRU):
    args = LRU
    print(LRU)
    
    cnx = mysql.connector.connect(host='localhost',database='mydb',user='root',password='password')
    try:
        cursor = cnx.cursor()
                
        obtiene = 'SELECT sku,descripcion,precio FROM producto where link_id = %s'
        cursor.execute(obtiene,(LRU,))
        result = cursor.fetchall()

    finally:
        cnx.close()
    
    print("El largo del recorrido es: ", len(producto))

    contador = 0
    for x in producto:
        a=int(x[0])
        valora=int(x[2])
        for y in result:    
            b = int(y[0])
            valorb = int(y[2])
            contador += 1
            print(contador, a, b, '  Valores: ', valora, valorb)
            if a == b and valora < valorb:
                diferencia.append(x)
                diferencia.append(y)
                break
            elif a == b and valora == valorb:
                break
       
              
####################################################################################


while(True):

    producto = []
    diferencia = []
    URL = ''

    cnx = mysql.connector.connect(host='localhost', database='mydb', user='root', password='password')
    try:
        cursor = cnx.cursor()
        cursor.execute("""select id,link from link""")
        result = cursor.fetchall()
        
        for x in result:        
            URL = x[1]       
            recorre(x[0])        
            verifica(x[0])
            guarda(x[0])
            producto = []
            
    finally:
        cnx.close()

        if len(diferencia)>0:
            print('hay diferencias')
            for x in diferencia:
                print(x)
            cnx = mysql.connector.connect(host='localhost', database='mydb', user='root', password='password')
            try:
                cursor = cnx.cursor()

                for q in diferencia:        
                    inserta = 'INSERT INTO cambio(sku,descripcion,precio)VALUES(%s, %s, %s)'
                    args = (q[0], q[1], q[2])
                    cursor.execute(inserta, args)

                    cnx.commit()
            finally:
                cnx.close()
            manda_correo() 
    

    time.sleep(300)


