import logging

def setupLogger(loggerName: str, logFile: str, level=logging.DEBUG):
    log = logging.getLogger(loggerName)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    fileHandler = logging.FileHandler(logFile, mode='a', encoding='utf-8')
    fileHandler.setFormatter(formatter)

    log.setLevel(level)
    log.addHandler(fileHandler)
