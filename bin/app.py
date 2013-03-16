#!/usr/bin/env python
import web
import model
from helpers import *
from lxml import etree
import StringIO

urls = (
	'/', 'Index',
	'/reader/(\d+)', 'Reader',
	'/import', 'Import',
	'/update', 'Update',
	'/(js|css|img|bootstrap)/(.*)', 'static'
)

t_globals = {
    'get_domain': get_domain,
    'strip_tags': strip_tags,
}

app = web.application(urls, globals())
render = web.template.render('templates/', base='layout', globals=t_globals)
render_plain = web.template.render('templates/', globals=t_globals)

class Index:
	def GET(self):
		feeds = model.get_feeds()
		return render.reader(feeds)

class Reader:
	def GET(self, page):
		feeds = model.get_feeds(page)
		return render_plain.reader(feeds)

class Import:
	def GET(self):
		return render.googlereader()

	def POST(self):
		x = web.input(subscriptions={})
		stream = x['subscriptions'].file.read()
		parser = etree.XMLParser()
		for data in (stream):
			parser.feed(data)
		root = parser.close()
		if root[1].tag == 'body':
			for child in root[1]:
				if child.tag == 'outline':
					model.insert_feed(child.get('text'), child.get('title'), child.get('type'), child.get('xmlUrl'), child.get('htmlUrl'))

		return 'Uploading...'

class Update:
	def POST(self):
		post_input = web.input(_method='post')
		model.remove_image(post_input.fid)
		return post_input.fid

if __name__ == '__main__':
	app.run()