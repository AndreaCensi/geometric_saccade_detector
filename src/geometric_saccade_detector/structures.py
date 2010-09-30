
# This is the subset of the dtype that we use.
# (sometimes flydra puts more info in the returned array, and
#  we strip it)
rows_dtype = [  
    ('timestamp', 'float64'),
    ('obj_id', 'int'),
    ('x', 'float32'),
    ('y', 'float32'),
    ('xvel', 'float32'),
    ('yvel', 'float32')
]


saccade_dtype = [
    ('time_middle', 'float64'),
    ('time_start', 'float64'),
    ('time_stop', 'float64'),
    ('orientation_start', 'float64'),
    ('orientation_stop', 'float64'),
    ('time_passed', 'float64'),
    ('sign', 'int8'),
    ('amplitude', 'float64'),
    ('duration', 'float64'),
    ('position', 'float64', (3,)),
    ('linear_velocity_modulus', 'float64'),
    ('linear_acceleration_modulus', 'float64'),
    ('velocity', 'float64'),
    ('velocity_vector', 'float64', (3,)),
    
    ('num_samples_used_before', 'uint8'),
    ('num_samples_used_after', 'uint8')
    ]

annotation_dtype = map(lambda x: (x, 'float64'),
                       ['before_orientation',
                        'before_dispersion',
                        'after_orientation',
                        'after_dispersion',
                        'turning_angle',
                        'preference',
                        'linear_velocity_modulus',
                        'linear_acceleration_modulus',
                        'amplitude']) + \
                        [('considered', 'uint8'),
                         ('marked_as_used', 'uint8'),
                          ('sign', 'int8'),
                          ('candidate', 'uint8'),
                          ('num_samples_used_before', 'uint8'),
                          ('num_samples_used_after', 'uint8')]


