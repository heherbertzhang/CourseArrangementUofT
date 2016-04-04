class Time:
    def __init__(self, term, day, hour):
        self.term = term
        self.day = day
        self.hour = hour
    def __eq__(self, other):
        return self.term == other.term and \
            self.day == other.day and \
            self.hour == other.hour