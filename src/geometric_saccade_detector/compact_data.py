import tables, numpy
from optparse import OptionParser
from geometric_saccade_detector.filesystem_utils import locate
from geometric_saccade_detector import logger
import os
import scipy.io


def h5_read_saccades(filename):
    h5 = tables.openFile(filename, 'r')
    saccades = numpy.array(h5.root.saccades, dtype=h5.root.saccades.dtype)
    return saccades

def main():
    parser = OptionParser()

    (options, args) = parser.parse_args()

    # detection parameters
    directory = args[0]
    
    if not os.path.exists(directory):
        raise Exception('Directory %s does not exist.' % directory)

    pattern = '*-saccades.h5'
    files = sorted(list(locate(pattern=pattern, root=directory)))
    
    if not files:
        raise Exception('No files with pattern %s found in directory %s ' % \
                        (pattern, directory))
        
    all_data = []
    for i, file in enumerate(files):
        logger.info('Reading file %s' % file)
        saccades = h5_read_saccades(file)
        saccades['sample_num'] = i
        all_data.append(saccades)
        
    saccades = numpy.concatenate(all_data)
    
    output_file_mat = os.path.join(directory, 'saccades.mat') 
    output_file_h5 = os.path.join(directory, 'saccades.h5')
    
    logger.info('Writing on %s' % output_file_h5)
    h5file = tables.openFile(output_file_h5, mode="w")
    h5file.createTable('/', 'saccades', saccades)
    h5file.close()
    
    logger.info('Writing to file %s' % output_file_mat)
    scipy.io.savemat(output_file_mat, {'saccades':saccades}, oned_as='column')
    
    
        
