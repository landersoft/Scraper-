import datetime
import time

import requests
import json
from bs4 import BeautifulSoup
# import pandas as pd
from database import Database


# url = 'https://www.paris.cl/linea-blanca/lavado-secado/'
def urls(empresa, url):
    cuenta_url = 0
    respuesta = ''

    while True:

        zurl = (url + '?start={}&sz=24').format(cuenta_url)
        # print(zurl)
        time.sleep(3)
        try:
            pagina = requests.get(zurl, timeout=30)
        except Exception as e:
            print(e)
            print(zurl)
            pagina = None
            continue
        if pagina:
            if pagina.status_code == 200:
                respuesta = sopa(empresa, pagina)
                if respuesta == 'nok':
                    break
                cuenta_url += 24
        else:
            print(pagina.status_code)
            print("no hay respuesta")
            break


def sopa(empresa, pagina):
    soup = BeautifulSoup(pagina.content, 'html.parser')
    data = soup.find_all('div', class_='product-tile')
    # print(data)
    productos = list()
    if not data:
        return 'nok'
    temp = dict()
    for d in data:
        # print(d.get('data-product', 'sin informacion'))
        productos.append(d.get('data-product', 'sin informacion'))

    # print("cantidad_productos" + str(len(productos)))
    if len(productos) > 0:
        for p in range(len(productos)):
            try:
                temp[p] = json.loads(productos[p])
                # print("id: " + str(temp[p]['id']), ",marca: " + str(temp[p]['brand']), ",precio: " + str(temp[p]['price']),
                #      ",precio_tc: " + str(temp[p].get('dimension20', '0')))
                if temp[p]:
                    data = {"sku": str(temp[p]['id']),
                            "marca": str(temp[p]['brand']),
                            "producto": str(temp[p]['name']),
                            "precio": str(temp[p]['price']),
                            "precio_tc": str(temp[p].get('dimension20', str(temp[p]['price']))),
                            "fecha": datetime.datetime.now(),
                            "tienda": empresa
                            }

                    # print(data['sku'])
                    insertar_producto(empresa, data)
            except Exception as e:
                print('error_sin data json')
                continue


def insertar_producto(empresa, datos):
    producto_object = Database()
    producto = producto_object.find(empresa, datos['sku'])
    if producto:
        porcentage = float
        # print("precio_actual: {}".format(producto.get('precio', '')))
        # print('precio_nuevo: {}'.format(datos.get('precio', '')))
        if int(producto.get('precio', '')) != int(datos.get('precio', '')) or int(producto.get('precio_tc', '')) != int(
                datos.get('precio_tc', '')):
            if int(producto.get('precio', '')) > int(datos.get('precio', '')):
                print("ALERTA BAJÓ PRECIO DE: sku {} en tienda {} precio antiguo {} precio actual {}".format(
                    datos.get('sku', ''), producto.get('tienda', ''), producto.get('precio', ''), datos.get('precio')))
            elif int(producto.get('precio_tc', '')) > int(datos.get('precio_tc', '')):
                print("ALERTA DE PRECIO CON TC: sku {} en tienda {} precio antiguo {} precio actual {}".format(
                    datos.get('sku', ''), producto.get('tienda', ''), producto.get('precio_tc', ''),
                    datos.get('precio_tc', '')))
            # elif int(producto.get('precio_tc', '')) < int(datos.get('precio_tc', '')):
            #     print("ALERTA DE CANALLAS QLS TC EL PRECIO DE: sku {} en tienda {} precio antiguo {} precio actual {}".format(
            #         datos.get('sku', ''), producto.get('tienda', ''), producto.get('precio', ''), datos.get('precio')))

            # elif int(producto.get('precio', '')) < int(datos.get('precio', '')):
            # print("ALERTA DE CANALLAS QLS EL PRECIO DE: sku {} en tienda {} precio antiguo {} precio actual {}".format(
            #    datos.get('sku', ''), producto.get('tienda', ''), producto.get('precio', ''), datos.get('precio')))
            porcentage = (1-(int(producto.get('precio', 0))/int(datos['precio'])))*100

            print("hay diferencia {}".format(porcentage))

            producto_object.update(empresa, datos['sku'], datos['precio'], datos['precio_tc'], producto.get('precio', ''), producto.get('precio_tc', ''), porcentage)

    else:
        # print("producto_nuevo: {}".format(datos))
        producto_object.inserta(empresa, datos)


if __name__ == '__main__':
    links = [
        'https://www.paris.cl/electro/television/',
        'https://www.paris.cl/electro/audio/',
        'https://www.paris.cl/electro/audio-hifi/',
        'https://www.paris.cl/tecnologia/computadores/',
        'https://www.paris.cl/tecnologia/celulares/',
        # 'https://www.paris.cl/tecnologia/smart-home/',
        # 'https://www.paris.cl/tecnologia/gamers/',
        'https://www.paris.cl/tecnologia/fotografia/',
        # 'https://www.paris.cl/linea-blanca/refrigeracion/',
        # 'https://www.paris.cl/linea-blanca/lavado-secado/',
        'https://www.paris.cl/linea-blanca/electrodomesticos/',
        'https://www.paris.cl/deportes/bicicletas/'

        # 'https://www.paris.cl/decohogar/navidad/pinos/',
        # 'https://www.paris.cl/decohogar/navidad/esferas/',

    ]
    while True:
        for l in links:
            empresa = l.split(".")[1]
            urls(empresa, l)
