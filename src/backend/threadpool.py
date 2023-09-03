import threading, queue
from job import Job

# Handles a pool of threads to run expensive tasks in parallel
class Threadpool:

    MAX_QUEUE_SIZE = 10000
    queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
    pool_mutex = threading.Lock()
    stopping_condition = threading.Condition(pool_mutex)
    terminate = False

    def __init__(self, num_threads):
        
        self.threads = []
        
        for i in range(num_threads):
            self.threads.append(threading.Thread(target=self.threadpool_worker))
            self.threads[i].start()

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


    # Adds a job to the threadpool queue 
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
            while self.queue.empty() and not self.terminate:
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

            # Adds to completed job counter, allowing calling thread to know when all jobs are complete
            job.counter_ptr[0] += 1
            job.cond.notify()
            job.cond.release()

            # Garbage collector cannot remove objects passed between threads. Should fix our memory leak issue
            job = None


    