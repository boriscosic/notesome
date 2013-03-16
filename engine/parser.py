#!/usr/bin/python
import __init__ as lib
import feedparser
import datetime
import lxml.html
import re
import urllib2, httplib
import dateutil.parser
import time

def fetch():
	print 'selecting feeds from database'
	cur = lib.conn.cursor()
	cur.execute("select id,xml_url,tags,updated from links where public = 't' order by updated desc limit 50")
	rows = cur.fetchall()
	cur.close
	return rows

def parse(uri, updated):
	rss = feedparser.parse(uri)
	print "title: " + rss.feed.title

	cur = lib.conn.cursor()
	for entry in rss.entries: 
		content = ''
		summary = ''
		image = ''

		# check if this needs to be inserted by comparing dates
		title = str(entry.title.encode('ascii', 'ignore'))
		published = str(dateutil.parser.parse(entry.published))
		xml_link = link = str(entry.links[0].href)
		
		if updated is not None:
			if (updated.replace(tzinfo=None) > dateutil.parser.parse(published).replace(tzinfo=None)):
				continue
			else: 
				cur.execute("select id from feeds where xml_link = '" + xml_link + "'")
				record = cur.fetchone()
				if record:
					continue
		
		published = str(datetime.datetime.today())
		if entry.has_key('published'):
			published = str(entry.published)
		
		# some feeds have content or summary but not both
		if entry.has_key('content'):
			summary = content = str(entry.content[0].value.encode('ascii', 'ignore'))
			match = re.search(r'<img.*?src="([^"]*)".*?width="([^"]*)".*?>', content)
			if match:
				img = lxml.html.fromstring(match.group())
				if img.attrib.has_key('width') and int(img.attrib['width'].replace('px','')) > 200 and len(img) == 0:
					image = img.attrib['src']


		if entry.has_key('summary_detail'):
			summary = str(entry.summary_detail.value.encode('ascii', 'ignore'))
			if len(content) == 0:
				content = summary

		# get the actual link where this needs to go
		try:
			f = urllib2.urlopen(link)
			if link != f.geturl():
				link = f.geturl()
		except:
			print 'link error'

		tags = []
		if entry.has_key('tags'):
			for tag in entry.tags:
				tags.append(tag.term) 
	
		cur.execute("insert into feeds (title, summary, content, published, tags, link, xml_link, image, valid_image) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
			(title, summary, content, published, tags, link, xml_link, image, 'true'))
		lib.conn.commit()
	
	cur.close()


def main():
	rows = fetch()
	cur = lib.conn.cursor()
	for row in rows: 
		parse(row[1], row[3])
		cur.execute("update links set updated = '" + str(datetime.datetime.today()) + "' where id = " + str(row[0]))
		lib.conn.commit()
	cur.close()

if __name__ == '__main__':
    main()