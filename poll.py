import time
import threading
import config

class Poll:
    def __init__(self, list, defaultInterval = config.requestMinIntervalForSameDomain):
        self.list = list
        self.defaultInterval = defaultInterval
        # READ THIS
        # Difference between lock and Rlock
        # http://stackoverflow.com/questions/22885775/what-is-the-difference-between-lock-and-rlock/22885810#22885810
        self.lock = threading.RLock()

    def getWebsite(self):
        with self.lock:
            if len(self.list) == 0:
                return None
            # TODO put here an while and check len(self.list) at every iteration
            for website in self.list:
                if website.ended:
                    self.remove(website)
                else:
                    if time.time() - website.lastRequest >= self.defaultInterval and not website.inProgress:
                        website.lastRequest = time.time()
                        website.inProgress = True
                        return website
        return None

    def add(self, website):
        with self.lock:
            self.list.append(website)

    def remove(self, website):
        with self.lock:
            try:
                # Bug here, python rise exception if you remove when iterate over list
                self.list.remove(website)
            except Exception as e:
                print('exception at remove website:')
                raise e

    def pop(self):
        with self.lock:
            listLength = len(self.list)
            if listLength == 0:
                return None
            website = self.list[listLength-1]
            self.list.remove(website)
            return website

    def __len__(self):
        return len(self.list)