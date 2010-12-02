import numpy
import scipy.signal


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
        # c[f] = a[f][:]   not working on pytables
        c[f] = a[:][f]
    for f in b.dtype.fields:
        # c[f] = b[f][:]
        c[f] = b[:][f]
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

    assert not numpy.isnan(mean)
    assert not numpy.isnan(std)
    
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
    
def normalize_180(d):
    ''' Normalizes an angle, expressed in degrees, in the [-180,180] interval. '''
    return numpy.degrees(normalize_pi(numpy.radians(d)))
    


def compute_derivative(x, timestamp):
    dt = timestamp[1] - timestamp[0]
    deriv_filter = numpy.array([0.5, 0, -0.5] / dt)
    d = scipy.signal.convolve(x, deriv_filter, mode=1) #@UndefinedVariable
    d[0] = d[1]
    d[-1] = d[-2]
    return d        



# Taken from the numpy cookbook

def smooth1d(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len < 3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s = numpy.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w = numpy.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = numpy.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]




    
