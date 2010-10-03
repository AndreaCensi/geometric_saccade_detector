
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

# Note that all this data is expressed in degrees, not radians.
saccade_dtype = [
    # Standard saccade representation
    ('time_start', 'float64'),
    ('time_stop', 'float64'),
    ('orientation_start', 'float64'), # degrees
    ('orientation_stop', 'float64'), # degrees
    ('time_passed', 'float64'),
    ('sign', 'int8'),
    ('amplitude', 'float64'), # degrees
    # the following are not computed meaningfully 
    ('duration', 'float64'),
    ('top_velocity', 'float64'), # angular velocity, degrees/second
    
    # other fields used for managing different samples, used in the analysis
    ('species', 'S255'),
    ('stimulus', 'S255'),
    ('sample', 'S255'), # format: 'YYYYMMDD_HHmmSS'
    ('sample_num', 'int'), # unique index for the sample
                           # This is filled in later

    # other debug fields, not used in the analysis
    ('processed', 'S255'), # timestamp and processing host
    
    # Specific to mamarama data
    ('time_middle', 'float64'),
    ('x', 'float64'), # x position in arena
    ('y', 'float64'), # y position in arena
    ('linear_velocity_modulus', 'float64'), # m/s
    ('linear_acceleration_modulus', 'float64'),

    # Number of samples used to average orientation_start,_stop.
    ('num_samples_used_before', 'uint8'),
    ('num_samples_used_after', 'uint8')
]

# These are the fields that are added to the rows containing the
# intermediate computations.
# Note that all this data is expressed in *radians*, not degrees.
annotation_dtype = [
    ('orientation_start', 'float64'),
    ('orientation_stop', 'float64'),
    ('before_dispersion', 'float64'),
    ('after_dispersion', 'float64'),
    ('turning_angle', 'float64'),
    ('preference', 'float64'),
    ('linear_velocity_modulus', 'float64'),
    ('linear_acceleration_modulus', 'float64'),
    ('amplitude', 'float64'),
    ('considered', 'uint8'),
    ('sign', 'int8'),
    ('marked_as_used', 'uint8'),
    ('num_samples_used_before', 'uint8'),
    ('num_samples_used_after', 'uint8'),
    ('candidate', 'uint8'),
]

