import unicurses as uc
import copy

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

    scans = {}

    def __init__(self, bar_length):
        self.bar_length = bar_length
        uc.initscr()
        uc.curs_set(False)
        self.resize()
        self.show()

    def resize(self):

        uc.move(0, 0)
        uc.clear()
        uc.refresh()
        self.pad_label = 0
        self.height = 3
        if self.scans:
            for scan in self.scans.values():
                self.height += len(scan) + 2

                for bar in scan.values():
                    self.pad_label = max(self.pad_label, len(bar.label) + 1)

        y, x = uc.getmaxyx(uc.stdscr)
        uc.stdscr = uc.newwin(self.height, x, 0, 0)


    def add_bars(self, auth, bars: dict):

        self.scans[auth] = bars
        self.resize()


    def rm_bars(self, auth):

        del self.scans[auth]
        self.resize()

    # Draws progress bar
    def show(self):

        uc.move(0, 0)
        uc.clear()
        uc.border(0)
        if len(self.scans) == 0:
            uc.move(1, 1)
            uc.addstr("NO SCANS CURRENTLY RUNNING...")
            uc.refresh()
            return
        
        scans_cpy = copy.deepcopy(self.scans)
        line = 0
        id = 0
        for scan in scans_cpy.values():

            line += 2
            uc.move(line, 1)
            uc.addstr("SCAN ID: %d" % id)
            id += 1

            for bar in scan.values():
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

        uc.endwin()
        uc.delwin(uc.stdscr)


    def get_progress(self):
        return 
    