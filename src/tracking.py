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
    userId: int
    channelId: int
    status: TrackStatus
    course: Course

    def __init__(self, crn: str, term: str, userId: int, channelId: int):
        self.crn = crn
        self.term = term
        self.userId = userId
        self.channelId = channelId
        self.status = None
        self.fetch()

    # return True if status changed
    def fetch(self) -> bool:
        if hasattr(self,'course'):
            oldVacant = self.course.data['vacant']
            oldWaitlist = self.course.data['waitlist']['vacant']
        self.course = Course(self.crn, self.term)
        # oldStatus = self.status
        # if self.course.is_open():
        #     self.status = TrackStatus.CLASS_OPEN
        # elif self.course.waitlist_available():
        #     self.status = TrackStatus.CLASS_CLOSED_WAITLIST_OPEN
        # else:
        #     self.status = TrackStatus.CLASS_CLOSED_WAITLIST_CLOSED
        if 'oldVacant' in locals():
            return (oldVacant != self.course.data['vacant']) or (oldWaitlist != self.course.data['waitlist']['vacant'])
        return False
        # return oldStatus != None and oldStatus != self.status
    
class TrackList:
    trackRequests: list[TrackRequest]
    def __init__(self, trackRequests: list[TrackRequest] = []):
        self.trackRequests = trackRequests
    
    def new_request(self, request: TrackRequest):
        self.trackRequests.append(request)