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
        .update({"schedule": course['schedule']})
        .eq("rgno", course['rgno'])
        .execute()
    )
    print(f'{response=}')