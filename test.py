from ArrangeCourse import *

def printCourse(course):
    assert isinstance(course, Course)
    print(course.name, course.courseCode)
    print(" lec")
    lec = course.getLecSectionsCopy()

    for l in lec:
        assert isinstance(l, LecSection)
        print(" " + l.name)
        print(" " , l.times)
    tut = course.getTutSectionsCopy()
    print(" tut")
    for t in tut:
        print(" " + t.name)
        print(" " , t.times)
    print(" lab")
    lab = course.getLabSectionsCopy()
    for l in lab:
        print(" " + l.name)
        print(" " , l.times)

def printCourses(cs):
    for c in cs:
        printCourse(c)

def simpletest():
    courseList = []
    courseList += getCourses("Artificial Intelligence", "CSC384H1")
    courseList += getCourses("Natural Language Computing", "CSC401H1")
    courseList += getCourses("Introduction to Computer Science", "CSC148H1")
    courses = getCourses("Introduction to Computer Science", "CSC148H1")
    #printCourses(courses)

    #startArrange(courseList, propagators.prop_BT)
    #startArrange(courseList, propagators.prop_FC)
    startArrange(courseList, propagators.prop_GAC)
simpletest()