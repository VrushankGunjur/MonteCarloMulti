import ray

@ray.remote
class ProgressActor:
    def __init__(self, num_samples: int):
        self.num_samples = num_samples
        # maps each task to # of samples completed in that task
        self.num_samples_completed_per_task = {}

    def report(self, task_id: int, num_samples_finished: int) -> None:
        self.num_samples_completed_per_task[task_id] = num_samples_finished

    def get_progress(self) -> float:
        prog_sum = sum(self.num_samples_completed_per_task.values())
        return prog_sum / self.num_samples