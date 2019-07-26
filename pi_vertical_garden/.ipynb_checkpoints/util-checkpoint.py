# project name: pi-vertical-garden
# created by diego aliaga daliaga_at_chacaltaya.edu.bo

from pi_sht1x import SHT1x
import RPi.GPIO as GPIO

import pandas as pd
import sqlite3 as sq3
import datetime as dt
import time
import logging
import os
from pprint import pformat
import matplotlib.pyplot as plt
plt.style.use('ggplot')

GPIO.setwarnings(False)

from pi_vertical_garden.pvg_log import logger
LOG_LEVEL = logging.DEBUG
logger.setLevel(LOG_LEVEL)

COL_TEMP = 'temp'
COL_HUMIDITY = 'humidity'
COL_DEW_POINT = 'dew_point'
COL_DT_SECS = 'dt_secs'
SOIL_DATA_TB_NAME = 'soil_data'

DATA_PIN = 18
SCK_PIN = 23
RELAY_PIN = 6

SOIL_MEAS_INTERVAL = 60 #in seconds
HUM_CHECK_INTERVAL = 600
VALVE_OPEN_TIME = 120
HUM_OPEN_THRESHOLD = 75

DB = 'data.sqlite'


def get_soil_sensor_dic():
    with SHT1x(DATA_PIN, SCK_PIN, gpio_mode=GPIO.BCM) as sensor:
        logger.setLevel(LOG_LEVEL)
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
    logger.debug(os.getcwd())
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
    df[COL_DT_SECS]=df[COL_DT_SECS].astype(int)
    df[COL_DT_SECS]=(df[COL_DT_SECS]/meas_int).round() * meas_int
    row = df.set_index(COL_DT_SECS)
    return row


def get_soil_data(db=DB,last=10**9):
    now = get_now_unix()
    last_unix = now-last
    query = 'select * from {} where {}>{} '.format(SOIL_DATA_TB_NAME,COL_DT_SECS,last_unix)
    with sq3.connect(db) as con:
        df = pd.read_sql(query, con, index_col=COL_DT_SECS)
    return df

def drop_soil_table(db=DB):
    query = 'drop table {}'.format(SOIL_DATA_TB_NAME)
    with sq3.connect(DB) as con:
        c = con
        cursor = c.cursor()
        cursor.execute(query)
        c.commit()

def start_soil_meas():
    while True:
        logger.debug('getting row')
        row=meas_soil_interval(meas_int=SOIL_MEAS_INTERVAL)
        logger.debug('adding row to db')
        logger.debug(pformat(row))
        add_soil_row2db(row)

def plot_col_ts(col,db=DB,last=10**9):
    ds = get_soil_data(db=db,last=last)
    ds.index = pd.to_datetime(ds.index*10**9)
    ds = ds[[col]]
    ds.plot(style='.')

def plot_cols(db=DB,last=10**9):
    cols = [COL_DEW_POINT,COL_HUMIDITY,COL_TEMP]
    for c in cols:
        plot_col_ts(c,db=db,last=last)

def open_valve(check_int = VALVE_OPEN_TIME):
    valve_on()
    time.sleep(check_int)
    valve_off()

def check_hum_threshold():
    hum = get_last_soil_hum()
    logger.debug('hum is %s',hum)
    logger.debug('hum threshold is %s',HUM_OPEN_THRESHOLD)
    #logger.debug('%s',hum<HUM_OPEN_THRESHOLD)
    if hum<HUM_OPEN_THRESHOLD:
        logger.debug('opening valve for %s seconds', VALVE_OPEN_TIME)
        open_valve(VALVE_OPEN_TIME)
    logger.debug('sleeping for %s seconds', HUM_CHECK_INTERVAL)
    time.sleep(HUM_CHECK_INTERVAL)

def start_valve_watchdog():
    logger.debug('start valve watchdog')
    valve_off()
    try:
        while True:
            check_hum_threshold()
            logger.debug('hum check done. resting for %s seconds',HUM_CHECK_INTERVAL)
    except:
        logger.error('there s been an error')
        pass
    finally:
        valve_off()

def get_soil_data_last_row():
    query = 'select * from {} order by {} desc limit 1'
    query = query.format(SOIL_DATA_TB_NAME,COL_DT_SECS)
    with sq3.connect(DB) as con:
        df = pd.read_sql(query, con, index_col=COL_DT_SECS)

    row = df.iloc[0]


    return row


def check_delta_t_ok(row):
    now = get_now_unix()
    row_time = row.name
    delta_t = now - row_time
    delta_t_ok = delta_t < 2 * SOIL_MEAS_INTERVAL
    return delta_t_ok

def get_last_soil_hum():
    for i in range(2):
        row = get_soil_data_last_row()
        delta_t_ok = check_delta_t_ok(row)
        if delta_t_ok:
            return row[COL_HUMIDITY]
        else:
            time.sleep(SOIL_MEAS_INTERVAL)
    logger.error('we cant get last humidity from db')

