import ray
import math
import time
import random

"""
Following Tutorial From:
    https://docs.ray.io/en/latest/ray-core/examples/monte_carlo_pi.html#monte-carlo-pi
    (all credits to above, not my own work)
"""

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

@ray.remote
def sample(num_samples: int, task_id: int, progress_actor: ray.actor.ActorHandle) -> int:
    num_inside = 0
    for idx in range(num_samples):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if (x**2 + y**2) <= 1:      # math.hypot()
            # check if our random sample was inside the circle
            num_inside += 1
        
        if (idx+1) % 1_000_000 == 0:
            progress_actor.report.remote(task_id, idx+1)
    
    progress_actor.report.remote(task_id, num_samples)
    return num_inside

NUM_SAMPLERS = 10
NUM_SAMPLES_PER = 10_000_000
TOT_NUM_SAMPLES = NUM_SAMPLERS * NUM_SAMPLES_PER

def main():
    ray.init()
    progress_actor = ProgressActor.remote(TOT_NUM_SAMPLES)
    res = [sample.remote(NUM_SAMPLES_PER, idx, progress_actor) for idx in range(NUM_SAMPLERS)]

    while(True):
        progress = ray.get(progress_actor.get_progress.remote())
        print(f'progress: {int(progress * 100)}%')
        if progress == 1:
            break
        time.sleep(1)
    
    num_inside = sum(ray.get(res))
    pi = (num_inside * 4) / TOT_NUM_SAMPLES
    print(f'Estimated val of pi: {pi}')


if __name__ == "__main__":
    main()
