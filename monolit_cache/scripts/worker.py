from threading import Thread
from queue import Queue
from time import sleep
import schedule


class Task:
	def __init__(self, task_func):
		self.task = task_func

	def run(self):
		try:
			self.task()
		except Exception as e:
			print('holy shit:', e)
			pass


class QueueAsyncWorker:
	def __init__(self):
		self.queue = Queue()
		self.thread = Thread(target=self.queue_worker)
		self.working = False

	def start(self):
		self.working = True
		self.thread.start()

	def queue_worker(self):
		while self.working:
			try:
				task = self.queue.get()
				task.run()
				self.queue.task_done()
			except Exception as e:
				print(e)

	def stop(self):
		def zombie():
			return None

		self.working = False
		self.queue.put(Task(zombie))

	def start_if_died(self):
		if not self.thread.is_alive():
			self.thread = Thread(target=self.queue_worker)
			self.start()

	def add_task(self, task: Task):
		self.start_if_died()
		self.queue.put(task)


class ScheduleWorker:
	def __init__(self, loop_delay=2):
		self.thread = Thread(target=self.loop)
		self.working = False
		self.loop_delay = loop_delay

	def start(self):
		self.working = True
		self.thread.start()

	def loop(self):
		while self.working:
			schedule.run_pending()
			sleep(self.loop_delay)

	def schedule(self, task: Task, seconds: int, just_once=True):
		if not self.working or not self.thread.is_alive():
			self.start()

		def run_task():
			try:
				task.run()
			except Exception as e:
				print("error on worker", e)
				pass
			if just_once:
				return schedule.CancelJob

		schedule.every(seconds).seconds.do(run_task)


# queue_worker = QueueAsyncWorker()
# schedule_worker = ScheduleWorker()
