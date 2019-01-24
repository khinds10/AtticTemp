#!/usr/bin/python
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import datetime as dt
import time, json, string, cgi, subprocess, json
import settings as settings
import Adafruit_DHT
from oled.device import ssd1306
from oled.render import canvas
from PIL import ImageFont

# mono 8 bit font
font = ImageFont.truetype('fonts/vcr.ttf', 50)
device = ssd1306(port=1, address=0x3C)

## Raspberry Pi with DHT22 sensor - connected to GPIO18 / Pin 12
sensor = Adafruit_DHT.DHT22
pin = 18
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

# get current date and time
date=dt.datetime.now()

# get 10 readings and average, in case the humidistat is inaccurate
count, readingCount, avgTemperature, avgHumidity = [ 0, 0, 0, 0 ]
while (count < 10):    
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        avgTemperature = avgTemperature + temperature
        avgHumidity = avgHumidity + humidity
        readingCount = readingCount + 1                
    count = count + 1
avgTemperature = avgTemperature / readingCount
insideTemperature = int(avgTemperature * 9/5 + 32)
avgHumidity = avgHumidity / readingCount
insideHumidity = int(avgHumidity)

# show temp on the 1306 display
with canvas(device) as draw:
    if insideTemperature > 100:
        font = ImageFont.truetype('fonts/vcr.ttf', 50)
        draw.text((10, 10),    str(insideTemperature) + '*',  font=font, fill=255)
    elif insideTemperature >= 0:
        font = ImageFont.truetype('fonts/vcr.ttf', 60)
        draw.text((20, 10),    str(insideTemperature) + '*',  font=font, fill=255)    
    else: 
        font = ImageFont.truetype('fonts/vcr.ttf', 50)
        draw.text((10, 10),    str(insideTemperature) + '*',  font=font, fill=255)

# get current forecast from location
weatherInfo = json.loads(subprocess.check_output(['curl', settings.weatherAPIURL + settings.weatherAPIKey + '/' + str(settings.latitude) + ',' + str(settings.longitude) + '?lang=en']))
currentConditions = weatherInfo['currently']
icon = str(currentConditions['icon'])
apparentTemperature = str(int(currentConditions['apparentTemperature']))
humidity = str(int(currentConditions['humidity'] * 100))
windSpeed = str(int(currentConditions['windSpeed']))
cloudCover = str(int(currentConditions['cloudCover'] * 100))
precipProbability = str(int(currentConditions['precipProbability'] * 100))

# minutely conditions, limit the characters to 30 in the summary
minutelyConditions = weatherInfo['minutely']
summary = str(minutelyConditions['summary'])
summary = (summary[:27] + '...') if len(summary) > 29 else summary

# conditions for the day
dailyConditions = weatherInfo['daily']
dailyConditions = dailyConditions['data'][0]
apparentTemperatureMin = str(int(dailyConditions['apparentTemperatureMin']))
apparentTemperatureMax = str(int(dailyConditions['apparentTemperatureMax']))

# clear and setup display to show basic info
subprocess.call(["/home/pi/AtticTemp/digole", "clear"])
subprocess.call(["/home/pi/AtticTemp/digole", "setRot90"])
subprocess.call(["/home/pi/AtticTemp/digole", icon])
subprocess.call(["/home/pi/AtticTemp/digole", "setFont", "18"])
subprocess.call(["/home/pi/AtticTemp/digole", "setColor", "255"])
subprocess.call(["/home/pi/AtticTemp/digole", "printxy_abs", "10", "178", summary])
subprocess.call(["/home/pi/AtticTemp/digole", "setFont", "51"])
subprocess.call(["/home/pi/AtticTemp/digole", "printxy_abs", "150", "40", date.strftime('%a, %b %d')])

# print the min daily temp in the evening and night, print the day max temp in the morning and daytime
if dt.datetime.now().hour > 16 or dt.datetime.now().hour < 6:
    subprocess.call(["/home/pi/AtticTemp/digole", "setColor", "223"])
    subprocess.call(["/home/pi/AtticTemp/digole", "printxy_abs", "150", "130", "LOW\n" + apparentTemperatureMin + '*F'])
else:
    subprocess.call(["/home/pi/AtticTemp/digole", "setColor", "222"])
    subprocess.call(["/home/pi/AtticTemp/digole", "printxy_abs", "150", "130", "HIGH\n" + apparentTemperatureMax + '*F'])

# show indoor / outdoor temp
subprocess.call(["/home/pi/AtticTemp/digole", "setFont", "120"])

subprocess.call(["/home/pi/AtticTemp/digole", "setColor", "255"])
subprocess.call(["/home/pi/AtticTemp/digole", "printxy_abs", "150", "85", apparentTemperature + "*F [" + humidity + "%]"])

subprocess.call(["/home/pi/AtticTemp/digole", "setColor", "250"])
subprocess.call(["/home/pi/AtticTemp/digole", "printxy_abs", "70", "230", "IN: " + str(insideTemperature) + "* F [" + str(insideHumidity) + " %]"])

