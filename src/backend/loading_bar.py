import sys

# Functions as a loading bar
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


    # Resets the loading bar to default values.
    # This state is used to tell the frontend to stop requesting progress updates
    def reset(self):

        self.total_value = 0
        self.label = ""
        self.counter = 0


    # Draws progress bar
    def show(self):

        if self.total_value == 0:
            return
            
        percent = 100.0 * self.counter / self.total_value
        sys.stdout.write('\r')
        progress = int(percent / (100.0 / self.length))
        sys.stdout.write("[INFO] %s: [%s%s] %d%% (%d / %d)" % \
                        (self.label, '-' * progress, ' ' * (self.length - progress), int(percent), self.counter, self.total_value))
        
        if self.counter == self.total_value:
            sys.stdout.write("\n")  

        sys.stdout.flush()


    # Sets the progress of the loading bar, used in threaded situations where it is difficult to increment
    def set_progress(self, val):

        self.counter = val


    # Increases the loading bar's progress by one
    def increment(self):

        self.counter += 1
        