import scrape
from bs4 import BeautifulSoup
import re
import pandas as pd

# Fill 0 for first 10 ids
def convert_to_target(num):
    if num <10:
        res = str(num).zfill(2)
    else:
        res = str(num)
    return res


def parse_schedule(schedule_raw):
    """
    Parses a raw schedule string into a structured format.
    Handles:
      - Alternatives enclosed in angle brackets: <>
      - Parentheses for grouping entries: ()
      - Flags marked with an asterisk (*)
    """
    structured_schedule = []

    # Remove parentheses and process their contents
    schedule_clean = schedule_raw.replace('(', '').replace(')', '')

    # Split by commas, spaces, or 'or'
    parts = re.split(r',\s*|\sor\s|<|>\s*', schedule_clean)
    parts = list(filter(None, parts)) # Remove empty strings
    print(f'{parts=}')

    for part in parts:
        flag = False
        if part.startswith('*'):  # Detect flag
            flag = True
            part = part[1:]  # Remove the asterisk for processing
        try:
            time, day = part.split('/', 1)  # Limit split to 1 to prevent too many values
            structured_schedule.append({
                "time": int(time),
                "day": day,
                "flag": flag
            })
        except ValueError:
            # Handle cases where the split results in an unexpected format
                print(f"Warning: Skipping malformed schedule entry: {part}")
                continue

    return structured_schedule

def get_course_info():
    raw = scrape.get_courses()
    full = BeautifulSoup(raw, 'lxml')
    courses = full.find('tr').find_all('tr')
    # print(f'courses: {courses}')
    res_list = []
    target_number = 3
    labels = ["rgno", "season", "ay", "course_no", "lang", "title_e", "title_j", "schedule", "room", "instructor", "unit"]
    labels_original = ["rgno", "season", "ay", "course_no", "old_cno", "lang", "section", "title_e", "title_j", "schedule", "room", "comment", "maxnum", "instructor", "unit"]

    for i in range(len(courses)):
        # In case of not scraping "ALL" courses but "10"
        # if i == 0 or i == 1 or i == 2 or i == 13 or i ==14:
        #     continue

        # In case of not scraping "ALL" courses but "50"
        # if i == 0 or i == 1 or i == 2 or i == 53 or i == 54:
        #     continue

        # In case of scraping "ALL"
        if i == 0 or i == 1:
            continue

        # Set Course number
        target_string = convert_to_target(target_number)
        tar_id_no_label = "ctl00_ContentPlaceHolder1_grv_course_ctl" + target_string + "_lbl_"
        res_dict = {}
        for label in labels:
            # Generate label
            tar_id = tar_id_no_label + label
            print(f'{tar_id=}')
            # Find element
            
            res = courses[i].find('span', {'id': tar_id}).getText()
            print(f'{res=}')
            if label == "schedule":
                # Parse the schedule into structured format
                res_dict["schedule"] = parse_schedule(res)
            elif label == "unit":
                res_dict[label] = res.replace('(','').replace(')','')
            else:
                res_dict[label] = res
        # res_dict["ids"]=int(res_dict["rgno"])
        # res_list.append(json.dumps(res_dict,ensure_ascii=False))
        res_list.append(res_dict)
        # print("\n")
        target_number = target_number + 1
    return res_list

def get_course_list():
    x = get_course_info()
    regs=[]
    for x in regs:
        regs.append(x['rgno'])
    return regs

def get_ela_classrooms():
    day_map = {
        1:'M',
        2:'Tu',
        3:'W',
        4:'Th',
        5:'F',
        6:'Sa'
    }
    room_map = {}
    raw = scrape.get_ela()
    for section in raw:
        tables = pd.read_html(section)[0]
        title = tables.loc[0][0]
        if title == '(Regular)':
            date_range = range(1,6)
            time_range = range(1,8)
            for i in date_range:
                for j in time_range:
                    pp = tables.loc[j][i]
                    if str(pp) != 'nan' and pp[-5] == ('H' or 'I' or 'T'):
                        # print("{}/{} : {}".format(j,day_map[i],pp[-5:]))
                        period = "{}{}".format(day_map[i].lower(),j)
                        room_map.setdefault(str(pp[-5:]),[]).append(period)

        elif title == 'Component':
            try:
                col_range = range(3,4)
                row_range = range(1,25)
                for i in col_range:
                    for j in row_range:
                        pp = tables.loc[j][i]
                        # print("{}/{} : {}".format(tables.loc[j][i][:1],tables.loc[j][i][-1],tables.loc[j][i+1]))
                        room_map.setdefault(tables.loc[j][i+1],[]).append("{}{}".format(tables.loc[j][i][:1].lower(),tables.loc[j][i][-1]))
            except:
                continue
        elif title == 'Instructor':
            col_range = range(1,5)
            row_range = range(2,10)
            for col in col_range:
                period = (tables.loc[1][col])
                for row in row_range:
                    pp = tables.loc[row][col]
                    date = "tu" if period[0] == "T" else period[0]
                    # print("{}/{} : {}".format(date,period[-1],pp))
                    room_map.setdefault(pp,[]).append("{}{}".format(date.lower(),period[-1]))
        else:
            print('Error')
    return room_map

def get_open_classrooms(term_value ="all"):
    raw = scrape.get_courses(term_value)
    full = BeautifulSoup(raw,'lxml')
    courses = full.find('tr').find_all('tr')
    res_list = []
    target_number= 2
    courses.pop(0)
    classrooms = {}
    labels = ["rgno","season","ay","course_no","old_cno","lang","section","title_e","title_j","schedule","room","comment","maxnum","instructor","unit"]
    for i in range(len(courses)):
        # Set Course number
        target_string = convert_to_target(target_number)
        id = "ctl00_ContentPlaceHolder1_grv_course_ctl" + target_string + "_lbl_"
        res_dict = {}
        for j in range(len(labels)):
            # Generate label
            tarID = id + labels[j]
            # Find element
            res = courses[i].find('span',{'id': tarID}).getText()
            res_dict[labels[j]] = res
        res_dict["id"]=int(res_dict["rgno"])
        cno = res_dict['course_no']
        schedule = res_dict['schedule']
        room = res_dict['room']
        shelist = []
        schedule = schedule.lower()
        schedule = schedule.replace("(","")
        schedule = schedule.replace(")","")
        schedule = schedule.replace("*","l")
        shelist = schedule.split(',')
        tag = []
        dictobj = {}
        if room != '':
            rooms = room.split(',')
            for r in rooms:    
                for period in shelist:
                    if period != '':
                        period = period.split('/')
                        text = period[1] + period[0]
                        if text[-2] == "l":
                            classrooms.setdefault(r,[]).append(period[1]+"4")
                        classrooms.setdefault(r,[]).append(text)
                # print(f'room {r} is used by {cno} for {shelist}')
        #print("\n")
        target_number = target_number + 1
    ela = get_ela_classrooms()
    for k in ela.keys():
        period_list = ela[k]
        for p in period_list:
            classrooms.setdefault(k,[]).append(p)

    list_keys = list(classrooms.keys())
    sorted_list = sort_list(list_keys)
    for t in sorted_list:
        filter_list = ""
        for time in classrooms[t]:
            filter_list = filter_list + time + " "
        
        print(f'<div class="classroom {filter_list}">\n\t{t}\n</div>')
    return res_list

def sort_list(l):
    l.sort()
    return l