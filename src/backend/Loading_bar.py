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
        sys.stdout.write("[INFO] %s: [%s] %d%%" % (self.label, ' ' * self.length, 0))
        sys.stdout.flush()

    # Updates progress bar and re prints with one more unit of completion
    def increment(self):
        self.counter += 1

        percent = 100.0 * self.counter / self.total_value
        sys.stdout.write('\r')
        progress = int(percent / (100.0 / self.length))
        sys.stdout.write("[INFO] %s: [%s%s] %d%%" % (self.label, '-' * progress, ' ' * (self.length - progress), int(percent)))
        sys.stdout.flush()