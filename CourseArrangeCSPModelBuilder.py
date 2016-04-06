from CourseClass import *
from cspbase import *
from functools import partial


class CourseModelBuilder:
    def __init__(self, courseList):
        self.timeDic = {}
        self.courseList = courseList
        self.sortedTimeSlots = None
        terms = self.getTerms()
        # build time variables
        # one day start at 9am-10am timeslot and end at 8pm-9pm (20-21)
        weekdays = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
        for term in terms:
            for day in weekdays:
                for i in range(9, 21):
                    time_name = term + "-" + day + "-" + str(i)
                    # print("time name", time_name)
                    v = Variable(time_name)
                    self.timeDic[time_name] = v
        self.addDomainForTimeVars()
        self.sortedTimeSlots = sorted(list(self.timeDic.values()), key=getCompareKeyforTimeName)

    def createNumCourseRequire(self, number):
        vars = self.findAllTimeHaveCourse()
        #print("num var", vars)
        #todo: only add to scope the timeslot has courses and one for each since SS constraints will take care
        c = Constraint("number of courses", vars)#list(self.timeDic.values()))
        f = partial(numberReqFunc, number)
        # print("test fc", f(["no", self.courseList[0], self.courseList[0], "no"]))
        c.add_satisfy_function(f)
        sf = partial(numberRequiredSupportFunc, number)
        c.add_support_function(sf)
        return c

    def findAllTimeHaveCourse(self):

        timehavecourses = set()
        '''
        for time in self.sortedTimeSlots:
            if time.domain_size() > 1:'''
        for course in self.courseList:
            for lec in course.getLecSectionsCopy():
                lectimes = self.getAllTimeVarForSect(lec)
                timehavecourses.add(lectimes[0])
                #print("time have course", course, lectimes[0])
        return list(timehavecourses)


    def addDomainForTimeVars(self):
        # add None choice
        noneCourse = Course("No Course", "No Course", "", [], [], [], [], [])  # "No Course"
        noneSec = Section("Free", [], "N/A")
        for timeVar in list(self.timeDic.values()):
            timeVar.add_domain_values([(noneCourse, noneSec)])
        # add domain for time
        timeslotCount = 0
        for course in self.courseList:
            assert isinstance(course, Course)
            lecs, tuts, labs = course.getAllSectionCopy()
            sects = lecs + tuts + labs
            for sect in sects:
                # assert isinstance(sect, Section)
                for time in sect.times:
                    var = self.getVariableForTime(time)
                    assert isinstance(var, Variable)
                    # domain is tuple of course and sec
                    var.add_domain_values([(course, sect)])
                    timeslotCount += 1
        print("!!!!!course time slot count", timeslotCount)

    def getTerms(self):
        terms = set()
        for course in self.courseList:
            assert isinstance(course, Course)
            terms.add(course.term)
        print("terms", terms)
        return terms

    def buildModel(self):
        vars = list(self.sortedTimeSlots)
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
            prereqs = self.find_prereq(course)  # a list of list
            PRCs = self.create_all_prConstraints(course, prereqs)
            csp.add_constraints(PRCs)
        # for number of courses
        c = self.createNumCourseRequire(2)
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
                '''
        for p in MEpairs:
            print("pair start")
            for pp in p:
                print("ME!!!", pp)'''
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
                sf = partial(MESupportFunc, Alter1, Alter2)
                constraint.add_support_function(sf)
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
                r += l
            return r
        else:
            return []

    def lecTutPraIfOneMustAll(self, course, lecTimes, othertwo):
        cs = []
        for time in lecTimes:
            for other in othertwo:
                if other:
                    cname = "SS_LTP:{}".format(course)
                    c = Constraint(cname, [time] + other)
                    # print("time + other", [time] + other)
                    f = partial(preqFunction, course, course)
                    c.add_satisfy_function(f)
                    sf = partial(preqSupportFunc, course, course)
                    c.add_support_function(sf)
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
                    sf = partial(SSCSupportFunc, course)
                    c.add_support_function(sf)
                    constraints.append(c)
        # create ME for different sections
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
            # cannot be binary
            c = Constraint("PR:{},{}".format(course.courseCode, prereq.courseCode),
                           [timeC] + timePrereq)
            f = partial(preqFunction, course, prereq)
            c.add_satisfy_function(f)
            sf = partial(preqSupportFunc, course, prereq)
            c.add_support_function(sf)
            cs.append(c)
        return cs

    def getAllTimeVarForCourse(self, course):
        secs = course.getAllSectionCopy()

        secs = self.sumList(secs)
        times = self.getAllTimeVarForSects(*secs)
        return self.sumList(times)

    def getAllTimeVarForSects(self, *secs):
        result = []
        for sec in secs:
            vs = self.getAllTimeVarForSect(sec)
            result.append(vs)
        return tuple(result)

    def getAllTimeVarForSect(self, sec):
        # assert isinstance(sec, Section)
        result = []
        for t in sec.times:
            v = self.getVariableForTime(t)
            result.append(v)
        return result

    def getVariableForTime(self, time):
        return self.timeDic[time]


def numberReqFunc(number, vals):
    #print("num!!!!!!!!!!!!!!!!!!")
    count = 0
    courses = []
    for val in vals:
        # print("val", val[0], val[1])

        if not val[0].name == "No Course":
            coursecode = val[0].getGeneralCourseCode()

            if coursecode not in courses:
                count += 1
                courses.append(coursecode)
            '''
            if val[0] not in courses:
                count += 1
                courses.append(val[0])'''
    if count == number:
        #print("num : true")
        return True
    else:
        #print("num : false")
        return False


def MEFunc(course1, course2, vals):
    if course1 in vals[0]:
        return course2 not in vals[1]
    else:  # vals[0] not == course1
        return True


def cfuncBuilder(course, func):
    return lambda vals: func(course, vals)


def SSCFunc(course, vals):
    # binary only
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


def numberRequiredSupportFunc(number, val, othervars):
    # print("running num req")
    courses = []
    count = 0
    if val[0].name != "No Course":
        courses.append(val[0].getGeneralCourseCode())
        count += 1

    for v in othervars:
        if v.is_assigned():
            c = v.get_assigned_value()[0]
            if c.name != "No Course":
                code = c.getGeneralCourseCode()
                if code not in courses:
                    courses.append(code)
                    count += 1
    # check if count is over now:
    if count > number:
        # print("!!!!!!!!!!!!!!pre false")
        return False
    if count == number:
        # print("!!!!!!!!!!!!!!pre true")
        return True

    for v in othervars:
        if not v.is_assigned():  # find if there is course in domain
            domain = v.cur_domain()
            for c in [c for c, s in domain]:
                code = c.getGeneralCourseCode()
                if code not in courses:
                    courses.append(code)
                    count += 1
                    if count == number:
                        # print("num true")
                        return True
                    break  # one time slot can only count once
    # print("num false")
    return False


def MESupportFunc(course1, course2, val, othervars):
    if val[0] == course1:
        # check other var cur domain contain not only course2
        for v in othervars:
            if not len(v.cur_domain()) > 1:
                if v.cur_domain()[0] == course2:
                    return False
    return True


def preqSupportFunc(course, prereq, val, othervars):
    if val[0] == course:
        # need to check if other var cur domain contain prereq
        for v in othervars:
            return prereq in [c for c, s in v.cur_domain()]

    return True


def SSCSupportFunc(course, val, othervars):
    #print("running ss support")
    if val[0] == course:
        # check other variable to see if they have course in their domain
        for v in othervars:
            assert isinstance(v, Variable)
            if not course in [c for c, s in v.cur_domain()]:
                #print("SS false")
                return False

    else:
        #the val is not course, check if othervar has course if has return False
        for v in othervars:
            assert isinstance(v, Variable)
            if v.is_assigned():
                if v.get_assigned_value()[0] == course:
                    return False
    #print("SS true")
    return True


def convertDay(day):
    daydict = {"MONDAY": '1', "TUESDAY": '2', "WEDNESDAY": '3', "THURSDAY": '4', "FRIDAY": '5'}
    return daydict[day]


def convertTermSlot(term):
    termdict = {"Winter": '0', "Summer": '1', "Fall": '2'}
    return termdict[term]


def getCompareKeyforTimeName(timeVar):
    timeName = timeVar.name
    sl = timeName.split("-")
    yearterm = sl[0].split()
    year = yearterm[0]
    term = yearterm[1]
    term = convertTermSlot(term)
    day = sl[1]
    day = convertDay(day)
    hour = sl[2]
    if hour == '9':
        hour = '09'
    # print("convert",year+term+day+hour, timeName)
    return year + term + day + hour


def compareTimeName(time1, time2):
    sl1 = time1.split("-")
    sl2 = time2.split("-")
    term1 = sl1[0].split()
    term2 = sl2[0].split()
    day1 = sl1[1]
    day2 = sl2[1]
    hour1 = sl1[2]
    hour2 = sl2[2]
    if term1[0] < term2[0]:
        return -1
    elif term1[0] > term2[0]:
        return 1
    else:
        if term1[1] < term2[1]:
            return -1
        elif term1[1] > term2[1]:
            return 1
        else:
            if convertDay(day1) < convertDay(day2):
                return -1
            elif convertDay(day1) > convertDay(day2):
                return 1
            else:
                if hour1 < hour2:
                    return -1
                elif hour1 > hour2:
                    return 1
                else:
                    return 0
