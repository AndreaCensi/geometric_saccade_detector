import scipy.signal
from . import np, contract


def merge_fields(a, b, ignore_duplicates=False):
    ''' Merge the fields of the two np arrays a,b. 
        They must have the same shape. '''
    if a.shape != b.shape:    
        raise ValueError('Arrays must have the same shape; '
                         'found %s and %s.' % (str(a.shape), str(b.shape)))
    all_fields = {}    
    new_dtype = []
    
    for f in a.dtype.fields:
        all_fields[f] = a.dtype[f]
        new_dtype.append((f, a.dtype[f]))
    
    for f in b.dtype.fields:
        if f in all_fields:
            if ignore_duplicates:
                continue
            else:
                msg = ('Field %r is in both datatypes.\n%r\n%r' % 
                       (f, a.dtype, b.dtype))
                raise ValueError(msg)
        else:
            new_dtype.append((f, b.dtype[f]))
        
    new_dtype = np.dtype(new_dtype)

    c = np.ndarray(shape=a.shape, dtype=new_dtype)
    for f in b.dtype.fields:
        # c[f] = b[f][:]
        c[f] = b[:][f]
    for f in a.dtype.fields:
        # c[f] = a[f][:]   not working on pytables
        c[f] = a[:][f]
    return c


def find_closest_index(t, value):
    ''' Finds the index i such that t[i] is closest to value. '''
    indices = find_indices_in_bounds(t, value, t[-1])
    return indices[0] 


def find_indices_in_bounds(t, lower_bound, upper_bound):
    ''' 
        Return the indices i such that t[i] >= lower_bound 
        and t[o] <= upper_bound. 
    '''
    indices, = np.nonzero(np.logical_and(t >= lower_bound,
                                               t <= upper_bound))
    
    # make sure it is sorted
    if len(indices) > 0:
        assert indices[0] <= indices[-1] 
    return indices        


def get_orientation_and_dispersion(rows, center, indices):
    ''' Rows: np array with 'x','y' fields.
        center: index of point to be considered the reference.
        indices: indices of points.
        
        Returns (orientation, dispersion) in radians.
    '''
    # central point
    p0 = np.array([rows['x'][center], rows['y'][center]])
    
    N = len(indices)
    # compute the angle of each point with respect to the center
    theta = np.ndarray((N,))
    for i in range(len(indices)):
        j = indices[i]
        p = np.array([rows['x'][j], rows['y'][j]])
        diff = p - p0
        theta[i] = np.arctan2(diff[1], diff[0])
    
    # compute statistics of this angle distribution
    mean, std = angle_mean_and_std(theta)

    assert not np.isnan(mean)
    assert not np.isnan(std)
    
    return mean, std
        
        
def angle_mean_and_std(theta):
    ''' Computes mean and standard deviation for a distribution
        of angles.
        
        returns (mean, std)
    '''
    assert len(theta) >= 2
    
    C = np.cos(theta)
    S = np.sin(theta)
    
    mean = np.arctan2(S.mean(), C.mean())
    
    error = np.array(map(normalize_pi, theta - mean))
    std = error.std()
    
    return mean, std


def normalize_pi(a):
    ''' Normalizes an angle in [-pi, pi] '''
    return np.arctan2(np.sin(a), np.cos(a))
    
    
def normalize_180(d):
    ''' 
        Normalizes an angle, expressed in degrees, in the [-180,180] 
        interval. 
    '''
    return np.degrees(normalize_pi(np.radians(d)))
    

@contract(x='array[K]', timestamp='array[K]', returns='array[K]')
def compute_derivative(x, timestamp):
    dt = timestamp[1] - timestamp[0]
    deriv_filter = np.array([0.5, 0, -0.5] / dt)
    if scipy.version.short_version == '0.8.0':
        d = scipy.signal.convolve(x, deriv_filter, mode='same',
                                  old_behavior=True)
    else:
        d = scipy.signal.convolve(x, deriv_filter, mode=1)
    d[0] = d[1]
    d[-1] = d[-2]
    return d        

# Taken from the np cookbook


def smooth1d(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd 
            integer
        window: the type of window from 'flat', 'hanning', 'hamming', 
            'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array 
    instead of a string   
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is not one of 'flat', 'hanning', 'hamming',"
                            "'bartlett', 'blackman'")

    s = np.r_[2 * x[0] - 
              x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


 
