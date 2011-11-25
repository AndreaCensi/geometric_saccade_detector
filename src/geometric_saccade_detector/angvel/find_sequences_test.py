from geometric_saccade_detector.angvel.angvel_detect import find_sequences
from numpy.testing.utils import assert_allclose

def find_sequences_test_1():
    
    pairs = [
             
            ([0, 0, 0, 0, 0], []),
            ([1, 0, 0, 0, 0], [ (0, 1)]),
            ([1, 1, 1, 0, 0], [ (0, 3)]),
            ([0, 1, 1, 0, 0], [ (1, 3)]),
            ([0, 1, 1, 1, 1], [ (1, 5)]),
            ([1, 1, 1, 1, 1], [ (0, 5)]),
            ([1, 1, 0, 1, 1], [ (0, 2), (3, 5)]),
    ]
    
    for x, res in pairs:
        result = list(find_sequences(x))
        assert_allclose(res, result, err_msg='Failure for %s' % x) 
    
