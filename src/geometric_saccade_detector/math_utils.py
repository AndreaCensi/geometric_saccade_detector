import numpy

def merge_fields(a, b):
    ''' Merge the fields of the two numpy arrays a,b. 
        They must have the same shape. '''
    if a.shape != b.shape:    
        raise ValueError('Arrays must have the same shape; '
                         'found %s and %s.' % (str(a.shape), str(b.shape)))
        
    new_dtype = []
    
    for f in a.dtype.fields:
        new_dtype.append((f, a.dtype[f]))
    for f in b.dtype.fields:
        new_dtype.append((f, b.dtype[f]))
        
    new_dtype = numpy.dtype(new_dtype)

    c = numpy.ndarray(shape=a.shape, dtype=new_dtype)
    for f in a.dtype.fields:
        c[f] = a[f][:]
    for f in b.dtype.fields:
        c[f] = b[f][:]
    return c


def find_closest_index(t, value):
    ''' Finds the index i such that t[i] is closest to value. '''
    indices = find_indices_in_bounds(t, value, t[-1])
    return indices[0] 

def find_indices_in_bounds(t, lower_bound, upper_bound):
    ''' Return the indices i such that t[i] >= lower_bound and t[o] <= upper_bound. '''
    indices, = numpy.nonzero(numpy.logical_and(t >= lower_bound, t <= upper_bound))
    
    # make sure it is sorted
    if len(indices) > 0:
        assert indices[0] <= indices[-1] 
    return indices        

def get_orientation_and_dispersion(rows, center, indices):
    ''' Rows: numpy array with 'x','y' fields.
        center: index of point to be considered the reference.
        indices: indices of points.
        
        Returns (orientation, dispersion) in radians.
    '''
    # central point
    p0 = numpy.array([rows['x'][center], rows['y'][center]])
    
    N = len(indices)
    # compute the angle of each point with respect to the center
    theta = numpy.ndarray((N,))
    for i in range(len(indices)):
        j = indices[i]
        p = numpy.array([rows['x'][j], rows['y'][j]])
        diff = p - p0
        theta[i] = numpy.arctan2(diff[1], diff[0])
    
    # compute statistics of this angle distribution
    mean, std = angle_mean_and_std(theta)
    
    return mean, std
        
def angle_mean_and_std(theta):
    ''' Computes mean and standard deviation for a distribution
        of angles.
        
        returns (mean, std)
    '''
    assert len(theta) >= 2
    
    C = numpy.cos(theta)
    S = numpy.sin(theta)
    
    mean = numpy.arctan2(S.mean(), C.mean())
    
    error = numpy.array(map(normalize_pi, theta - mean))
    std = error.std()
    
    return mean, std

def normalize_pi(a):
    ''' Normalizes an angle in [-pi, pi] '''
    return numpy.arctan2(numpy.sin(a), numpy.cos(a))
    
from scipy import signal

def compute_derivative(x, timestamp):
    dt = timestamp[1] - timestamp[0]
    deriv_filter = numpy.array([-0.5, 0, 0.5] / dt)
    d = signal.convolve(x, deriv_filter, mode=1) #@UndefinedVariable
    d[0] = d[1]
    d[-1] = d[-2]
    return d        
    
