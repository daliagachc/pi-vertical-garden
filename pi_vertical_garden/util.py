# project name: pi-vertical-garden
# created by diego aliaga daliaga_at_chacaltaya.edu.bo

from pi_sht1x import SHT1x
import RPi.GPIO as GPIO

DATA_PIN = 18
SCK_PIN = 23
RELAY_PIN = 6


def get_soil_sensor_dic():
    with SHT1x(DATA_PIN, SCK_PIN, gpio_mode=GPIO.BCM) as sensor:
        temp = sensor.read_temperature()
        humidity = sensor.read_humidity(temp)
        dew_point = sensor.calculate_dew_point(temp, humidity)
        # print(sensor)
        out_dic = {
            'temp'     : temp,
            'humidity' : humidity,
            'dew_point': dew_point
        }
    return out_dic


# get_soil_sensor_dic()



GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN,1)
GPIO.output(RELAY_PIN,0)