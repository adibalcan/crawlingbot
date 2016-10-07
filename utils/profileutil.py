from pprint import pprint
import threading

class Profile:
    def __init__(self):
        self.profileData = {}

    def save(self, name, diff):
        if name + '_sum' in self.profileData:
            self.profileData[name + '_sum'] += diff
            self.profileData[name + '_count'] +=1
        else:
            self.profileData[name + '_sum'] = diff
            self.profileData[name + '_count'] =1
        self.profileData[name + '_average'] = round(self.profileData[name + '_sum'] / self.profileData[name + '_count'],4)

    def show(self):
        pprint(self.profileData)

profile = Profile()