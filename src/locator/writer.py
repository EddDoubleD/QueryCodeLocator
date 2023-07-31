import queue
import threading
import csv

from src.locator.processors import FINISH


class FileWriter(threading.Thread):
    """

    """

    def __init__(self, pipeline: queue.Queue, filePath, attempts):
        super().__init__()
        self.pipeline = pipeline
        self.filePath = filePath
        self.attempts = attempts

    """ 
        Implementing stream processing logic 
    """

    def run(self):
        value = None
        with open(self.filePath, 'w', newline='') as file:
            fields = ['path', 'sql', 'id', 'description']
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            while value != FINISH:
                while not self.pipeline.empty():
                    value = self.pipeline.get()
                    if value == FINISH:
                        self.attempts -= 1
                        print(f'Получено сообщение о завершении, осталось попыток {self.attempts}'
                              f' Сообщений в очереди {self.pipeline.qsize()}')
                        if self.attempts <= 0:
                            break

                    try:
                        writer.writerow(value)
                    except Exception as e:
                        print(f'write to file error {e}')
        print("writer finish")