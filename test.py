from ArrangeCourse import *
import sys

propagatorDict = {"BT": propagators.prop_BT, "FC": propagators.prop_FC, "GAC": propagators.prop_GAC}


def printCourse(course):
    assert isinstance(course, Course)
    print(course.name, course.courseCode)
    print(" lec")
    lec = course.getLecSectionsCopy()

    for l in lec:
        assert isinstance(l, LecSection)
        print(" " + l.name)
        print(" ", l.times)
    tut = course.getTutSectionsCopy()
    print(" tut")
    for t in tut:
        print(" " + t.name)
        print(" ", t.times)
    print(" lab")
    lab = course.getLabSectionsCopy()
    for l in lab:
        print(" " + l.name)
        print(" ", l.times)


def printCourses(cs):
    for c in cs:
        printCourse(c)


# 3 Simple courses to schedule
def simpletest():
    if len(sys.argv) != 2:
        print("please enter 1 command line argument for propagator to use i.e. BT, FC, GAC")
    courseList = []
    courseList += getCourses("Artificial Intelligence", "CSC384H1")
    courseList += getCourses("Natural Language Computing", "CSC401H1")
    courseList += getCourses("Introduction to Computer Science", "CSC148H1")
    # courseList += getCourses("")
    # courses = getCourses("Introduction to Computer Science", "CSC148H1")
    # printCourses(courses)
    arg = sys.argv[1]
    print(arg)
    propagator = propagatorDict.get(arg)

    if propagator:
        startArrange(courseList, 3, propagator)
    else:
        print("No such propagator")
        # startArrange(courseList, propagators.prop_FC)
        # startArrange(courseList, propagators.prop_GAC)


# 6 Course to choose 6 courses
def moderatetest():
    if len(sys.argv) != 2:
        print("please enter 1 command line argument for propagator to use i.e. BT, FC, GAC")
    courses = [("Artificial Intelligence", "CSC384H1"), \
                ("Natural Language Computing", "CSC401H1"), \
                ("Machine Learning", "CSC411H1"), \
                ("Communication Systems", "ECE316H1"), \
                ("Computer Networks", "ECE361H1"), \
                ("Probability and Applications", "ECE302H1")]
    courseList = []
    for course in courses:
        courseList += getCourses(*course)

    # courseList += getCourses("Artificial Intelligence", "CSC384H1")
    # courseList += getCourses("Natural Language Computing", "CSC401H1")
    # courseList += getCourses("Introduction to Computer Science", "CSC148H1")

    arg = sys.argv[1]
    print(arg)
    propagator = propagatorDict.get(arg)

    if propagator:
        startArrange(courseList, 6, propagator)
    else:
        print("No such propagator")


# 10 course to choose 6 course
def complextest():
    if len(sys.argv) != 2:
        print("please enter 1 command line argument for propagator to use i.e. BT, FC, GAC")
    courses = [("Artificial Intelligence", "CSC384H1"), \
               ("Natural Language Computing", "CSC401H1"), \
               ("Machine Learning", "CSC411H1"), \
               ("Communication Systems", "ECE316H1"), \
               ("Computer Networks", "ECE361H1"), \
               ("Probability and Applications", "ECE302H1"), \
               ("Urban Economics", "ECO333H1"), \
               ("Introduction to Number Theory", "MAT315H1"), \
               ("Introduction to Databases", "CSC343H1"), \
               ("Operating System", "ECE344H1")]
    courseList = []
    for course in courses:
        courseList += getCourses(*course)

    # courseList += getCourses("Artificial Intelligence", "CSC384H1")
    # courseList += getCourses("Natural Language Computing", "CSC401H1")
    # courseList += getCourses("Introduction to Computer Science", "CSC148H1")

    arg = sys.argv[1]
    print(arg)
    propagator = propagatorDict.get(arg)

    if propagator:
        startArrange(courseList, 8, propagator)
    else:
        print("No such propagator")
        # startArrange(courseList, propagators.prop_FC)
        # startArrange(courseList, propagators.prop_GAC)


#simpletest()
moderatetest()
#complextest()
