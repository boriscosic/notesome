#!/usr/bin/env python
import web
import sys
import psycopg2

try:
	db = web.database(dbn='postgres', db='notesome', user='postgres', password='password', host='debian')
except:
	print "Unexpected error:", sys.exc_info()[0]
	raise

def get_feeds(page = None):
	if page != None:
		page = 50 * (int(page) - 1)
	return db.select('feeds', order='published desc', limit='50', offset=page or 0)

def insert_feed(text, title, type, xml_url, html_url):
	db.insert('links', text=text, title=title, type=type, xml_url=xml_url, html_url=html_url)

def remove_image(fid):
	db.update('feeds', where="id = " + str(int(fid)), valid_image='false')