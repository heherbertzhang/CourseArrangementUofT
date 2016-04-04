import urllib.request
import urllib.parse
import json
from CourseClass import *

api_key = 'DjMlF9rT1Bgaz0rJPUCK5J15iy7aAh9Q'  # api key for cobalt
requestCourseIdUrl = 'https://cobalt.qas.im/api/1.0/courses/{}?key={}'
searchCourseUrl = 'https://cobalt.qas.im/api/1.0/courses/search?q="{}"&key={}'

def getCourses(courseName, courseCode):
    # example: Artificial Intelligence, code = CSC384H1
    courseList = []
    coursesJson = searchCourse(courseName)
    for courseJson in coursesJson:
        if courseJson["code"].startswith(courseCode):
            course = parseCourseJson(courseJson)
            courseList.append(course)
    return courseList

def searchCourse(courseName):
    # example: Artificial Intelligence
    url = searchCourseUrl.format(urllib.parse.quote(courseName), api_key)
    print(url)
    #u ='https://cobalt.qas.im/api/1.0/courses/search?q="artificial%20intelligence"&key=DjMlF9rT1Bgaz0rJPUCK5J15iy7aAh9Q'
    try:
        response = urllib.request.urlopen(url)
        decode = response.read().decode()
        #print(decode)
        data = json.loads(decode)
        #print(data)
        return data
    except Exception as e:
        print('cannot find course {} due to error: '.format(courseName), e)
        return None

def getCourseForId(course_id):
    #course id example: ECE311H1F20159 must end with 20159
    url = requestCourseIdUrl.format(course_id, api_key)
    #a = 'https://cobalt.qas.im/api/1.0/courses/CSC148H1F20159?key=DjMlF9rT1Bgaz0rJPUCK5J15iy7aAh9Q'
    try:
        response = urllib.request.urlopen(url)
        decode = response.read().decode()
        #print(decode)
        data = json.loads(decode)
        #print(data)
        return data
    except Exception as e:
        print('cannot find course {} due to error: '.format(course_id), e)
        return None

def parsePrereqOrExclusion(prereq):
    if isinstance(prereq, str):
        return [prereq[0:9]]
    elif isinstance(prereq, list) or isinstance(prereq, tuple):
        return [p[0:9] for p in prereq]

def parseCourseJson(jsonobj):
    print(jsonobj)
    courseCode = jsonobj["code"]
    courseName = jsonobj["name"]
    prerequisites = jsonobj["prerequisites"]
    prerequisites = parsePrereqOrExclusion(prerequisites)
    exclusions = jsonobj["exclusions"]
    exclusions = parsePrereqOrExclusion(exclusions)
    term = jsonobj["term"]
    sections = jsonobj["meeting_sections"]
    lecSections = []
    tutSections = []
    labSections = []
    if isinstance(sections, list):
        for sectionj in sections:
            section = parseSection(sectionj, term)
            if isinstance(section, LecSection):
                lecSections.append(section)
            elif isinstance(section, TutSection):
                tutSections.append(section)
            elif isinstance(section, LabSection):
                labSections.append(section)
    return Course(courseName, courseCode, term, lecSections, tutSections,
                  labSections, prerequisites, exclusions)


def parseSection(section, term):
    sectionName = section["code"]
    times = section["times"]
    instructor =""
    if section["instructors"]:
        instructor = section["instructors"][0]
    timelist = []
    for time in times:
        timelist += parseTime(time, term)
    if sectionName.startswith('L'):
        return LecSection(sectionName, timelist, instructor)
    elif sectionName.startswith('T'):
        return TutSection(sectionName, timelist, instructor)
    elif sectionName.startswith('P'):
        return LabSection(sectionName, timelist, instructor)
    else:
        print("unknown section")
        return Section(sectionName, timelist, instructor)

def parseTime(time, term):
    '''
    {
          "day":"MONDAY",
          "start":10,
          "end":11,
          "duration":1,
          "location":"RW 110"
    }
    return a list of time without set term yet
    '''
    day = time["day"]
    start = time["start"]
    end = time["end"]
    duration = time["duration"]
    result = []
    for i in range(duration):
        hour = start + i
        result.append(term+"-"+day+"-"+str(hour)) # the hour is start time and duration for 1 hour
    return result
'''
for c in getCourses("artificial intelligence", "CSC384H1"):
    print(c)'''