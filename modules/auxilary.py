'''Contains miscellaneous functions used in most cases'''

from datetime import datetime

# Return the current time in ISO8601 format string
def getTime() -> str:
    '''
    Returns the current time in ISO8601 format
    '''
    return datetime.now().strftime('%Y%m%dT%H%M%S')