from . import np
from reprep import Report
from reprep.plot_utils.axes import y_axis_set, x_axis_set
from geometric_saccade_detector.structures import saccade_dtype, UNKNOWN
from geometric_saccade_detector.algorithm import saccade_list_to_array
import warnings


def angvel_saccade_detect(rows,
                          angular_velocity_threshold_deg=300,
                          min_dt=1 / 60.0,
                          max_dt=1):
    ''' 
        Returns a saccade table, and an annotation table. 
        
        
    '''
    # Find points where the angular velocity is higher than a 
    # threhsold
    angular_velocity_deg = np.rad2deg(rows['reduced_angular_velocity'])
    orientation_deg = np.degrees(rows['reduced_angular_orientation'])
    obj_id = rows['obj_id']
    
    # Fix for irregular time stamps
    timestamp = rows['frame'] / 60.0
    warnings.warn('Fixing irregular timestamps')
    
    regular = np.zeros(shape=timestamp.shape, dtype='bool')
    max_so_far = timestamp[0] - 1
    for i in range(len(timestamp)):
        if timestamp[i] <= max_so_far:
            print('Irregular at %d: %s' % (i, ''))
            regular[i] = False
        else:
            regular[i] = True
        max_so_far = max(max_so_far, timestamp[i])
        
    fast_enough = (np.abs(angular_velocity_deg) 
                   >= angular_velocity_threshold_deg)
    candidates = np.logical_and(fast_enough, regular)
    
    saccades = []
    # Find sequences
    for start, stop in find_sequences(candidates):
        
        # Do not consider joining multiple tracks
        if obj_id[start] != obj_id[stop - 1]:
            continue
        
        stop -= 1
        time_start = timestamp[start]
        time_stop = timestamp[stop]
        duration = time_stop - time_start 
        
        if duration < min_dt or duration > max_dt:
            continue
        
        # Find the fastest point in the saccade   
        #print((stop + 1) - start)
        avel = np.abs(angular_velocity_deg)
        avel[:start] = 0  # zero other
        avel[stop:] = 0
        middle = np.argmax(avel)
        top_velocity_deg = angular_velocity_deg[middle]
        
        time_middle = timestamp[middle]
        assert time_middle >= time_start and time_middle <= time_stop
        orientation_start = orientation_deg[start]
        orientation_stop = orientation_deg[stop]
        amplitude_deg = orientation_stop - orientation_start
        sign = np.sign(amplitude_deg)
        
        i = start
        saccade = np.ndarray(dtype=saccade_dtype, shape=())
        saccade['top_velocity'] = top_velocity_deg
        saccade['time_start'] = time_start
        saccade['time_middle'] = time_middle
#        saccade['linear_velocity_modulus'] = \
#            annotations['linear_velocity_modulus'][i]  
#        saccade['linear_acceleration_modulus'] = \
#            annotations['linear_acceleration_modulus'][i]
        saccade['time_stop'] = time_stop
        saccade['amplitude'] = amplitude_deg
        saccade['sign'] = sign
        saccade['orientation_start'] = orientation_start
        saccade['orientation_stop'] = orientation_stop
        saccade['top_velocity'] = top_velocity_deg
        saccade['duration'] = duration
        # mamarama data
        saccade['position'] = np.array([rows['x'][i],
                                        rows['y'][i],
                                        rows['z'][i]])
        saccade['linear_velocity_world'] = \
            np.array([rows['xvel'][i], rows['yvel'][i], rows['zvel'][i]])
        saccade['frame'] = rows['frame'][i]
        saccade['obj_id'] = rows['obj_id'][i]
        
        # TODO: who should be setting this?
        saccade['species'] = UNKNOWN
        saccade['stimulus'] = UNKNOWN
        saccade['sample'] = UNKNOWN
        saccade['sample_num'] = -1  # will be filled in by someone else
        saccade['processed'] = UNKNOWN 
        
        saccades.append(saccade)
   
    saccades = saccade_list_to_array(saccades)
    
    return dict(
        angular_velocity_deg=angular_velocity_deg,
        fast_enough=fast_enough,
        angular_velocity_threshold_deg=angular_velocity_threshold_deg,
        saccades=saccades
    )


def plot_angvel_saccade_detect_results(rows):
    ''' Return a Report. '''
    r = Report()
    
    data = angvel_saccade_detect(rows)
    timestamp = rows['timestamp']
    orientation_deg = np.degrees(rows['reduced_angular_orientation'])

    T = timestamp 
    
    f = r.figure(cols=2)
    threshold = data['angular_velocity_threshold_deg']
    with f.plot('angular_velocity_deg') as pylab:
        pylab.plot([T[0], T[-1]], [0, 0], 'k--')
        pylab.plot(T, data['angular_velocity_deg'], '-')
        y_axis_set(pylab, -1500, 1500)
        x_axis_set(pylab, T[0], T[-1])
        pylab.ylabel('angular velocity')

    with f.plot('fast_enough') as pylab:
        pylab.plot([T[0], T[-1]], [0, 0], 'k--')
        pylab.plot(T, data['angular_velocity_deg'], 'k-')
        pylab.plot([T[0], T[-1]], [threshold, threshold], 'b--')
        pylab.plot([T[0], T[-1]], [-threshold, -threshold], 'b--')
        
        i = data['fast_enough'] 
        pylab.plot(T[i], data['angular_velocity_deg'][i], 'b.')
        y_axis_set(pylab, -threshold * 3, threshold * 3)
        x_axis_set(pylab, T[0], T[-1])
        
        pylab.ylabel('angular velocity (deg/s)')
        
    saccades = data['saccades']
    
    def plot_saccades(pylab, saccades):
        def plot_vert(pylab, x, *col):
            a = pylab.axis()
            pylab.plot([x, x], [a[2], a[3]], *col)
            
        for saccade in saccades:
            plot_vert(pylab, saccade['time_start'], 'g')
            plot_vert(pylab, saccade['time_stop'], 'b')
    
    with f.plot('detections') as pylab:
        pylab.plot([T[0], T[-1]], [0, 0], 'k--')
        pylab.plot(T, data['angular_velocity_deg'], 'k-')
        pylab.plot([T[0], T[-1]], [threshold, threshold], 'b--')
        pylab.plot([T[0], T[-1]], [-threshold, -threshold], 'b--')
        
        y_axis_set(pylab, -threshold * 3, threshold * 3)
        x_axis_set(pylab, T[0], T[-1])
        plot_saccades(pylab, saccades)
        
        pylab.ylabel('angular velocity (deg/s)')
        
    with f.plot('orientation') as pylab:
        pylab.plot(T, orientation_deg, 'k-') 
        
#        y_axis_set(pylab, -threshold * 3, threshold * 3)
#        x_axis_set(pylab, T[0], T[-1])
#        plot_saccades(pylab, saccades)
        
        for saccade in saccades:
            a = saccade['orientation_start']
            b = saccade['orientation_stop']
            t0 = saccade['time_start']
            t1 = saccade['time_stop']
            pylab.plot([t0, t1], [a, b], 'b-', linewidth=5)
             
        pylab.ylabel('orientation (deg)')
        
    return r
    

def find_sequences(x):
    ''' Finds all True subsequences in x. '''
    i = 0
    n = len(x)
    while i < n:
        # find next true element
        while i < n and not x[i]: 
            i += 1
        if i == n: return
        # find next false element
        j = i + 1
        while j < n and x[j]:
            j += 1            
        yield i, j
        i = j + 1
    
    
    
    
    



