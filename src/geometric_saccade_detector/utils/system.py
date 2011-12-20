from datetime import datetime
import pwd
import os
import platform


def get_user():    
    try:
        return pwd.getpwuid(os.getuid())[0]
    except:
        return '<unknown-user>'
    
    
def get_computed_string(prog=None, version=None):
    """ Returns a string that describes the major components of the system. """
    
    return ('%s %s %s %s@%s Python %s' % 
                (prog, version,
                 datetime.now().strftime("%Y%m%d_%H%M%S"),
                 get_user(), platform.node(),
                 platform.python_version()))
    
