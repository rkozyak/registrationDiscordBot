import requests
from bs4 import BeautifulSoup

class Course:
    name: str
    def __init__(self, crn: str, term: str):
        self.crn = crn
        self.term = term # default
        url = 'https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in='
        url += self.term + '&crn_in=' + self.crn
        with requests.Session() as s:
            with s.get(url) as page:
                soup = BeautifulSoup(page.content, 'html.parser')
                headers = soup.find_all('th', class_="ddlabel")

                if len(headers) == 0:
                    self.name = "DOES NOT EXIST"
                    self.data = self.get_failed_info()
                    return

                self.name = headers[0].getText()

                table = soup.find('caption', string='Registration Availability').find_parent('table')

                if len(table) == 0: raise ValueError()

                self.rawData = [int(info.getText()) for info in table.findAll('td', class_='dddefault')]
                self.data = self.get_registration_info(self.rawData)
    
    def has_name(self) -> bool:
        return self.name != None

    def get_registration_info(self, rawData):

        if len(rawData) < 6: raise ValueError()

        waitlist_data = {
            'seats': rawData[3],
            'taken': rawData[4],
            'vacant': rawData[5]
        }
        load = {
            'seats': rawData[0],
            'taken': rawData[1],
            'vacant': rawData[2],
            'waitlist': waitlist_data
        }
        return load

    def get_failed_info(self):
        waitlist_data = {
            'seats': -1,
            'taken': -1,
            'vacant': -1
        }
        load = {
            'seats': -1,
            'taken': -1,
            'vacant': -1,
            'waitlist': waitlist_data
        }
        return load

    def is_open(self) -> bool:
        return self.data['vacant']

    def waitlist_available(self) -> bool:
        return self.data['waitlist']['vacant'] > 0

    def __str__(self) -> str:
        res = "{}\n".format(self.name)
        for name in self.data:
            if name == 'waitlist': continue
            res += "{}:\t{}\n".format(name, self.data[name])
        res += "waitlist open: {}\n".format('yes' if self.waitlist_available() else 'no')
        if self.waitlist_available():
            for name in self.data['waitlist']:
                res += "waitlist {}:\t{}\n".format(name, self.data['waitlist'][name])
        return res