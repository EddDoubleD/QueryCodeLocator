# Query Code Locator
This script extracts SQL-code from various repository files <br/>
In this version, the script is configured to search for scripts in java files and xml files of a certain format

## How it works ?

- Connectors - connects to the git project (gitlab/github), creates wrappers for API interaction
- Producers - crawls the width of the repository and collects all the necessary files
- Consumers - searches for sql code (or any other code) in found files
- Writer - writes the found objects in csv format (an extension for writing to any other formats is possible)
## How to start
```
# install requirements
pip install -r requirements.txt
# run script
python src/main.py <youre gitlab project url> <gitlab project secret token>
```
## Useful
- [regexp online](https://regex101.com)
- [about regexp](https://habr.com/ru/articles/349860/)
