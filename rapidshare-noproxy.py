#!/usr/bin/env python
import time, re, subprocess, os, sys, pycurl, cStringIO, itertools, random
from urlparse import urlparse
ua='"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.13) Gecko/2009080316 Ubuntu/8.04 (hardy) Firefox/3.0.13"'
if len(sys.argv) != 2:
	print 'Usage: ./rapidshare.py url'
	exit()
class curl:
	def __init__(self):
		self.c = pycurl.Curl()
		self.c.setopt(pycurl.FOLLOWLOCATION, 1)
		self.c.setopt(pycurl.MAXREDIRS, 5)
		self.size = None
		self.downloaded = 0
		self.file = None
		self.html = cStringIO.StringIO()
	def header(self, buf):
		try:
			self.statuscode = int( re.findall(r'^HTTP\/1\.[0-2]\s*([1-5][0-9][0-9]).*\s*$', buf, re.M + re.I)[0] )
		except: pass
		try:
			contentlen = re.findall(r'^Content-Length:\s*(.*)\s*$', buf, re.M + re.I)[0]
			if self.statuscode >= 200 and self.statuscode < 300:
				self.size = int(contentlen)
		except: pass
	def start(self, url, writefunc, postfields, referer, ctimeout):
		self.c.setopt(pycurl.USERAGENT, ua)
		self.c.setopt(pycurl.URL, url)
		self.c.setopt(pycurl.WRITEFUNCTION, writefunc)
		self.c.setopt(pycurl.POSTFIELDS, postfields)
		self.c.setopt(pycurl.REFERER, referer)
		self.c.setopt(pycurl.CONNECTTIMEOUT, ctimeout)
		try:
			self.c.perform()
		except pycurl.error: pass
	def gethtml(self):
		self.html.seek(0)
		return self.html.getvalue()
	def htmlwrite(self, buf):
		print '.',
		sys.stdout.flush()
		self.html.write(buf)
		self.html.flush()
	def fwrite(self, buf):
		self.downloaded += len(buf)
		self.file.write(buf)
		self.file.flush()
		print '\rDownloaded %d%% %d/%d' % (int(100.0 * self.downloaded / self.size), self.downloaded, self.size), 
		sys.stdout.flush()
while True:
	Curl = curl()
	Curl.start(sys.argv[1], Curl.htmlwrite, 'dl.start=Free', sys.argv[1], 5)
	ff_html = Curl.gethtml()
	ff_url = re.findall('\<form\ id\=\"ff\"\ action\=\"(http.*)\"\ method\=', ff_html, re.M)
	if ff_url:
		print '\rTrying', 
		Curl.start(ff_url[0], Curl.htmlwrite, 'dl.start=Free', ff_url[0], 8)
		dlf_html = Curl.gethtml()
		dlf_url = re.findall('\<form\ name\=\"dlf\"\ action\=\"(http.*)\"\ method\=', dlf_html, re.M)
		if dlf_url:
			print 'Downloading with', dlf_url[0]
			path = urlparse(dlf_url[0]).path.split('/')
			filename = path[-1]
			randx = int(random.randint(8, 38))
			Curl.file = open(filename, 'wb')
			Curl.c.setopt(pycurl.HEADERFUNCTION, Curl.header)
			Curl.start(dlf_url[0], Curl.fwrite, 'mirror=on&x=' + str(randx) + '&y=18', ff_url[0], 8)
			Curl.file.close()
			if os.path.getsize(filename) < 1000000:
				dlf_urls = re.findall(r"dlf\.action=\\\'(http.*)\\\'", dlf_html, re.M)
				arguments = ''
				print '\nURLs:', len(dlf_urls)
				for dlf_url in dlf_urls:
					print 'Downloading', dlf_url
					randx = int(random.randint(8, 38))
					Curl.file = open(filename, 'wb')
					Curl.start(dlf_url, Curl.fwrite, 'mirror=on&x=' + str(randx) + '&y=18', ff_url[0], 8)
					Curl.file.close()
					if os.path.getsize(filename) > 1000000:
						exit()
	time.sleep(3)