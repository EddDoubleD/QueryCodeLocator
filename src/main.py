import queue
from sys import argv

from src.connection.gitlab_conn import Connector
from src.locator.processors import FileProducer, SQLJavaProcessorConsumer, SQLXMLProcessorConsumer
from src.locator.utils import EndOfMessage
from src.locator.writer import FileWriter

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
    # java processing
    javaPipeline = queue.Queue()
    javaFolders = queue.Queue()
    javaFolders.put('Modules/asfk-autoproc')
    javaFolders.put('Modules/asfk-convertation')
    javaFolders.put('Modules/asfk-doc')
    javaFolders.put('Modules/asfk-lib')
    javaFolders.put('Modules/asfk-print')
    javaFolders.put('Modules/asfk-ws')
    javaFolders.put('Modules/sed-integration')
    javaFolders.put('Modules/ws-client')
    for i in range(1, 3):
        fileProducer = FileProducer(project=project, commit=commit, pipeline=javaPipeline, folderQueue=javaFolders,
                                    regex=r"\.java$")
        fileProducer.start()

    out = queue.Queue()
    endOf = EndOfMessage(2)
    for i in range(1, 5):
        javaConsumer = SQLJavaProcessorConsumer(project=project, pipeline=javaPipeline, out=out, regex=SQL_REGEX, attempts=1)
        javaConsumer.start()
    # xml processing
    xmlFolders = queue.Queue()
    xmlFolders.put('Func/config/lifecycles')
    xmlPipeline = queue.Queue()
    xmlFileProducer = FileProducer(project=project, commit=commit, pipeline=xmlPipeline, folderQueue=xmlFolders,
                                   regex=r"\.(lc|check|action)$")
    xmlFileProducer.start()
    for i in range(1, 5):
        xmlFileConsumer = SQLXMLProcessorConsumer(project=project, pipeline=xmlPipeline, out=out, attempts=0)
        xmlFileConsumer.start()

    fileWriter = FileWriter(pipeline=out, filePath="out.csv", attempts=8)

    fileWriter.start()
