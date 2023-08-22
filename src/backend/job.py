class Job:
    def __init__(self, fptr, args, ret_ls, ret_id, counter_ptr, cond):
        self.fptr = fptr
        self.args = args
        self.ret_ls = ret_ls
        self.ret_id = ret_id
        self.counter_ptr = counter_ptr
        self.cond = cond