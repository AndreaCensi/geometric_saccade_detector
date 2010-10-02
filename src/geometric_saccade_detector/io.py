import numpy
import tables
import scipy.io
from geometric_saccade_detector.structures import saccade_dtype
from geometric_saccade_detector import logger

def saccades_read_h5(filename):
    h5 = tables.openFile(filename, 'r')
    saccades = numpy.array(h5.root.saccades, dtype=h5.root.saccades.dtype)
    # TODO: check the dtype is the same
    return saccades

def saccades_write_h5(filename, saccades):
    h5file = tables.openFile(filename, mode="w")
    h5file.createTable('/', 'saccades', saccades)
    h5file.close()
    
def saccades_write_mat(filename, saccades):
    scipy.io.savemat(filename, {'saccades':saccades}, oned_as='column')
    
    
def saccades_read_mat(filename):
    ''' Reads a saccade file written by matlab. 
        Not all the meta information is currently recovered, so we
        have to do some hammering to fit the data into our saccade dtype. '''
    contents = scipy.io.loadmat(filename,
                                struct_as_record=True, squeeze_me=True)
    data = contents['saccades'] 

    return enforce_saccade_dtype(data)

def enforce_saccade_dtype(data):
    saccades = numpy.zeros(shape=(len(data),), dtype=saccade_dtype)
    
    for field in saccades.dtype.fields:
        if not field in data.dtype.fields:
            logger.warning('Matlab data does not have field "%s".' % field)
            # saccades[field] = numpy.NaN
        else:
            # This does not work between |O4 and strings
            # saccades[field] = data[field]
            for i in range(len(saccades)):
                saccades[field][i] = data[field][i]
            
    more = [field for field in data.dtype.fields 
                if not field in saccades.dtype.fields]
    if more:
        logger.warning('Data has more fields (%s) than expected.' % ", ".join(more))
            
    return saccades
    
    
    
