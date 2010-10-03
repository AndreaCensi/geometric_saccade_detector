import numpy
from geometric_saccade_detector import logger
from geometric_saccade_detector.structures import saccade_dtype, annotation_dtype
from geometric_saccade_detector.math_utils import merge_fields, \
    compute_derivative, find_indices_in_bounds, get_orientation_and_dispersion, \
    normalize_pi, smooth1d
                                 
def geometric_saccade_detect(rows, params):
    ''' Detects saccades in a log fragment. 
    
        Rows is a numpy array with at least the fields
            timestamp, obj_id, x, y, xvel, yvel.
        
        params should be a dict with the following keys:
          'deltaT_inner_sec',
          'deltaT_outer_sec',
          'min_amplitude_deg',
          'max_orientation_dispersion_deg',
          'min_linear_velocity',
          'minimum_interval_sec',
          'max_linear_acceleration',
          'max_angular_velocity'
        
        Returns a tuple of two numpy arrays. 
        The first is the saccade array (using saccade_dtype),
        the other is a copy of rows with additional fields
        describing the intermediate computation, useful for debug
        purposes.
    '''
    minimum_acceptable_length = 30
    
    # do some sanity tests
    if not isinstance(rows, numpy.ndarray):
        raise ValueError('Expected ndarray, not %s' % rows.__class__.__name__)
    
    if len(rows.shape) != 1:
        raise ValueError('Expected unidimensional ndarray, got shape %s.' % 
                         str(rows.shape))
    
    if len(rows) <= minimum_acceptable_length:
        raise ValueError('I cannot do much with only %s entries.' % len(rows))
    
    required_fields = ['obj_id', 'timestamp', 'x', 'y', 'xvel', 'yvel']
    for field in required_fields:
        if not field in rows.dtype.fields:
            raise ValueError('Cannot find required field "%s" in dtype %s' % \
                             field, rows.dtype)
        values = rows[field]
        num_nan = numpy.isnan(values).sum()
        num_inf = numpy.isinf(values).sum()
        if num_nan > 0 or num_inf > 0:
            raise ValueError('Found invalid data for field "%s": '
                             'nan %d inf %d (len %d)' % \
                             (field, num_nan, num_inf, len(rows)))
        
    
    # check that timestamp is increasing and reasonably spaced
    # (we allow "missing" parts from the data, but it should be
    #  at most a few seconds)
    timestamp = rows['timestamp']
    obj_id = rows['obj_id']
    
    # check each consecutive pair of rows that have the same obj_id
    for i in range(len(rows) - 1):
        if obj_id[i] != obj_id[i + 1]:
            continue
        
        if not timestamp[i] < timestamp[i + 1]:
            raise ValueError('Invalid timestamp sequence %.3f %.3f at index %d/%d: ' % \
                             (timestamp[i], timestamp[i + 1], i, len(timestamp)) + \
                             str(rows[i]), str(rows[i + 1]))
        dt = timestamp[i + 1] - timestamp[i]
        # print dt, 'fps', int(1 / dt)
        maximum_dt_allowed = 60
        if dt > maximum_dt_allowed:
            raise ValueError('Detected dt %.3f > %.3f at index %d/%d' % \
                             (dt, maximum_dt_allowed, i, len(rows)))
    

    #saccades = numpy.ndarray(dtype=saccade_dtype, shape=(0,))    
    
    annotations = numpy.ndarray(dtype=annotation_dtype, shape=rows.shape)
    
    # Get parameters for detection
    
    deltaT_inner_sec = params['deltaT_inner_sec']
    min_amplitude_deg = params['min_amplitude_deg']
    max_orientation_dispersion_deg = params['max_orientation_dispersion_deg']
    deltaT_outer_sec = params['deltaT_outer_sec']
    minimum_interval_sec = params['minimum_interval_sec']
    min_linear_velocity = params['min_linear_velocity']
    max_linear_acceleration = params['max_linear_acceleration']
    max_angular_velocity = params['max_angular_velocity']
    
    assert deltaT_inner_sec < deltaT_outer_sec
    
    xvel, yvel = rows['xvel'], rows['yvel']
    
    # compute velocity and acceleration
    annotations['linear_velocity_modulus'] = numpy.sqrt(xvel ** 2 + yvel ** 2)
    
    xacc = compute_derivative(rows['xvel'], timestamp)
    yacc = compute_derivative(rows['yvel'], timestamp)
    annotations['linear_acceleration_modulus'] = numpy.sqrt(xacc ** 2 + yacc ** 2)
    
    # smooth both to compute angular velocity
    annotations['linear_velocity_modulus_smooth'] = \
        smooth1d(annotations['linear_velocity_modulus'],
                 window_len=5, window='hanning')
    annotations['linear_acceleration_modulus_smooth'] = \
        smooth1d(annotations['linear_acceleration_modulus'],
                 window_len=5, window='hanning')
    
    #annotations['angular_velocity_modulus'] = \
    #   annotations['linear_acceleration_modulus'] / annotations['linear_velocity_modulus']
    annotations['angular_velocity_modulus'] = \
        annotations['linear_acceleration_modulus_smooth'] / \
        annotations['linear_velocity_modulus_smooth']
        
    for i in range(len(rows)):
        
        # make sure we have enough log before and after
        if (timestamp[i] - timestamp[0] < deltaT_outer_sec) or \
           (timestamp[-1] - timestamp[i] < deltaT_inner_sec):
            continue
        
        # find the indices j such that
        # timestamp[i] - params.DeltaTOuter <  timestamp[j]  < timestamp[i] - params.DeltaTInner

        before = find_indices_in_bounds(timestamp,
                    lower_bound=timestamp[i] - deltaT_outer_sec,
                    upper_bound=timestamp[i] - deltaT_inner_sec)
        after = find_indices_in_bounds(timestamp,
                    lower_bound=timestamp[i] + deltaT_inner_sec,
                    upper_bound=timestamp[i] + deltaT_outer_sec)
      
        # TODO: check obj_id as well
        
        if len(before) < 2 or len(after) < 2:
            annotations['considered'][i] = 0
            annotations['candidate'][i] = 0 
            continue

        # these are orientation and dispersion of each branch
        before_orientation_inverted, before_dispersion = \
            get_orientation_and_dispersion(rows, center=i, indices=before)
            
        orientation_start = before_orientation_inverted + numpy.pi
 
        orientation_stop, after_dispersion = \
            get_orientation_and_dispersion(rows, center=i, indices=after)

        
        # the net angle is estimated as  before_orientation - after_orientation
        
        turning_angle = normalize_pi(orientation_start - orientation_stop) 
        amplitude = abs(turning_angle)
        
        candidate = \
            (before_dispersion <= numpy.radians(max_orientation_dispersion_deg)) and \
            (after_dispersion <= numpy.radians(max_orientation_dispersion_deg)) and \
            (amplitude >= numpy.radians(min_amplitude_deg)) and \
            (annotations['linear_velocity_modulus'][i] >= min_linear_velocity) and \
            (annotations['linear_acceleration_modulus'][i] <= max_linear_acceleration) and \
            (annotations['angular_velocity_modulus'][i] <= numpy.radians(max_angular_velocity)) and \
            (annotations['angular_velocity_modulus'][i] >= numpy.radians(100)) 

        preference = amplitude - 0.5 * before_dispersion - 0.5 * after_dispersion

    
        annotations['considered'][i] = 1
        annotations['orientation_start'][i] = orientation_start
        annotations['orientation_stop'][i] = orientation_stop
        annotations['before_dispersion'][i] = before_dispersion
        annotations['after_dispersion'][i] = after_dispersion
        annotations['turning_angle'][i] = turning_angle
        annotations['amplitude'][i] = amplitude  
        annotations['preference'][i] = preference
        annotations['sign'][i] = numpy.sign(turning_angle)
        annotations['num_samples_used_before'][i] = len(before)
        annotations['num_samples_used_after'][i] = len(after)

        annotations['candidate'][i] = candidate
            
    
    preferences = annotations['preference']
    for i in range(len(rows)):
        if not annotations['considered'][i] or not annotations['candidate'][i]:
            preferences[i] = -15 # like -inf, but nicer in the plots
            
    ordered_indices = numpy.argsort(-preferences)
    # make sure we are sorting from big to small
    assert preferences[ordered_indices[0]] >= preferences[ordered_indices[-1]]
    
    saccades = []
    # while looking for saccades, mark as used 
    annotations['marked_as_used'] = 0
    
    # visit each point in order of preference 
    for i in ordered_indices:
        # skip if it is already part of a saccade
        if annotations['marked_as_used'][i]:
            continue
        # skip if it does not pass the minimum requirements
        if not annotations['candidate'][i]:
            continue
        
        # print "found saccade at %d, time %.2f" % (i, timestamp[i] - timestamp[0])
        
#        from_index = i - annotations['num_samples_used_before'][i]
#        to_index = i + annotations['num_samples_used_after'][i]
#        from_index = i - 1
#        to_index = i + 1
#        top_velocity = \
#            annotations['angular_velocity_modulus'][from_index:(to_index + 1)].max()
        top_velocity = annotations['angular_velocity_modulus'][i]
       
        duration = annotations['amplitude'][i] / top_velocity
        
        # ok, let's mark this point as a saccade 
        saccade = numpy.ndarray(dtype=saccade_dtype, shape=())
        saccade['top_velocity'] = numpy.NaN
        saccade['time_start'] = timestamp[i] - deltaT_outer_sec
        saccade['time_middle'] = timestamp[i]
        saccade['linear_velocity_modulus'] = \
            annotations['linear_velocity_modulus'][i]  
        saccade['linear_acceleration_modulus'] = \
            annotations['linear_acceleration_modulus'][i]
        saccade['time_stop'] = timestamp[i] + deltaT_outer_sec
        saccade['amplitude'] = numpy.degrees(annotations['amplitude'][i])
        saccade['sign'] = annotations['sign'][i]
        saccade['orientation_start'] = numpy.degrees(annotations['orientation_start'][i])
        saccade['orientation_stop'] = numpy.degrees(annotations['orientation_stop'][i])
        saccade['num_samples_used_after'] = annotations['num_samples_used_after'][i]
        saccade['num_samples_used_before'] = annotations['num_samples_used_before'][i]
        saccade['x'] = rows['x'][i]
        saccade['y'] = rows['y'][i]
        saccade['top_velocity'] = numpy.degrees(top_velocity)
        saccade['duration'] = duration
        
        saccades.append(saccade)
        
        # mark the nearby indices as used by this saccade
        nearby_indices = find_indices_in_bounds(timestamp,
                    lower_bound=timestamp[i] - minimum_interval_sec,
                    upper_bound=timestamp[i] + minimum_interval_sec)
        
        annotations['marked_as_used'][nearby_indices] += 1
    
    # sort the saccades chronologically
    saccades.sort(key=lambda x:x['time_start'])
    
    # make sure it is sorted
    if len(saccades) > 1:
        assert saccades[0]['time_start'] < saccades[1]['time_start']
        
    # now compute time_passed; discarding one first saccade
    for i in range(1, len(saccades)):
        saccades[i]['time_passed'] = \
            saccades[i]['time_start'] - saccades[i - 1]['time_start'];  
        assert saccades[i]['time_passed'] > 0
        
    # remove first saccade (cannot compute time_passed)
    saccades.pop(0)
    
    annotated_rows = merge_fields(rows, annotations)
    # convert to a big numpy array, excluding the first
    if len(saccades) > 0:
        n = len(saccades)
        logger.info("Found %d saccades" % n)
        saccades_array = numpy.ndarray(shape=(n,), dtype=saccade_dtype)
        for i in range(n):
            saccades_array[i] = saccades[i]
        #saccades = numpy.concatenate(saccades[1:])
    else:
        logger.info("Warning: no saccades found.")
        saccades_array = numpy.ndarray(dtype=saccade_dtype, shape=(0,))
        
    return saccades_array, annotated_rows

    
