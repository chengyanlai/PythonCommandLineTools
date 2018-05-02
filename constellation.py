#!/usr/bin/env python3
# coding=utf-8
import sys
from datetime import datetime

zodiacs = [(120, 'Capricorn', u'摩羯'),
           (218, 'Aquarius', u'水瓶'),
           (320, 'Pisces', u'雙魚'),
           (420, 'Aries', u'牡羊'),
           (521, 'Taurus', u'金牛'),
           (621, 'Gemini', u'雙子'),
           (722, 'Cancer', u'巨蟹'),
           (823, 'Leo', u'獅子'),
           (923, 'Virgo', u'處女'),
           (1023, 'Libra', u'天秤'),
           (1122, 'Scopio', u'天蠍'),
           (1222, 'Sagittarius', u'射手'),
           (1231, 'Capricorn', u'摩羯')]

if __name__ == "__main__":
  if len(sys.argv) == 1:
    date_number = datetime.today().month * 100 + datetime.today().day
  else:
    month, day = map(int, sys.argv[1].split('-'))
    date_object = datetime(datetime.today().year, month, day)
    date_number = date_object.month * 100 + date_object.day
  for z in zodiacs:
    if date_number <= z[0]:
      print(date_number, z[1], z[2])
      break
