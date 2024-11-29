import os
from supabase import create_client, Client
from dotenv import load_dotenv
import helper

# Load environment variables from the .env file
load_dotenv()

# Initializing Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

courses_list = helper.get_course_info()
print(f'{courses_list=}')
for course in courses_list:
    print(f'Inserting course: {course}')
    response = (
        supabase.table("courses")
        .insert(course)
        .execute()
    )
    print(f'{response=}')

# response = (
#     supabase.table("courses")
#     .insert({'rgno': 11244, 'ay': 2024, 'season': 'Spring', 'course_no': 'LNG102', 'lang': 'J', 'title_e': 'Introduction to Linguistics II', 'title_j': '言語学入門 II', 'schedule': [{'time': 3, 'unit': 'M'}, {'time': 3, 'unit': 'W'}, {'time': 3, 'unit': 'F'}], 'instructor': 'YOSHIDA, Tomoyuki', 'unit': '3', 'room': 'SH-N204'})
#     .execute()
# )
# print(response)
# response = supabase.table("courses").select("*").execute()
# print(response)