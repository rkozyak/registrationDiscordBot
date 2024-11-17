import discord
from courses import Course

from enum import Enum

class TrackStatus(Enum):
    CLASS_OPEN = 1,
    CLASS_CLOSED_WAITLIST_OPEN = 2
    CLASS_CLOSED_WAITLIST_CLOSED = 3

class TrackRequest:
    crn: str
    term: str
    userIds: list[int]
    channelIds: list[int] # order matters, channels paired to users
    status: TrackStatus
    course: Course
    statusChanged: bool

    def __init__(self, crn: str, term: str, userIds: list[int], channelIds: list[int]):
        self.crn = crn
        self.term = term
        self.userIds = userIds
        self.channelIds = channelIds
        self.status = None
        self.fetch()

    # return True if status changed
    def fetch(self) -> bool:
        self.course = Course(self.crn, self.term)
        oldStatus = self.status
        if self.course.is_open():
            self.status = TrackStatus.CLASS_OPEN
        elif self.course.waitlist_available():
            self.status = TrackStatus.CLASS_CLOSED_WAITLIST_OPEN
        else:
            self.status = TrackStatus.CLASS_CLOSED_WAITLIST_CLOSED
        self.statusChanged = oldStatus != None and oldStatus != self.status
        return self.statusChanged