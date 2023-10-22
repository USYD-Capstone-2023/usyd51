import unicurses as uc

class LoadingBar:

    progress = -1
    label = ""
    total_value = -1

    def __init__(self, label, total_value):
        self.progress = 0
        self.label = label
        self.total_value = total_value


    def set_progress(self, progress):
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
    

# Functions as a loading bar
class ProgressUI:

    def __init__(self, bar_length, bars: dict):
        self.bar_length = bar_length
        self.bars = bars
        uc.initscr()
        # mx, my = uc.getmaxyx(uc.stdscr)
        uc.stdscr = uc.newwin(len(bars) + 2, 100, 10, 0)
        uc.start_color()
        self.pad_label = 0
        for bar in self.bars.values():
            self.pad_label = max(self.pad_label, len(bar.label) + 1)


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

        uc.erase()
        uc.border(0)

        line = 0
        for bar in self.bars.values():
            line += 1
            label = bar.label + ":" + " " * (self.pad_label - len(bar.label))
            uc.move(line, 1)
            if bar.total_value == -1:
                uc.addstr("[WAITING] %s[%s]" % (label, ' ' * self.bar_length))
                continue

            percent = 100.0 * bar.progress / bar.total_value
            completed = int(percent / (100.0 / self.bar_length))
            status = "RUNNING"
            if bar.progress == bar.total_value:
                status = "DONE!  "

            bar_str = "[%s%s]" % ('-' * completed, ' ' * (self.bar_length - completed))
            uc.addstr("[%s] %s%s %d%% (%d / %d)" % \
                (status, label, bar_str, percent, bar.progress, bar.total_value))

        uc.refresh()

    def end(self):

        del self.scr


    def get_progress(self):
        return {x.label : x.to_json() for x in self.bars.values()}
    