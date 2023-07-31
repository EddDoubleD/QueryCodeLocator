import base64
import queue
import re
import threading

from gitlab.v4.objects import Project

# Wrap over queue for logging
FINISH = object()


class FileProducer(threading.Thread):
    """
    SQL scanner for java files, reads files from the queue and parses them for SQL code

    @:argument project     GitLab project API
    @:argument commit      Hash code of the commit to search against
    @:argument pipeline    Queue for subtracting file paths
    @:param folderQueue Queue for find folder path
    """

    def __init__(self, project: Project, commit, pipeline: queue.Queue, folderQueue: queue.Queue, regex):
        super().__init__()
        self.project = project
        self.pipeline = pipeline
        self.commit = commit
        self.folderQueue = folderQueue
        self.pattern = re.compile(regex)

    """
    Bypasses the folder and adds java files to the general queue, and folders to the local queue
    @:argument folder relative folder path in GitLab 
    """

    def bypass(self, folder):
        files = self.project.repository_tree(path=folder, ref=self.commit, all=True)
        key = True
        for index, file in enumerate(files):
            filePath = file['path']
            fileName = file['name']
            if file['type'] == 'tree':
                self.folderQueue.put(filePath)
            elif key and self.pattern.search(fileName):
                self.pipeline.put(folder)
                key = False

    # Bypass all folders
    def run(self):
        while not self.folderQueue.empty():
            value = self.folderQueue.get()
            self.bypass(value)

        self.pipeline.put(FINISH)
        print("Java File Producer finish")


class SQLJavaProcessorConsumer(threading.Thread):
    """
    SQL scanner for java files, reads files from the queue and parses them for SQL code

    @:argument project  GitLab project API
    @:argument commit   Hash code of the commit to search against
    @:argument pipeline Queue for subtracting file paths
    """

    def __init__(self, project: Project, commit, pipeline: queue.Queue, out: queue.Queue, regex):
        super().__init__()
        self.project = project
        self.pipeline = pipeline
        self.commit = commit
        self.out = out
        self.pattern = re.compile(regex)

    """ 
    Implementing stream processing logic 
    """

    def run(self):
        filePath = None
        while filePath != FINISH:
            while not self.pipeline.empty():
                filePath = self.pipeline.get()
                if filePath is FINISH:
                    self.pipeline.put(FINISH)  # pushing further
                    break
                files = self.project.repository_tree(path=filePath, ref=self.commit, all=True)
                content = [{"id": file['id'], "name": file['name'], "path": file['path']} for file in files if
                           file['type'] == 'blob']
                for index, value in enumerate(content):
                    fileB64 = self.project.repository_blob(value["id"])
                    textFile = base64.b64decode(fileB64['content']).decode()
                    result = self.pattern.search(textFile, re.IGNORECASE)
                    if result:
                        self.out.put({"file": value['path'], "sql": result.groups()})

        self.out.put(FINISH)
        print(' SQL scanner for java files finish')


class ParseResult:
    def __init__(self, file, sql):
        self.file = file
        self.sql = sql


class FileWriter(threading.Thread):
    """

    """

    def __init__(self, pipeline: queue.Queue, filePath):
        super().__init__()
        self.pipeline = pipeline
        self.filePath = filePath

    """ 
        Implementing stream processing logic 
    """

    def run(self):
        value = object()
        while value != FINISH:
            while not self.pipeline.empty():
                value = self.pipeline.get()
                if value == FINISH:
                    break

                print(value)
