import numpy as np

def check_saccade_is_well_formed(saccade):
    
    check_not_nan = [
        'time_start',
        'time_stop',
        'orientation_start', 
        'orientation_stop', 
        'time_passed', 
        'sign', 
        'amplitude', 
        'duration', 
        'top_velocity',
    ]
    
    try: 
            
        for x in check_not_nan:
            if not np.isfinite(saccade[x]):
                raise Exception('Not finite values in %r' % x)
        
        if saccade['time_stop'] <= saccade['time_start']:
            raise Exception('Incoherent values of time_start, time_stop')
            
        
        #assert_allclose(saccade['amplitude'],  np.abs(saccade['orientation_start']-
        #                                              saccade['orientation_stop']) 
        if not (saccade['sign'] == -1 or saccade['sign'] == 1):
            raise Exception('Strange value for sign: %r' % saccade['sign'])
        
        
        
        if not np.isfinite(saccade['position']).all():
            raise Exception('Invalid position')
    except Exception as e:
        
        msg = str(e)
        msg += '\n\tDType: %s\n\tvalues: %s' % (saccade.dtype, str(saccade))
        raise Exception(e)