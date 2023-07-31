import queue
from sys import argv

from src.connection.gitlab_conn import Connector
from src.locator.processors import FileProducer, SQLJavaProcessorConsumer, FileWriter

BRANCH = "master"  # default GitLab project branch
SQL_REGEX = r"\"(select|call|update|delete|insert){1} (\s|\S|\n)*\";"

"""
Script Entry Point
@:arg GITLAB_URL   gitlab project url
@:arg ACCESS_TOKEN project secret 
"""
if __name__ == '__main__':
    if argv.__len__() < 3:
        print("not enough parameters")
        exit(1)
        # get argument's
    script, url, token = argv
    gl = Connector(url, token)
    if not gl.auth():
        exit(1)

    project = gl.getProject()
    if project is None:
        exit(1)

    # Hash code of the last commit from the master branch
    commit = project.commits.list(ref_name=BRANCH)[0].id

    pipeline = queue.Queue()
    folders = queue.Queue()
    # folders.put('Modules/asfk-doc/src/main/java/com/otr/sufd_new/')
    folders.put('Modules/asfk-doc/src/main/java/com/otr/sufd_new/lifecycle')
    out = queue.Queue()

    fileProducer = FileProducer(project=project, commit=commit, pipeline=pipeline, folderQueue=folders,
                                regex=r"\.java$")

    fileConsumer = SQLJavaProcessorConsumer(project=project, commit=commit, pipeline=pipeline, out=out,
                                            regex=SQL_REGEX)
    fileConsumer2 = SQLJavaProcessorConsumer(project=project, commit=commit, pipeline=pipeline, out=out,
                                             regex=SQL_REGEX)
    fileWriter = FileWriter(pipeline=out, filePath="/")

    fileProducer.start()
    fileConsumer.start()
    fileConsumer2.start()
    # time.sleep(60)
    fileWriter.start()
