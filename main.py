import datetime
import os
import sys
base_dir=os.path.dirname(os.path.realpath(sys.argv[0]))
file_path =os.path.join(base_dir, 'TMP.html')
Registered_ID = []
each_course_info = {}
course_name = {}
final_time = {}
drop_time = {}
course_type = {}
course_location = {}
course_weekdays = {}
course_starttime = {}
course_endtime = {}
course_meeting_time = {}
weekdy = {"M":"MO","T":"TU","W":"WE","R":"TH","F":"FR"}
wkdynum = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4}

def sort_weekdays(weekdays_str):
    weekday_order = ["MO", "TU", "WE", "TH", "FR"]
    weekdays_list = weekdays_str.split(',')
    sorted_weekdays = sorted(weekdays_list, key=lambda day: weekday_order.index(day))
    return ','.join(sorted_weekdays)

def adjust_to_weekday(start_date, target_weekday):
    start_weekday = start_date.weekday()
    if start_weekday == target_weekday:
        return start_date
    days_diff = (target_weekday - start_weekday) % 7
    adjusted_date = start_date + datetime.timedelta(days=days_diff)
    return adjusted_date

def remove_dfrt(lst): #去重复
    result = list(set(lst))
    return result

def find_id(path):
    registered_courses = []
    with open(path, 'r') as file:
        for line in file:
            if 'CourseDetails.t' in line and '.REGISTRATION_STATUS = "Registered"' in line:
                start_idx = line.find('CourseDetails.t') + len('CourseDetails.t')
                end_idx = line.find('.REGISTRATION_STATUS')
                course_id = line[start_idx:end_idx]
                registered_courses.append(course_id)
            if 'CourseDetails.t' in line and '.REGISTRATION_STATUS = "W' in line:
                start_idx = line.find('CourseDetails.t') + len('CourseDetails.t')
                end_idx = line.find('.REGISTRATION_STATUS')
                course_id = line[start_idx:end_idx]
                registered_courses.append(course_id)
    return registered_courses

Registered_ID = find_id(file_path)
Registered_ID = remove_dfrt(Registered_ID)
#print(Registered_ID)
def combine_course_time(str1, str2):
    return str1[:8]+str2[8:]

def final_time_export(date_str):
    if date_str == "null":
        return "null"
    parts = date_str.split(",")
    year = parts[0]
    month = str(int(parts[1]) + 1).zfill(2)
    day = parts[2].zfill(2)
    hour = parts[3].zfill(2)
    minute = int(parts[4])
    second = int(parts[5])
    minute =minute - 10#提前10分钟提醒防止考试被抓
    if minute < 0:
        hour = str(int(hour) - 1).zfill(2)
        minute += 60
    minute = str(minute).zfill(2)
    return f"{year}{month}{day}T{hour}{minute}{second:02}"

def drop_date_export(date_str):
    #print("测速：               ",date_str)
    if date_str == "null":
        return "null"
    date_str = date_str.replace("(", "").replace(" - 1)", "")
    parts = date_str.split(",")
    year = parts[0]
    month = parts[1].zfill(2)
    day = parts[2].zfill(2)
    hour = parts[3].zfill(2)
    minute = parts[4].zfill(2)
    second = parts[5].zfill(2)
    return f"{year}{month}{day}T{hour}{minute}{second}"

def course_date_export(date_str):
    date_str = date_str.replace("(", "").replace(" - 1", "").replace(")", "")
    parts = date_str.split(",")
    year = parts[0]
    month = parts[1].zfill(2)
    day = parts[2].zfill(2)
    hour = parts[3].zfill(2)
    minute = parts[4].zfill(2)
    second = parts[5].zfill(2)
    return f"{year}{month}{day}T{hour}{minute}{second}"

def weekdays_export(date_str):
    date_str = date_str.replace("M", 'MO').replace("T", 'TU').replace("W", 'WE').replace("R", 'TH').replace("F", 'FR')
    return date_str

def find_all_positions(char, string):
    positions = []
    start_index = 0
    while True:
        index = string.find(char, start_index)
        if index == -1:
            break
        positions.append(index+len(char)-1)
        start_index = index + 1
    return positions

def final_exam_output(numbers):
    header = "BEGIN:VEVENT\n"
    footer = "END:VEVENT\n\n"
    for number in numbers:
        if final_time[number] == "null":
            continue
        dtstart = "DTSTART;TZID=America/Los_Angeles:"+final_time[number]+"\n"
        dtend = "DTEND;TZID=America/Los_Angeles:"+final_time[number][:len(final_time[number])-1]+"1\n"
        summary = "SUMMARY:"+course_name[number]+" Final Exam\n"
        with open(f"{file_path}.ics", 'a') as file:
            file.write(header)
            file.write(dtstart)
            file.write(dtend)
            file.write(summary)
            file.write(footer)

def drop_export(numbers):
    header = "BEGIN:VEVENT\n"
    footer = "END:VEVENT\n\n"
    for number in numbers:
        if drop_time[number] == "null":
            continue
        dtstart = "DTSTART;TZID=America/Los_Angeles:" + drop_time[number] + "\n"
        dtend = "DTEND;TZID=America/Los_Angeles:" + drop_time[number][:len(drop_time[number]) - 6] + "235959\n"
        summary = "SUMMARY:" + course_name[number] + " drop day\n"
        with open(f"{file_path}.ics", 'a') as file:
            file.write(header)
            file.write(dtstart)
            file.write(dtend)
            file.write(summary)
            file.write("TRANSP:FREE\n")
            file.write(footer)

def course_output(numbers):
    header = "BEGIN:VEVENT\n"
    footer = "END:VEVENT\n\n"
    for number in numbers:
        for tp in range(0,course_meeting_time[number]):
            meetingname = f"{number}{tp}"
            if course_starttime[meetingname] == "null":
                continue
            if course_weekdays[meetingname] == "null":
                continue
            startday = datetime.datetime(int(course_starttime[meetingname][:4]),int(course_starttime[meetingname][4:6]),int(course_starttime[meetingname][6:8]))
            coursedays=sort_weekdays(weekdays_export(course_weekdays[meetingname]))
            rightday=adjust_to_weekday(startday, wkdynum[coursedays[0:2]])
            dtstart = "DTSTART;TZID=America/Los_Angeles:" + rightday.strftime('%Y%m%d')+course_starttime[meetingname][8:] + "\n"
            classover = combine_course_time(rightday.strftime('%Y%m%d'), course_endtime[meetingname])
            dtend = "DTEND;TZID=America/Los_Angeles:" + classover + "\n"
            location = "LOCATION:"+course_location[meetingname]+"\n"
            rrule=f"RRULE:FREQ=WEEKLY;UNTIL={course_endtime[meetingname][:9]}235959Z;BYDAY={sort_weekdays(weekdays_export(course_weekdays[meetingname]))}\n"
            summary = "SUMMARY:"+course_name[number]+' '+course_type[meetingname]+'\n'
            with open(f"{file_path}.ics", 'a') as file:
                file.write(header)
                file.write(dtstart)
                file.write(dtend)
                file.write(summary)
                file.write(location)
                file.write(rrule)
                file.write(footer)

def a_to_b(s, a, b):
    start_index = s.find(a)
    if start_index == -1:
        return "null",-1
    end_index = s.find(b, start_index + len(a))
    if end_index == -1:
        return "null",-1
    result = s[start_index + len(a):end_index]
    return result, end_index+1

def find_courses_details(path, numbers):
    with open(path, 'r') as file:
        content = file.read()
    for number in numbers:
        coursenum=0
        target_str1 = f"\"ID\":\"{number}\""
        target_str2 = f"CourseDetails.t{number}.REGISTRATION_STATUS = "
        lines_in_range, tmp = a_to_b(content, target_str1, target_str2)
        each_course_info[number] = lines_in_range
        ##print(each_course_info[number])
        global quarter_time
        quarter_time,tmp= a_to_b(each_course_info[number],'COURSE_MATERIALS_TERM":"','"')
        #print("学期：",quarter_time)
        a,tmp=a_to_b(each_course_info[number], '"SUBJECT_CODE":\"', '"')
        b,tmp=a_to_b(each_course_info[number], '"COURSE_NUMBER":\"', '"')
        c,tmp=a_to_b(each_course_info[number], '"SECTION_NUMBER":\"', '"')
        course_name[number] = a + " " + b + " " + c
        final_time[number], tmp = a_to_b(each_course_info[number], ',"FINAL_EXAM_STARTDATE":new Date(', ')')
        final_time[number] = final_time_export(final_time[number])
        drop_time[number],tmp = a_to_b(each_course_info[number],",\"DROP_DATE\":new Date(",")\n")
        drop_time[number]=drop_date_export(drop_time[number])
        ##print()
        ##print("课程名字：",course_name[number])
        ##print("期末时间：",final_time[number])
        ##print("drop时间：",drop_time[number])
        each_course_info[number],tmp = a_to_b(each_course_info[number],'"MEETINGS":[','"REGISTRATION_STATUS":')
        ##print(each_course_info[number])
        posi = find_all_positions('"TYPE":"',each_course_info[number])
        meetingnum=len(posi)
        course_meeting_time[number] = meetingnum
        ##print(course_meeting_time[number])
        ##print("          :",number)
        ##print("课程次数",course_meeting_time[number])
        for tp in range(0,meetingnum):
            meetingname = f"{number}{tp}"
            course_type[meetingname],tmp = a_to_b(each_course_info[number][posi[tp]:],'"','"')
            #print("课程类型：",course_type[meetingname])
        posi = find_all_positions('"LOCATION":"',each_course_info[number])
        for tp in range(0,meetingnum):
            meetingname = f"{number}{tp}"
            course_location[meetingname],tmp = a_to_b(each_course_info[number][posi[tp]:],'"','"')
            #print("课程地址：",course_location[meetingname])
        posi = find_all_positions(',"WEEKDAYS":"', each_course_info[number])
        for tp in range(0,meetingnum):
            meetingname = f"{number}{tp}"
            course_weekdays[meetingname],tmp = a_to_b(each_course_info[number][posi[tp]:],'"','"')
            if course_weekdays[meetingname]=="":
                course_weekdays[meetingname]='null'
            #print("课程日期：",course_weekdays[meetingname])
        posi = find_all_positions('"STARTTIME"', each_course_info[number])
        for tp in range(0, meetingnum):
            meetingname = f"{number}{tp}"
            course_starttime[meetingname], tmp = a_to_b(each_course_info[number][posi[tp]:], 'te(', ',0)')
            if tmp==-1:
                course_starttime[meetingname]='null'
                continue
            course_starttime[meetingname]=course_date_export(course_starttime[meetingname])
            #print("课程开始：",course_starttime[meetingname])
        posi = find_all_positions('"ENDTIME"', each_course_info[number])
        for tp in range(0, meetingnum):
            meetingname = f"{number}{tp}"
            course_endtime[meetingname], tmp = a_to_b(each_course_info[number][posi[tp]:], 'te(', ',0)')
            if tmp==-1:
                course_endtime[meetingname]='null'
                continue
            course_endtime[meetingname]=course_date_export(course_endtime[meetingname])
            #print("课程结束：",course_endtime[meetingname])

find_courses_details(file_path, Registered_ID)
#时间处理
#20240925T181000
#2024年9月25日T18点10分0秒

def ics_export():
    header = f"BEGIN:VCALENDAR\nCALSCALE:GREGORIAN\nVERSION:2.0\nPRODID:rzjin@ucdavis.edu\nMETHOD:PUBLISH\n\n"
    footer = "\nEND:VCALENDAR"

    with open(f"{file_path}.ics","w") as file:
        file.write(header)
    course_output(Registered_ID)
    final_exam_output(Registered_ID)
    drop_export(Registered_ID)
    with open(f"{file_path}.ics","a") as file:
        file.write(footer)

#print(course_starttime)

ics_export() 