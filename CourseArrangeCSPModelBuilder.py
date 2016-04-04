from CourseClass import *
from cspbase import *
from functools import partial


class CourseModelBuilder:
    def __init__(self, courseList):
        self.timeDic = {}
        self.courseList = courseList
        terms = self.getTerms()
        # build time variables
        # one day start at 9am-10am timeslot and end at 8pm-9pm (20-21)
        weekdays = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
        for term in terms:
            for day in weekdays:
                for i in range(9, 21):
                    time_name = term + "-" + day + "-" + str(i)
                    #print("time name", time_name)
                    v = Variable(time_name)
                    self.timeDic[time_name] = v
        self.addDomainForTimeVars()

    def createNumCourseRequire(self, number):
        c = Constraint("number of courses", list(self.timeDic.values()))
        f = partial(numberReqFunc, number)
        #print("test fc", f(["no", self.courseList[0], self.courseList[0], "no"]))
        c.add_satisfy_function(f)
        return c

    def addDomainForTimeVars(self):
        #add None choice
        none = "No Course"#Course("None", "No Course", "", [], [], [], [], [])
        for timeVar in list(self.timeDic.values()):
            timeVar.add_domain_values([none])
        # add domain for time
        for course in self.courseList:
            assert isinstance(course, Course)
            lecs, tuts, labs = course.getAllSectionCopy()
            sects = lecs + tuts + labs
            for sect in sects:
                #assert isinstance(sect, Section)
                for time in sect.times:
                    var = self.getVariableForTime(time)
                    assert isinstance(var, Variable)
                    # domain is tuple of course and sec
                    var.add_domain_values([(course, sect)])

    def getTerms(self):
        terms = set()
        for course in self.courseList:
            assert isinstance(course, Course)
            terms.add(course.term)
        print("terms", terms)
        return terms

    def buildModel(self):
        vars = list(self.timeDic.values())
        csp = CSP("model1:normal model with binary constraints", vars)
        # for SS
        for course in self.courseList:
            SSCs = self.create_sameSectionConstraint(course)
            csp.add_constraints(SSCs)
        # for ME
        MEPairs = self.findMEpairs()
        for pair in MEPairs:
            MECs = self.create_all_MEConstraints(pair)
            csp.add_constraints(MECs)
        # for PR
        for course in self.courseList:
            prereqs = self.find_prereq(course) # a list of list
            PRCs = self.create_all_prConstraints(course, prereqs)
            csp.add_constraints(PRCs)
        # for number of courses
        c = self.createNumCourseRequire(3)
        csp.add_constraint(c)
        return csp

    def findMEpairs(self):
        '''return a list of set'''
        MEpairs = []
        MECourses = list(self.courseList)
        while MECourses:
            course = MECourses.pop(0)
            assert isinstance(course, Course)
            MElist = course.getExclusionCopy()
            pairs = set()
            pairs.add(course)
            for c in MECourses:
                assert isinstance(c, Course)
                if c.getGeneralCourseCode() in MElist:
                    pairs.add(c)
            if len(pairs) > 1 and pairs not in MEpairs:
                MEpairs.append(pairs)

        # add ME for same course different term courses
        sameCodeCourses = list(self.courseList)
        while sameCodeCourses:
            course = sameCodeCourses.pop(0)
            generalCode = course.getGeneralCourseCode()
            pairs = set()

            assert isinstance(course, Course)
            for c in sameCodeCourses:
                if c.getGeneralCourseCode() == generalCode:
                    pairs.add(c)
            for rc in pairs:
                sameCodeCourses.remove(rc)
            if len(pairs) > 0:
                pairs.add(course)
                MEpairs.append(pairs)
        for p in MEpairs:
            print("pair start")
            for pp in p:
                print("ME!!!", pp)
        return MEpairs


    def create_all_MEConstraints(self, MElist):
        MEl = list(MElist)
        cs = []
        while MEl:
            course = MEl.pop(0)
            for c in MEl:
                cs += self.create_MutualExclusiveConstraints(course, c)
        return cs

    def create_MutualExclusiveConstraints(self, course1, course2):
        assert isinstance(course1, Course)
        assert isinstance(course2, Course)

        times1 = self.getAllTimeVarForCourse(course1)
        times2 = self.getAllTimeVarForCourse(course2)
        return self.ME_for_2time(course1, course2, times1, times2)

    def ME_for_2time(self, Alter1, Alter2, times1, times2):
        constraints = []
        for time1 in times1:
            for time2 in times2:
                cname = "ME:{},{}".format(str(Alter1), str(Alter2))
                constraint = Constraint(cname, [time1, time2])
                # lambda vals: (vals[0] == course1 and vals[1] != course2) \
                #            or (vals[1] == course2 and vals[0] != course1) \
                #            or (vals[0] != course1 and vals[0] != course2 and vals[1] != course2)
                f = partial(MEFunc, Alter1, Alter2)
                # or use x.name == course1.name
                constraint.add_satisfy_function(f)
                constraints.append(constraint)
        return constraints

    def create_sameSectionConstraint(self, course):
        # all-nary should be faster
        assert isinstance(course, Course)
        lecSecs, tutSecs, labSecs = course.getAllSectionCopy()
        lecConts = self.SS_helper_binary(course, lecSecs)
        tutConts = self.SS_helper_binary(course, tutSecs)
        labConts = self.SS_helper_binary(course, labSecs)
        constraints = lecConts + tutConts + labConts
        constraints += self.createSameSecForLecTutPraConstraints(course, lecSecs, tutSecs, labSecs)
        return constraints

    def createSameSecForLecTutPraConstraints(self, course, lecs, tuts, labs):
        lectimesForAllSecs = self.getAllTimeVarForSects(*lecs)
        tutTimesForAllSecs = self.getAllTimeVarForSects(*tuts)
        labTimesForAllSecs = self.getAllTimeVarForSects(*labs)
        print(lectimesForAllSecs)
        lecTimes = self.sumList(lectimesForAllSecs)
        tutTimes = self.sumList(tutTimesForAllSecs)
        labTimes = self.sumList(labTimesForAllSecs)
        cs = []
        cs += self.lecTutPraIfOneMustAll(course, lecTimes, [tutTimes, labTimes])
        cs += self.lecTutPraIfOneMustAll(course, tutTimes, [lecTimes, labTimes])
        cs += self.lecTutPraIfOneMustAll(course, labTimes, [lecTimes, tutTimes])
        return cs

    def sumList(self, inputs):
        if inputs:
            i = list(inputs)
            r = i.pop(0)
            for l in i:
                r+=l
            return r
        else:
            return []

    def lecTutPraIfOneMustAll(self, course, lecTimes, othertwo):
        cs = []
        print("other two", othertwo)
        for time in lecTimes:
            for other in othertwo:
                if other:
                    cname = "SS_LTP:{}".format(course)
                    c = Constraint(cname, [time] + other)
                    print("time + other", [time] + other)
                    f = partial(preqFunction, course, course)
                    c.add_satisfy_function(f)
                    cs.append(c)
        return cs


    def SS_helper_binary(self, course, lecSecs):
        constraints = []
        for sec in lecSecs:
            lecTimes = self.getAllTimeVarForSect(sec)
            while lecTimes:
                time = lecTimes.pop(0)
                for otherTime in lecTimes:
                    c = Constraint("SS:{}:{}".format(lecSecs[0].name[0], course.courseCode), [time, otherTime])
                    f = cfuncBuilder(course, SSCFunc)
                    c.add_satisfy_function(f)
                    constraints.append(c)
        #create ME for different sections
        secs = list(lecSecs)
        while secs:
            sec = secs.pop(0)
            for s in secs:
                time1 = self.getAllTimeVarForSect(sec)
                time2 = self.getAllTimeVarForSect(s)
                cs = self.ME_for_2time(sec, s, time1, time2)
                constraints += cs
        return constraints

    def find_prereq(self, course):
        '''return a list of list of alternatives'''
        courses = list(self.courseList)
        prereqs = course.getPreqreCopy()
        pre_dict = dict()
        for c in courses:
            code = c.getGeneralCourseCode()
            if code in prereqs:
                if pre_dict.get(code):
                    pre_dict[code].append(c)
                else:
                    pre_dict[code] = []
        return list(pre_dict.values())

    def create_all_prConstraints(self, course, prereqs):
        cs = []
        for preAlters in prereqs:
            assert isinstance(preAlters, list)
            cs += self.create_prereqConstraints(course, preAlters)
        return cs


    def create_prereqConstraints(self, course, prereqAlters):
        cs = []
        timeCourse = self.getAllTimeVarForCourse(course)
        timePrereq = []
        for prereq in prereqAlters:
            timePrereq += self.getAllTimeVarForCourse(prereq)
        for timeC in timeCourse:
            #cannot be binary
            c = Constraint("PR:{},{}".format(course.courseCode, prereq.courseCode),
                           [timeC] + timePrereq)
            f = partial(preqFunction, course, prereq)
            c.add_satisfy_function(f)
            cs.append(c)
        return cs

    def getAllTimeVarForCourse(self, course):
        secs = course.getAllSectionCopy()

        secs = self.sumList(secs)
        print("after sum", secs)
        times = self.getAllTimeVarForSects(*secs)
        return self.sumList(times)

    def getAllTimeVarForSects(self, *secs):
        result = []
        for sec in secs:
            vs = self.getAllTimeVarForSect(sec)
            result.append(vs)
        return tuple(result)

    def getAllTimeVarForSect(self, sec):
        #assert isinstance(sec, Section)
        result = []
        for t in sec.times:
            v = self.getVariableForTime(t)
            result.append(v)
        return result

    def getVariableForTime(self, time):
        return self.timeDic[time]



def numberReqFunc(number, vals):
    count = 0
    courses = []
    for val in vals:
        if isinstance(val, tuple):
            #print("val", val[0], val[1])
            coursecode =val[0].getGeneralCourseCode()
            '''
            if coursecode not in courses:
                count += 1
                courses.append(coursecode)
                '''
            if val[0] not in courses:
                count += 1
                courses.append(val[0])
    if count == number:
        return True
    else:
        return False

def MEFunc(course1, course2, vals):
    if vals[0][0] == course1:
        return vals[1][0] != course2
    else:  # vals[0] not == course1
        return True


def cfuncBuilder(course, func):
    return lambda vals: func(course, vals)


def SSCFunc(course, vals):
    if vals[0][0] == course:
        return vals[1][0] == course
    elif vals[1][0] == course:
        return False  # x is != course
    else:
        # both not == course
        return True


def preqFunction(course, prereq, vals):
    if vals[0][0] == course:
        return prereq in [v[0] for v in vals[1:]]
    else:
        return True
