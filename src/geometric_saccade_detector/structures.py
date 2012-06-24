
# This is the subset of the dtype that we use.
# (sometimes flydra puts more info in the returned array, and
#  we strip it)
rows_dtype = [  
    ('timestamp', 'float64'),
    ('obj_id', 'int'),
    ('frame', 'int'),
    ('x', 'float32'),
    ('y', 'float32'),
    ('z', 'float32'),
    ('xvel', 'float32'),
    ('yvel', 'float32'),
    ('zvel', 'float32'),
]

# Note that all this data is expressed in degrees, not radians.
saccade_dtype = [
    # Standard saccade representation
    ('time_start', 'float64'),
    ('time_stop', 'float64'),
    
     # degrees
    ('orientation_start', 'float64'),
    
    # degrees
    ('orientation_stop', 'float64'),
    
    ('time_passed', 'float64'),
    ('sign', 'int8'),
    
    # degrees
    ('amplitude', 'float64'),
    
    ('duration', 'float64'),
    
    # angular velocity, degrees/second
    ('top_velocity', 'float64'),
    
    # other fields used for managing different samples, used in the analysis
    ('species', 'S32'),
    ('stimulus', 'S32'),
    
    # format: 'YYYYMMDD_HHmmSS'
    ('sample', 'S64'),
    
    # unique index for the sample
    # This is filled in later
    ('sample_num', 'int'),
                           
    # other debug fields, not used in the analysis
    # timestamp and processing host
    ('processed', 'S128'),
    
    # Specific to mamarama data
    ('time_middle', 'float64'),
    ('frame', 'int'),
    ('obj_id', 'int'),
    ('position', ('float64', 3)),
    ('linear_velocity_world', ('float64', 3)),
    
    # m/s
    ('linear_velocity_modulus', 'float64'),
    ('linear_acceleration_modulus', 'float64'),
    ('smooth_displacement', 'float64'),

    # Number of samples used to average orientation_start,_stop.
    ('num_samples_used_before', 'uint8'),
    ('num_samples_used_after', 'uint8')
]

# These are the fields that are added to the rows containing the
# intermediate computations.
# Note that all this data is expressed in *radians*, not degrees.
annotation_dtype = [
                    # XXX repeated?
    ('orientation_start', 'float64'),
    ('orientation_stop', 'float64'),
    ('before_dispersion', 'float64'),
    ('after_dispersion', 'float64'),
    ('turning_angle', 'float64'),
    ('preference', 'float64'),
    ('linear_velocity_modulus', 'float64'),
    ('linear_acceleration_modulus', 'float64'),
    ('linear_velocity_modulus_smooth', 'float64'),
    ('linear_acceleration_modulus_smooth', 'float64'),
    ('angular_velocity_modulus', 'float64'),
    ('amplitude', 'float64'),
    ('considered', 'uint8'),
    ('sign', 'int8'),
    ('marked_as_used', 'uint8'),
    ('num_samples_used_before', 'uint8'),
    ('num_samples_used_after', 'uint8'),
    ('candidate', 'uint8'),
]

UNKNOWN = '?'


def saccade_description(saccade):
    s = 'Saccade structure:'
    for field, _ in saccade_dtype:
        s += '\n  %30s : %s ' % (field, saccade[field])
    return s
    
