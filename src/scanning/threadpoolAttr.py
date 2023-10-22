import threading

class ThreadpoolAttr:

    def __init__(self, ret_size, update_func):
        self.ctr = [0]
        self.ret = [-1] * ret_size
        self.mutex = threading.Lock()
        self.cond = threading.Condition(lock=self.mutex)
        self.batch_done = False
        self.update_func = update_func