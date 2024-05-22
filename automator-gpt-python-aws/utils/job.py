import uuid

class Job:

    def __init__(self, title, description, detailed_steps, results=None, state="Open") -> None:
        self._job_id = str(uuid.uuid4())
        self._title = title
        self._description = description
        self._detailed_steps = detailed_steps
        self._results = results
        self._state = state

    def __repr__(self) -> str:
        return f"Job(title={self._title}, description={self._description})"

    @property
    def job_id(self):
        return self._job_id
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        self._title = value

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value

    @property
    def detailed_steps(self):
        return self._detailed_steps
    
    @detailed_steps.setter
    def detailed_steps(self, value):
        self._detailed_steps = value
    
    @property
    def results(self):
        return self._results
    @results.setter
    def results(self, value):
        self._results = value
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
