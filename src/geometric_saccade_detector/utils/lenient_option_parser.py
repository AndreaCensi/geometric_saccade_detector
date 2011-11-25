__version__ = '1.1'

import optparse
from optparse import IndentedHelpFormatter
from . import UserError

class LenientOptionParser(optparse.OptionParser):
    
    def __init__(self, prog=None, usage=None):
        formatter = IndentedHelpFormatter(
                 indent_increment=2,
                 max_help_position=80,
                 width=100,
                 short_first=1)
        optparse.OptionParser.__init__(self, prog=prog, usage=usage,
                                       formatter=formatter)
        
    def parse_args(self, args):
        self.arguments = list(args)
        return optparse.OptionParser.parse_args(self, args)
    
    def error(self, msg):
        #msg = '%s: %s' % (self.get_prog_name(), msg)
        msg += ('\nArguments: %s %s' % 
                (self.get_prog_name(), " ".join(self.arguments)))
        raise UserError(msg)
