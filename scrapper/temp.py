from bs4 import BeautifulSoup
import re
import MySQLdb
import datetime
import requests
import urllib
import json
import hashlib
import os

today = datetime.datetime.now().strftime("%Y%m%d")
db = MySQLdb.connect("localhost","root","98527410.0+","studyportal")
url_search_courses="https://channeli.in/lectut_api/search/?"
cursor = db.cursor()
cursor.execute("SELECT * FROM courses;")
url_files_list="https://channeli.in/lectut_api/files/"
row = cursor.fetchone()
url_file_dl = "https://channeli.in/lectut_api/download/"

db2= MySQLdb.connect("localhost","root","98527410.0+","studyportal")
cursor_for_update = db2.cursor()
##################################################function!!
def file_dl(file_sub_list,file_type,new_course_code,new_course_dep):
	if file_sub_list:
		for file_lectut in file_sub_list:
				update=False
				file_name = file_lectut["upload_file"]
				
				print(file_name)
				
				cursor_for_update.execute("SELECT * FROM files")
				file_in_db = cursor.fetchone()
				#checks whether the file is already present or not
				while file_in_db is not None:
				
					if file_in_db[1] == file_name:#whether the new file is actually new or not
						if int(file_lectut["datetime_created"][0:4]) > int(file_in_db["date"][0:4]):       ##check for correct year comparison
							update=True
							file_name=file_name+file_lectut["datetime_created"][0:4]
						else:
							update=False
							file_in_db= cursor.fetchone()
					else: 
						update=True
						file_in_db = cursor.fetchone()

					
					

				if update==True:
					address_for_hash="/uploads/"+new_course_dep.upper()+"/"+new_course_code+"/temp/"+"/"+file_name
					m=hashlib.md5()#############################upload temp directory?????
					m.update(address_for_hash)
					filehash=m.hexdigest()
					dl_dir="./uploads/"+new_course_dep.upper()+"/"+new_course_code+"/sdslabs/"+file_type+"/"
					if not os.path.exists(dl_dir):
						os.makedirs(dl_dir)
					
					os.chdir(dl_dir)
					#dl_here = os.path.join(dl_path, file_name) tried but failed
					urllib.urlretrieve(url_file_dl+str(file_lectut["id"]),
					file_name)#what is hash?
					os.chdir("../../../../../")
					
					cursor_for_update.execute("INSERT INTO files\
					(title, \
					department, \
					course,\
					location,\
					date,\
					uploader,\
					contentType,\
					description,\
					hash,upvotes,\
					downvotes,\
					no_of_downloads)\
					VALUES ({},{},{},{},{},{},{},{},{},{},{})".format(
				   file_name,
				   new_course_dep,
				   new_course_code,
				   "/uploads/"+new_course_dep.upper()+"/"+new_course_code+"/sdslabs/"+file_type+"/"+file_name,
				   int(today),
				   "sdslabs",
				   file_type,
				   file_lectut["file_type"],
				   filehash,0,0,0))
					print("file successfully downloaded:"+file_name)

##########################################main program--


  ###doubt!!1
		
while row is not None:
	name_of_course = urllib.urlencode({"q":row[4].replace(".","")})
	search_course_results=requests.post(url_search_courses+name_of_course)
	
	course_list = json.loads(search_course_results.text)["courses"]
	if course_list :
		#print(course_list)
		
		course_details = course_list[0]
		
		old_course_code = row[2]
		old_course_dep = row[1]
		new_course_code = course_details["code"]
		new_course_dep = new_course_code[0:2].lower()
		new_course_id= course_details["id"]
		print(new_course_dep)
		
		
		#should i just verified =1?
		cursor_for_update.execute("UPDATE courses SET \
		course='{}',\
		department='{}',\
		verified=0,\
		verifier='sdslabs' \
		WHERE course='{}' ".format(
		new_course_code,
		new_course_dep,
		old_course_code))
		
		
		cursor_for_update.execute("UPDATE files SET \
		department='{}',\
		course='{}' \
		WHERE course='{}'".format(new_course_dep,
		new_course_code,
		old_course_code))
		
		# just check whether old file ought to be deleted or not 
		# ensure the hash algo
		# check for correct content type 
		# review it	
		
		#files list
		files_list_results = requests.post(url_files_list+str(new_course_id))
		files_list = json.loads(files_list_results.text)
		print(files_list)
		# for current files
		file_dl(files_list["currentFiles"]["Exam Papers"],"exam",new_course_code,new_course_dep)
		file_dl(files_list["currentFiles"]["Solution"],"exam",new_course_code,new_course_dep)
		file_dl(files_list["currentFiles"]["Lecture"],"professor",new_course_code,new_course_dep)
		file_dl(files_list["currentFiles"]["Tutorial"],"tutorials",new_course_code,new_course_dep)
		#for archive files
		file_dl(files_list["archiveFiles"]["Exam Papers"],"exam",new_course_code,new_course_dep)
		file_dl(files_list["archiveFiles"]["Solution"],"exam",new_course_code,new_course_dep)
		file_dl(files_list["archiveFiles"]["Lecture"],"professor",new_course_code,new_course_dep)
		file_dl(files_list["archiveFiles"]["Tutorial"],"tutorials",new_course_code,new_course_dep)
		
			
		db2.commit()
		
	row =cursor.fetchone()

cursor.close()
db.close()
