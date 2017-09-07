from bs4 import BeautifulSoup
import re
import MySQLdb
import datetime
import requests
import urllib
import json

today = datetime.datetime.now().strftime("%Y%m%d")
db = MySQLdb.connect("localhost","root","98527410.0+","studyportal")
url_search_courses="https://channeli.in/lectut_api/search/?"
cursor = db.cursor()
cursor.execute("SELECT * FROM courses")
url_files_list="https://channeli.in/lectut_api/files/"
row = cursor.fetchone()
url_file_dl = "https://channeli.in/lectut_api/download/"
while row is not None:
	name_of_course = urllib.urlencode({"q":row[4].replace(".","")})
	search_course_results=requests.post(url_search_courses+name_of_course)
	course_list = json.loads(search_course_results.text)["courses"]
	if not course_list is None:
		print("Ya hoo")
	
	if not course_list:
		course_details = course_list[0]
		old_course_code = row[2]
		old_course_dep = row[1]
		new_course_code = course_details["code"]
		new_course_dep = new_course_code[0:1].lower()
		new_course_id= course_details["id"]
		db2= MySQLdb.connect("localhost","root","98527410.0+","studyportal")
		cursor_for_update = db2.cursor()  ###doubt!!1
		cursor_for_update.execute("UPDATE courses SET course='{}',department='{}',verified=0,verifier=''WHERE course='{}'; ".format(new_course_code,new_course_dep,old_course_code))
		
		cursor_for_update.execute("UPDATE files SET department='{}',course='{}'WHERE course='{}';".format(new_course_dep,new_course_code,old_course_code))
		##doubt currentFiles and ArchiveFiles both? ## what if name of slide clashes .what the heck are questions in lectut #solutions paradox 
		db2.commit()
		
		#files list
		files_list_results = requests.post(url_files_list+new_course_id)
		files_list = json.loads(files_list_results)
		no_of_files = len(files_list)
		
		for file_sub_list in files_list["currentFiles"]:
			if file_sub_list is not None:
				if file_sub_list[0]["upload_type"]=="Lecture":
					file_type="professor"
				elif file_sub_list[0]["upload_type"]=="Solution":
					file_type="notes"
				elif file_sub_list[0]["upload_type"]=="Exam Papers":
					file_type="exam"
				elif file_sub_list[0]["upload_type"]=="Tutorial":
					file_type="tutorials"
			for file in file_sub_list:
				update=False
				file_name = file["upload_file"]

				cursor_for_update.execute("SELECT * FROM files")
				row_for_file_in_db = cursor.fetchone()
				for file_in_db in row_for_file_in_db["title"]:
					if file_in_db == file_name:
						if file["datetime_created"][0:3] > file_in_db["date"][0:3]:       ##check for correct year comparison
							update=True
							file_name=file_name+"Year_of_new_file"
						break
					else: 
						update=True
						row_for_filename = cursor.fetchone()

					if update==True:
						break


				urllib.request.urlretrieve(url_file_dl+file["id"],"uploads/"+file["upload_file"])#what is hash?

				cursor_for_update.execute("INSERT INTO files (title,department,course,location,date,uploader,contentType,description,hash,upvotes,downvotes,no_of_downloads) VALUES ({},{},{},{},{},{},{},{},{},{},{},{});".format(file_name,new_course_dep,new_course_code,"/"+"uploads/"+file["upload_file"],int(today),"sdslabs",file_type,file["file_type"],"",0,0,0))
		
		
		
		for file_sub_list in files_list["archiveFiles"]:
			if file_sub_list is not None:
				if file_sub_list[0]["upload_type"]=="Lecture":
					file_type="professor"
				elif file_sub_list[0]["upload_type"]=="Solution":
					file_type="notes"
				elif file_sub_list[0]["upload_type"]=="Exam Papers":
					file_type="exam"
				elif file_sub_list[0]["upload_type"]=="Tutorial":
					file_type="tutorials"
			for file in file_sub_list:
				
				urllib.request.urlretrieve(url_file_dl+file["id"],"uploads/"+file["upload_file"])#what is hash?

				cursor_for_update.execute("INSERT INTO files (title,department,course,location,date,uploader,contentType,description,hash,upvotes,downvotes,no_of_downloads) VALUES ({},{},{},{},{},{},{},{},{},{},{},{});".format(file_name,new_course_dep,new_course_code,"/"+"uploads/"+file["upload_file"],int(today),"sdslabs",file_type,file["file_type"],"",0,0,0))




	row =cursor.fetchone()
cursor.close()
db.close()











'''
urllib.urlencode() #use this
r = requests.get(url_search_courses)

data = r.text

soup = BeautifulSoup(data,"lxml")
results = soup.findAll("a",{"href":re.compile("/departments/*")})

dep_code_regex=re.compile("([A-Z][A-Z])|([A-Z][A-Z][A-Z])")
for deps in results:
	print(deps.contents[0].decode('utf-8'))
	m = re.match(deps['href'][0])
	
	print(m.group(0))
'''
'''

db = MySQLdb.connect("localhost","root","98527410.0+","studyportal")

cursor = db.cursor()

sql ="""INSERT INTO courses() VALUES ()"""

try:
	cursor.execute(sql)
	db.commit()
except:
	db.rollback()

db.close()
'''
