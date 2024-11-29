import helper
import csv
import datetime
import os

courses_list = helper.get_course_info()

# save to csv
fieldnames = ['rgno', 'season', 'ay', 'course_no', 'old_cno', 'lang', 'section', 'title_e', 'title_j', 'schedule_meta', 'schedule', 'room', 'comment', 'maxnum', 'instructor', 'unit']

# get date (DDMMYYYY-HHMM) (e.g. 01Jan2022-0000
date = datetime.datetime.now().strftime("%d%b%Y-%H%M")

with open(f"out/courses_ay{os.environ['ACADEMIC_YEAR']}_asOf{date}.csv", 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(courses_list)