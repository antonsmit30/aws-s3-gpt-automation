from openai import OpenAI
import uuid
import time
import threading

class Worker:

    instances = []
    job_queue = []

    def __init__(self, open_ai_key, role="user", state=None):
        Worker.instances.append(self)
        self._openai_key = open_ai_key
        self._role = role
        self.state = state
        self._client = OpenAI(
            api_key=self._openai_key
        )
        # a random string value
        self._id = str(uuid.uuid4())
        self._full_message = [
            {"role": "system", "content": f"""You are known by uuid : {self.instance_id}.You are a general worker.
             You will communicate directly with the master bot."""},            
        ]

    # Getters
    @property
    def instance_id(self):
        # print(f"self._id: {self._id}")
        return self._id

    
    def start_thread(self):
        """Starts a thread for the worker to check the job queue for any jobs."""
        thread = threading.Thread(target=self.check_job_orders)
        thread.start()
    
    
    def check_job_orders(self):
        """Checks the job queue for any jobs. If there are jobs in the queue then return the job. 
        If there are no jobs in the queue then return string `no jobs in queue`."""
        if len(Worker.job_queue) > 0:
            job = Worker.job_queue.pop(0)
            print(f"job: {job.job_id} in queue. message: {job.message}. Putting back in queue for now.")
            Worker.job_queue.append(job)
        else:
            print(f"worker {self.instance_id} has no jobs in queue.")
            return "no jobs in queue"
