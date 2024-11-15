import discord
from courses import Course

class TrackRequest:
    crn: str
    term: str
    user: discord.User
    status: str
    channelId: int

    def __init__(self, crn: str, term: str, user: discord.User, channelId: int):
        self.crn = crn
        self.term = term
        self.user = user
        self.status = "None"
        self.channelId = channelId

    def fetch(self) -> Course:
        course = Course(self.crn, self.term)
        return course

class TrackList:
    trackRequests: list[TrackRequest]
    def __init__(self, trackRequests: list[TrackRequest] = []):
        self.trackRequests = trackRequests
    
    def new_request(self, request: TrackRequest):
        self.trackRequests.append(request)