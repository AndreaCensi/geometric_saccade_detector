import os, numpy, sys, pickle
from optparse import OptionParser

from .. import logger
from ..utils import locate
from ..io import saccades_read_h5, saccades_write_h5, saccades_write_mat

description = """ 
    Compacts the data in two files (posts and noposts).
    Used in Fall 2010. 
"""


def main():
    parser = OptionParser(usage=description)

    (options, args) = parser.parse_args() #@UnusedVariable

    if len(args) != 1:
        logger.error('I expect exactly one argument.')
        sys.exit(-1)

    # detection parameters
    directory = args[0]
    
    if not os.path.exists(directory):
        raise Exception('Directory %s does not exist.' % directory)

    pattern = '*-saccades.h5'
    files = sorted(list(locate(pattern=pattern, root=directory)))
    
    if not files:
        raise Exception('No files with pattern %s found in directory %s ' % 
                        (pattern, directory))
        
    all_data = []
    for i, filename in enumerate(files):
        logger.info('Reading file %s' % filename)
        saccades = saccades_read_h5(filename)
        saccades['sample_num'] = i
        all_data.append(saccades)
        
    saccades = numpy.concatenate(all_data)
    
    select = saccades['stimulus'] == 'nopost'
    saccades_noposts = saccades[select]
    saccades_posts = saccades[numpy.logical_not(select)]
    
    for (data, name) in [
            (saccades, 'saccades'),
            (saccades_noposts, 'saccades-noposts'),
            (saccades_posts, 'saccades-posts'),
    ]:
        out_mat = os.path.join(directory, '%s.mat' % name) 
        out_h5 = os.path.join(directory, '%s.h5' % name)
        out_pickle = os.path.join(directory, '%s.pickle' % name)

        logger.info('Writing on %s (%d saccades)' % (out_h5, len(data)))
        saccades_write_h5(out_h5, data)
        
        logger.info('Writing on %s (%d saccades)' % (out_mat, len(data)))
        saccades_write_mat(out_mat, data)
        
        logger.info('Writing on %s (%d saccades)' % (out_pickle, len(data)))
        pickle.dump(data, open(out_pickle, 'w'))
        
        
        
    
    
    
        
