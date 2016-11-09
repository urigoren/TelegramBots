# -*- coding: utf-8 -*-
from icalendar import Calendar
from datetime import datetime
with open('basic.ics', 'rb') as f:
	cal = Calendar.from_ical(f.read())
day = lambda dt: tuple(map(int,str(dt).split(' ',1)[0].split('-',2)))
events = [(e['DTSTART'].dt,e['SUMMARY'].title()) for e in cal.walk('vevent') if day(e['DTSTART'].dt)>=day(datetime.today())]