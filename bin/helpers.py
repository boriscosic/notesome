#!/usr/bin/env python
from urlparse import urlparse
from bs4 import BeautifulSoup

def get_domain(uri):
	parsed_uri = urlparse(uri)
	return parsed_uri[1]

def strip_tags(html):
	soup = BeautifulSoup(html)
	return ''.join([e for e in soup.recursiveChildGenerator() if isinstance(e,unicode)])