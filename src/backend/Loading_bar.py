import sys

# Functions as a loading bar
# Prints empty on init, prints updated on increment
class Loading_bar:
    
    def __init__(self, label, length, total_value):
        # total length of progress bar in chars
        self.length = length 
        # "full" value of progress bar
        self.total_value = total_value 
        self.label = label
        self.counter = 0

        sys.stdout.write('\r')
        sys.stdout.write("[INFO] %s: [%s] %d%% (%d / %d)" % (self.label, ' ' * self.length, 0, 0, self.total_value))
        sys.stdout.flush()

    def set_progress(self, val):
        self.counter = val
        percent = 100.0 * self.counter / self.total_value
        sys.stdout.write('\r')
        progress = int(percent / (100.0 / self.length))
        sys.stdout.write("[INFO] %s: [%s%s] %d%% (%d / %d)" % (self.label, '-' * progress, ' ' * (self.length - progress), int(percent), self.counter, self.total_value))

        if self.counter == self.total_value:
            sys.stdout.write("\n")  

        sys.stdout.flush()

    # Updates progress bar and re prints with one more unit of completion
    def increment(self):
        self.counter += 1
        self.set_progress(self.counter)

        