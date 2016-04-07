from cspbase import *
from CourseConnector import *
from CourseArrangeCSPModelBuilder import *
import propagators


def main():
    notfinish = True
    courseList = []

    while (notfinish):
        courseName = input("Course name? i.e. Artificial Intelligence\n")
        courseCode = input("General course code? i.e. CSC384H1\n")
        finish = input("finish? i.e. yes\n")
        if finish == "yes":
            notfinish = False
        courseList += getCourses(courseName, courseCode)
    startArrange(courseList)


def startArrange(courseList, numberRequire, propagator=propagators.prop_FC):
    courseBuilder = CourseModelBuilder(courseList, numberRequire)
    course_csp = courseBuilder.buildModel()
    print([str(c) for c in courseList])
    '''
    for var in course_csp.get_all_vars():
        assert isinstance(var, Variable)
        s = ""
        for d in var.domain():
            s+=str(d) + " , "
        print(s)'''
    btracker = BT(course_csp)
    # btracker.trace_on()
    btracker.bt_search(propagator)


if __name__ == '__main__':
    main()
