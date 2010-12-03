import numpy, tables, os, scipy.io

from .logger import logger
from .structures import saccade_dtype

def saccades_write_all(basename, saccades):
    ''' Writes in all the output types we know. ``basename`` is
        the file name without the extension. '''
    # just in case
    basename = os.path.splitext(basename)[0]
    dirname = os.path.dirname(basename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    saccades_write_h5(basename + '.h5', saccades)
    saccades_write_mat(basename + '.mat', saccades)
    
def saccades_read_h5(filename):
    h5 = tables.openFile(filename, 'r')
    saccades = numpy.array(h5.root.saccades, dtype=h5.root.saccades.dtype)
    # TODO: check the dtype is the same
    return saccades

def saccades_write_h5(filename, saccades):
    h5file = tables.openFile(filename, mode="w")
    table = h5file.createTable('/', 'saccades', saccades)
    # if there is only one sample, then add a symbolic link 
    # to /flydra/samples/<SAMPLE>/saccades
    num_samples = len(numpy.unique(saccades[:]['sample']))
    if num_samples == 1:
        id = saccades[0]['sample']
        parent = '/flydra/samples/%s' % id
        name = 'saccades'
        target = table 
        h5file.createHardLink(where=parent, name=name, target=target,
                              createparents=True)
    
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

    saccades = enforce_saccade_dtype(data)
    
    # check the important things are ok
    
    for field in ['time_passed']:
        x = saccades[field]
        ok = numpy.isfinite(x)
        bad, = numpy.nonzero(numpy.logical_not(ok))
        if len(bad):
            print 'Fixing %d/%d non finite data in %s in %s' % \
                (len(bad), len(saccades), field, filename)
            saccades = saccades[ok]
            
    return saccades

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
    
    
    
