import numpy
import unittest
from geometric_saccade_detector.math_utils import compute_derivative,\
    merge_fields


class UtilsTest(unittest.TestCase):
    ''' Tests some of the utility functions. '''
        
    def merge_fields_test(self):
        shape = (4, 3)
        a = numpy.ndarray(shape=shape, dtype=[('field1', 'uint8')])
        b = numpy.ndarray(shape=shape, dtype=[('field2', 'float64')])
        c = merge_fields(a, b)
        self.assertEqual(set(['field1', 'field2']), set(c.dtype.fields.keys()))
        self.assertEqual(c.shape, a.shape)

    def merge_fields_test_failure(self):
        ''' If fields with the same name, it should fail. '''
        shape = (4, 1)
        a = numpy.ndarray(shape=shape, dtype=[('field1', 'uint8')])
        b = numpy.ndarray(shape=shape, dtype=[('field1', 'float64')])
        self.assertRaises(ValueError, merge_fields, a, b)
        

    def derivative_test(self):
        
        t = numpy.linspace(1,10,20)
        x = t ** 2
        
        dx = compute_derivative(x,t)
        ddx= compute_derivative(dx,t)
        
        self.assertTrue( (dx >= 0).all() )
        self.assertTrue( (ddx >= 0).all() )