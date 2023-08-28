import sys

# Functions as a loading bar
# Prints empty on init, prints updated on increment
class Loading_bar:

    counter = 0
    total_value = 0
    label = ""

    def set_params(self, label, length, total_value):
        # total length of progress bar in chars
        self.length = length 
        # "full" value of progress bar
        self.total_value = total_value 
        self.label = label
        self.counter = 0

    def reset(self):
        self.total_value = 0
        self.label = ""
        self.counter = 0

    # Updates progress bar
    def show(self):
        percent = 100.0 * self.counter / self.total_value
        sys.stdout.write('\r')
        progress = int(percent / (100.0 / self.length))
        sys.stdout.write("[INFO] %s: [%s%s] %d%% (%d / %d)" % \
                        (self.label, '-' * progress, ' ' * (self.length - progress), int(percent), self.counter, self.total_value))
        
        if self.counter == self.total_value:
            sys.stdout.write("\n")  

        sys.stdout.flush()

    def set_progress(self, val):
        self.counter = val

    def increment(self):
        self.counter += 1
        