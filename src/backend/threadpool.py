import threading, queue
from job import Job

# Handles a pool of threads to run expensive tasks in parallel
class Threadpool:

    MAX_QUEUE_SIZE = 1000
    running = False
    terminate = False
    queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
    pool_mutex = threading.Lock()
    stopping_condition = threading.Condition(pool_mutex)

    def __init__(self, num_threads):
        self.threads = []
        
        for i in range(num_threads):
            self.threads.append(threading.Thread(target=self.threadpool_worker))
            self.threads[i].start()

    # Signals all threads in the threadpool to start working
    def start(self):
        self.stopping_condition.acquire()
        self.running = True
        self.stopping_condition.notify_all()
        self.stopping_condition.release()

    # Signals all threads in the pool to stop working
    def stop(self):
        self.pool_mutex.acquire()
        self.running = False
        self.pool_mutex.release()

    # Terminates the threadpool and ends all threads
    def end(self):
        self.stopping_condition.acquire()
        self.terminate = True
        self.stopping_condition.notify_all()
        self.stopping_condition.release()

        print("Waiting on threads to exit...")
        for thread in self.threads:
            thread.join()

        print("Successfully terminated threadpool!")


    def add_job(self, job):
        if self.queue.full():
            return False

        self.queue.put(job)
        self.stopping_condition.acquire()
        self.stopping_condition.notify()
        self.stopping_condition.release()
        return True

    # Runs jobs entered into the job queue
    def threadpool_worker(self):
        
        while True:
            # Waits if theres no jobs or the thread pool is halted and the threadpool isnt terminating
            self.stopping_condition.acquire()
            while (self.queue.empty() or not self.running) and not self.terminate:
                self.stopping_condition.wait()
                if self.terminate:
                    break

            if self.terminate:
                self.stopping_condition.release()
                print("Thread shutting down...")
                return

            self.stopping_condition.release()
            # Retrieves and completed job.
            # Python Queue is threadsafe, so no mutex is required
            job = self.queue.get(block=True, timeout=0)

            job.ret_ls[job.ret_id] = job.fptr(job.args)
            job.cond.acquire()
            job.counter_ptr[0] += 1
            job.cond.notify()
            job.cond.release()

    