"""
Copyright (c) 2012 Anant Bhardwaj

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os, sys, pgdb, re
from stemming.porter2 import stem
from utils import *
from models import *

'''
Application Model Controller

@author: Anant Bhardwaj
@date: Aug 3, 2012
'''

class ModelController:
	def __init__(self):
		pass

	def find_post(self, post_id):
		try:
			p = Post.objects.get(id = post_id)
			return p
		except:
			print "find_post: ", sys.exc_info()
			return None



	def insert_post(self, phone_num, post):
		try:
			zipcode = extract_zipcode(post)
			p = Post(phone = phone_num, post=post, zip_code = zipcode)
			p.save()
			return p.id
		except:
			self.conn.rollback()
			print "insert_post: ", sys.exc_info()
			return -1

	
	def update_post(self, post_id, new_post):
		try:
			zipcode = extract_zipcode(post)	
			p = Post.objects.get(id = post_id)
			p.post = new_post
			p.save()
			return True
		except:
			self.conn.rollback()
			print "update_post: ", sys.exc_info()
			return False
			
	
			
	def delete_post(self, post_id):
		try:
			p = Post.objects.get(id = post_id)
			p.delete()
			return True
		except:
			self.conn.rollback()
			print "delete_post: ", sys.exc_info()
			return False
		



	def search_posts(self, query, limit=3, offset=0):
		try:
			data = None		
			q = re.findall('\w+', query)
			q = map(lambda x: x.lower(), filter(lambda x: x!='' and x!=',', map(lambda x: x.strip(), q)))
			q = '|'.join(q)				
			self.cursor.execute("SELECT post, id, ts_rank_cd(to_tsvector('english', post), query, 32 /* rank/(rank+1) */) as rank FROM posts, to_tsquery('english', '"+q+"') as query WHERE to_tsvector('english', post) @@ query ORDER BY rank DESC LIMIT " + str(limit) + " OFFSET " + str(offset))
			data = self.cursor.fetchall()
			if(not data):
				return None
			res = ""
			for d in data:
				res = res + str(d[0]) + ' (Post ID: ' + str(d[1]) + "). "
				res = res + '\n'
			return res
		except:
			print "search_posts: ", sys.exc_info()
			return None

	
			
	def find_follow_list(self, tags):
		follow_list = []
		try:
			tags = map(lambda x: str(stem(x.lower())), filter(lambda x: x!='' and x!=',', map(lambda x: x.strip(), tags)))
			for t in tags:	
				follow_tag = Follow_Tag.objects.get(tag=t)
				if(follow_tag == None):
					continue
				else:
					follow_list.append(follow_tag.follow_list)
			if(len(follow_list) > 0):
				recipients = ','.join(follow_list)
				follow_list = re.split(',', recipients)
				follow_list = list(set(filter(lambda x: x!='' and x!=',', follow_list)))
		except:
			print "find_follow_list: ", sys.exc_info()
		finally:
			return sub_list
	


	def update_follow_tag(self, tags, phone_number):
		tags = map(lambda x: str(stem(x.lower())), filter(lambda x: x!='' and x!=',', map(lambda x: x.strip(), tags)))
		for t in tags:
			try:
				follow_tag = Follow_Tag.objects.get(t)
				if(not follow_tag):
					new_follow_tag = Follow_Tag(tag = t, follow_list = str(phone_number))
					new_follow_tag.save()
				else:
					follow_list = follow_tag.follow_list
					if(phone_number not in follow_list):
						new_follow_list = follow_list + ','+ phone_number
						follow_tag.follow_list = new_follow_list
						follow_tag.update()
						
				return True
			except:
				print "update_follow_tag: ", sys.exc_info()
				return False






			
