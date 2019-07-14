# project name: pi-vertical-garden
# created by diego aliaga daliaga_at_chacaltaya.edu.bo

from pi_sht1x import SHT1x
import RPi.GPIO as GPIO

import pandas as pd
import os
import sqlite3 as sq3
import datetime as dt

DATA_PIN = 18
SCK_PIN = 23
RELAY_PIN = 6


def get_soil_sensor_dic():
    with SHT1x(DATA_PIN, SCK_PIN, gpio_mode=GPIO.BCM) as sensor:
        temp = sensor.read_temperature()
        humidity = sensor.read_humidity(temp)
        dew_point = sensor.calculate_dew_point(temp, humidity)
        # print(sensor)
        now = get_now_timestamp()
        out_dic = {
            'temp'     : temp,
            'humidity' : humidity,
            'dew_point': dew_point,
            'dt_secs'  : timestamp2unix(now)
        }
    return out_dic


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
    return pd.to_datetime(ut*10**9)
