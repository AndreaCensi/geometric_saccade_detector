
__version__ = '1.1'
 
import sys
import traceback

class UserError(Exception):
    pass

def wrap_script_entry_point(function, logger):
    try:
        function(sys.argv[1:])
        sys.exit(0)
    except UserError as e:
        logger.error(str(e))
        sys.exit(1) 
    except Exception as e:
        logger.error(traceback.format_exc())
        sys.exit(-55) 


def check_mandatory(options, mandatory):
    for m in mandatory:
        if options.__dict__[m] is None:
            msg = 'Mandatory option %r not passed.' % m
            raise UserError(msg)

def check_no_spurious(args):
    if args:
        raise UserError('Spurious arguments: %s' % args)
    
