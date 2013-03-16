#!/usr/bin/python
import sys
import psycopg2

try:
	conn = psycopg2.connect("dbname=notesome user=postgres password=password host=debian")
except:
	print 'unable to connect to database'