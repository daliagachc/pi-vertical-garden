# project name: pi-vertical-garden
# created by diego aliaga daliaga_at_chacaltaya.edu.bo

from pi_sht1x import SHT1x
import RPi.GPIO as GPIO

import pandas as pd
import os
import sqlite3 as sq3
import datetime as dt
import time

COL_TEMP = 'temp'

COL_HUMIDITY = 'humidity'

COL_DEW_POINT = 'dew_point'

COL_DT_SECS = 'dt_secs'

SOIL_DATA_TB_NAME = 'soil_data'

DATA_PIN = 18
SCK_PIN = 23
RELAY_PIN = 6

SOIL_MEAS_INTERVAL = 60

DB = '../data/data.sqlite'


def get_soil_sensor_dic():
    with SHT1x(DATA_PIN, SCK_PIN, gpio_mode=GPIO.BCM) as sensor:
        temp = sensor.read_temperature()
        humidity = sensor.read_humidity(temp)
        dew_point = sensor.calculate_dew_point(temp, humidity)
        # print(sensor)
        now = get_now_timestamp()
        out_dic = {
            COL_TEMP         : temp,
            COL_HUMIDITY : humidity,
            COL_DEW_POINT: dew_point,
            COL_DT_SECS  : timestamp2unix(now)
        }
    return out_dic

def get_soil_sensor_row():
    dic = get_soil_sensor_dic()
    ser = pd.Series(dic)
    df = pd.DataFrame(ser).T
    df = df.set_index(COL_DT_SECS)
    return df


# get_soil_sensor_dic()


def setup_valve():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)


# setup_valve()

def valve_on():
    setup_valve()
    GPIO.output(RELAY_PIN,0)

def valve_off():
    setup_valve()
    GPIO.setmode(GPIO.BCM)
    GPIO.output(RELAY_PIN,1)

def get_now_timestamp():
    now = dt.datetime.now()
    return pd.Timestamp(now)

def get_today_string():
    now = get_now_timestamp()
    return now.strftime('%Y-%m-%d')

def timestamp2unix(ts):
    return ts.value/10**9

def unix2timestamp(ut):
    return pd.to_datetime(round(int(ut*10**9)/100 )*100)

def get_now_unix():
    now = get_now_timestamp()
    now = timestamp2unix(now)
    return now

def add_soil_row2db(row):
    with sq3.connect(DB) as con:
        row.to_sql(SOIL_DATA_TB_NAME, con, index=True, if_exists='append')


def meas_soil_interval(meas_int=SOIL_MEAS_INTERVAL):
    dics = []
    t1 = get_now_unix()
    delt = 0
    while delt < meas_int:
        dics.append(get_soil_sensor_dic())
        time.sleep(meas_int / 11)
        delt = get_now_unix() - t1
    df = pd.DataFrame(dics).mean()
    df = pd.DataFrame(df).T
    df[COL_DT_SECS]=df[COL_DT_SECS].round().astype(int)
    row = df.set_index(COL_DT_SECS)
    return row


def get_soil_data():
    query = 'select * from {}'.format(SOIL_DATA_TB_NAME)
    with sq3.connect(DB) as con:
        df = pd.read_sql(query, con, index_col=COL_DT_SECS)
    return df

def drop_soil_table():
    query = 'drop table {}'.format(SOIL_DATA_TB_NAME)
    with sq3.connect(DB) as con:
        c = con
        cursor = c.cursor()
        cursor.execute(query)
        c.commit()

def start_soil_meas():
    while True:
        row=meas_soil_interval()
        add_soil_row2db(row)