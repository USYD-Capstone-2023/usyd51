from blessings import Terminal

class LoadingBar:

    def __init__(self, label, total_value):
        self.progress = 0
        self.label = label
        self.total_value = total_value


    def update(self, progress):
        if progress > self.total_value:
            self.progress = self.total_value
        
        else:
            self.progress = progress


    def set_total(self, total):
        self.total_value = total


    def increment(self):
        if self.progress < self.total_value:
            self.progress += 1


    def to_json(self):
        return {"label" : self.label, "progress" : self.progress, "total_value" : self.total_value}
    


term = Terminal()
# Functions as a loading bar
class ProgressUI:


    def __init__(self, bar_length, bars: dict):
        self.bar_length = bar_length
        self.bars = bars

    def set_params(self, label, length, total_value):
        # total length of progress bar in chars
        self.length = length 
        # "full" value of progress bar
        self.total_value = total_value 
        self.label = label
        self.progress = 0

    def get_bar(self, key):

        if key in self.bars.keys():
            return self.bars[key]
        return None

    # Draws progress bar
    def show(self):

        line = 0
        for bar in self.bars.values():

            with term.location(0, line):

                if bar.total_value == -1:
                    print("[WAITING] %s: [%s]" % (bar.label, ' ' * self.length))
                    continue

                percent = 100.0 * bar.progress / bar.total_value
                completed = int(percent / (100.0 / self.length))
                status = "RUNNING"
                if bar.progress == bar.total_value:
                    status = "DONE!  "

                print("[%s] %s: [%s%s] %d%% (%d / %d)" % \
                            (status, bar.label, '-' * completed, ' ' * (self.length - completed), percent, bar.progress, bar.total_value))


    def get_progress(self):
        return {x.label : x.to_json() for x in self.bars.values()}
    