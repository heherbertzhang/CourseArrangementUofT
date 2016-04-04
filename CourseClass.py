class Course:
    '''class for courses'''

    def __init__(self, name, course_code, term, lecSections, tutSections, labSections, prerequisites, exclusions):
        self.name = name
        self.courseCode = course_code
        self.term = term
        self.lecSections = list(lecSections)
        self.tutSections = list(tutSections)
        self.labSections = list(labSections)
        self.prerequisites = list(prerequisites) # in general code form, example : CSC384H1
        self.exclusions = list(exclusions) # in general code form, example : CSC384H1

    def __str__(self):
        return "Course {} at {}".format(self.courseCode, self.term)

    def getGeneralCourseCode(self):
        return self.courseCode[:8]

    def getLecSectionsCopy(self):
        return list(self.lecSections)

    def getTutSectionsCopy(self):
        return list(self.tutSections)

    def getLabSectionsCopy(self):
        return list(self.labSections)

    def getExclusionCopy(self):
        return list(self.exclusions)

    def getPreqreCopy(self):
        return list(self.prerequisites)

    def getAllSectionCopy(self):
        return self.getLecSectionsCopy(), self.getTutSectionsCopy(), self.getLabSectionsCopy()


class Section:
    def __init__(self, name, times, instructor):
        self.name = name
        self.times = list(times)
        self.instructor = instructor

    def __str__(self, *args, **kwargs):
        return self.name


class LecSection(Section):
    def __init__(self, name, times, instructor):
        Section.__init__(self, name, times, instructor)

class TutSection(Section):
    def __init__(self, name, times, instructor):
        Section.__init__(self, name, times, instructor)


class LabSection(Section):
    def __init__(self, name, times, instructor):
        Section.__init__(self, name, times, instructor)
