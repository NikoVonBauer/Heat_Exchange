from pywebio import start_server, config
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js
import math
import pandas as pd
import matplotlib.pyplot as plt
import io
import pywebio
import psycopg2
from config import host, user, password, db_name

def main():
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    conn.autocommit = True
    cur = conn.cursor()

    put_markdown("**Расчет теплообмена**")
    data = input_group("Введите данные", [
        input("Высота слоя:", name='H', placeholder='6'),
        input("Начальная температура материала:", name="TM1", placeholder='650'),
        input("Начальная температура газа:", name='TG1', placeholder='10'),
        input("Скорость газа на свободное сечение шахты:", name="VG", placeholder='0.6'),
        input("Средняя теплоёмкость газа:", name='TKG', placeholder='1.34'),
        input("Начальная теплоёмкость материала", name="TKM", placeholder='1.49'),
        input("Расход материалов:", name="LM", placeholder='1.7'),
        input("Диаметр аппарата", name="D", placeholder='2.1'),
        input("Объёмный коэффициент теплоотдачи", name="WK", placeholder='2450')
    ])
    m = (float(data["TKM"])*float(data["LM"]))/(float(data["VG"])*3.14*1.05*1.05*float(data["TKG"]))
    y0 = (float(data["WK"])*3.14*1.05*1.05*float(data["H"]))/(float(data["VG"])*3.14*1.05*1.05*float(data["TKG"]))/1000
    y = []
    hei = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []
    y6 = []
    y7 = []
    all = []
    i = 0
    while i <= float(data['H']):
        hei.append(i)
        count = (float(data['WK'])*i)/(float(data['VG'])*float(data['TKG']))/1000
        y.append(round(count, 3))
        count1 = 1 - math.exp(((m-1)*count)/m)
        y1.append(round(count1, 3))
        count2 = 1 - m*math.exp(((m-1)*count)/m)
        y2.append(round(count2, 3))
        count3 = count1/(1 - m*math.exp(((m-1)*y0)/m))
        y3.append(round(count3, 3))
        count4 = count2/(1 - m*math.exp(((m-1)*y0)/m))
        y4.append(round(count4, 3))
        count5 = float(data["TM1"]) + (float(data["TG1"])-float(data["TM1"]))*count3
        y5.append(round(count5, 3))
        count6 = float(data["TM1"]) + (float(data["TG1"])-float(data["TM1"]))*count4
        y6.append(round(count6, 3))
        count7 = count5 - count6
        y7.append(round(count7, 3))
        cur_query = 'INSERT INTO "Heat_exchange" ("Высота слоя", "(avy)/(wC)", "1 - exp[((m-1)Y)/m]", "1 -mexp[((m-1)Y)/m]", "V", "O", "t","T","Разность температур") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur_record = (i, count, count1, count2, count3, count4, count5, count6, count7)
        cur.execute(cur_query, cur_record)
        i+=0.5
        
    put_markdown("Значения:")
    put_text("m:", round(m,5))
    put_text("Y0:", round(y0,5))
    all.extend((y,y1,y2,y3,y4,y5,y6,y7))
    df = pd.DataFrame(all, index=["(avy)/(wC)", "1 - exp[((m-1)Y)/m]", "1 -mexp[((m-1)Y)/m]", "V", "O", "t","T","Разность температур"], columns=hei)
    put_html(df.to_html(border=0))

    put_markdown("**Графики изменения температур**")
    fig, ax = plt.subplots()
    ax.set_title("Изменение температуры окатышей и газа по высоте слоя")
    ax.set_xlabel("Высота слоя")
    ax.set_ylabel("Температура")
    ax.plot(hei,y5)
    ax.plot(hei,y6)

    buf = io.BytesIO()
    fig.savefig(buf)
    pywebio.output.put_image(buf.getvalue())

    fig, ax = plt.subplots()
    ax.set_title("Изменение разности температур")
    ax.set_xlabel("Высота слоя")
    ax.set_ylabel("Температура")
    ax.plot(hei,y7)

    buf = io.BytesIO()
    fig.savefig(buf)
    pywebio.output.put_image(buf.getvalue())

if __name__ == "__main__":
    config(theme="dark")
    start_server(main, debug=True, port=7259, cdn=False)