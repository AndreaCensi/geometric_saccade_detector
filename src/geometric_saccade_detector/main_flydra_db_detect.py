from . import __version__, logger, np
from .algorithm import geometric_saccade_detect
from .debug_output import write_debug_output
from .utils import (LenientOptionParser, wrap_script_entry_point,
    get_computed_string)
from .well_formed_saccade import check_saccade_is_well_formed
from flydra_db import safe_flydra_db_open
import os
import warnings

usage = """

    %cmd  --db <flydra_db> --version row_version

"""

def flydra_db_detect(args):
    np.seterr(all='raise')
                 
    parser = LenientOptionParser(usage=usage)

    parser.add_option("--db", help="FlydraDB directory.")

    parser.add_option("--version", default=None, type='string',
                      help="Which version of the 'rows' table to use.")
    
    parser.add_option("--debug_output", help="Creates debug figures.",
                      default=False, action="store_true")

    parser.add_option("--nocache", help="Ignores already computed results.",
                      default=False, action="store_true")

    # detection parameters
    dt = 1.0 / 60 # XXX: read from file
    warnings.warn('Using fixed dt = %s.' % dt)
    parser.add_option("--deltaT_inner_sec", default=4 * dt, type='float',
                      help="Inner interval [= %default]")
    parser.add_option("--deltaT_outer_sec", default=10 * dt, type='float',
                      help="Outer interval [= %default]")
    parser.add_option("--min_amplitude_deg", default=25, type='float',
                      help="Minimum saccade amplitude (deg) [= %default]")
    parser.add_option("--min_linear_velocity", default=0.1, type='float',
                      help="Minimum linear velocity when saccading (m/s) [= %default]")
    parser.add_option("--max_linear_acceleration", default=20, type='float',
                      help="Maximum linear acceleration when saccading (m/s^2) [= %default]")
    parser.add_option("--max_angular_velocity", default=8000, type='float',
                      help="Maximum angular velocity when saccading (deg/s) [= %default]")
    parser.add_option("--max_orientation_dispersion_deg", default=15, type='float',
                      help="Maximum dispersion (deg) [= %default]")
    parser.add_option("--minimum_interval_sec", default=10 * dt, type='float',
                      help="Minimum interval between saccades. [= %default]")
    
    (options, args) = parser.parse_args(args)
    
    if not options.db:
        raise Exception('No flydra DB directory  specified.')
    
    if args:
        raise Exception('Spurious arguments')
    
        
    # Create processed string
    processed = get_computed_string('geometric_saccade_detector', __version__)

        
    rows_table_name = 'rows'
    rows_table_version = options.version
    saccades_table_name = 'saccades'
    annotations_table_name = 'annotated'
    saccades_table_version = options.version

    with safe_flydra_db_open(options.db) as db:
        samples = db.list_samples()

        for i, sample in enumerate(samples):
           
            already_has = db.has_table(sample, saccades_table_name,
                                       saccades_table_version)
                
            if options.nocache and already_has:
                msg = ('Sample %r already has table %s:%s; skipping.' % 
                       (sample, saccades_table_name, saccades_table_version))
                logger.info(msg)
                continue
            
            if not db.has_table(sample, rows_table_name, rows_table_version):
                msg = ('Sample %r does not have table %s:%s.' % 
                       (sample, rows_table_name, rows_table_version))
                raise Exception(msg)
            
            with db.safe_get_table(sample, rows_table_name,
                                   rows_table_version) as rows:
                 
                params = {
                  'deltaT_inner_sec': options.deltaT_inner_sec,
                  'deltaT_outer_sec':  options. deltaT_outer_sec,
                  'min_amplitude_deg':  options.min_amplitude_deg,
                  'max_orientation_dispersion_deg': 
                    options.max_orientation_dispersion_deg,
                  'minimum_interval_sec':  options.minimum_interval_sec,
                  'max_linear_acceleration':  options.max_linear_acceleration,
                  'min_linear_velocity': options.min_linear_velocity,
                  'max_angular_velocity': options.max_angular_velocity,
                }
                
                rows = np.array(rows[:])
                saccades, annotated = geometric_saccade_detect(rows, params)
        
                for saccade in saccades:
                    check_saccade_is_well_formed(saccade)
        
                dt = 1.0 / 60
                logger.info("%4d/%d %s: %d saccades for %d rows (%g saccades/s)" % 
                    (i, len(samples), sample,
                     len(saccades), len(rows), len(rows) * dt / len(saccades))) 
       
       
                db.set_table(sample=sample,
                             table=saccades_table_name,
                             data=saccades,
                             version=saccades_table_version)
                
                db.set_table(sample=sample,
                             table=annotations_table_name,
                             data=annotated,
                             version=saccades_table_version)
            
                db.set_attr(sample,
                            'saccades_%s_processed' % saccades_table_version,
                            processed)
            
            # Write debug figures
            if options.debug_output:
                
                if not os.path.exists(options.output_dir):
                    os.makedirs(options.output_dir)
                basename = sample
                debug_output_dir = os.path.join(options.output_dir, basename)
                logger.info("Writing HTML+png to %s" % debug_output_dir)    
                write_debug_output(debug_output_dir, basename,
                                   annotated, saccades)


def main():
    wrap_script_entry_point(flydra_db_detect, logger)


if __name__ == '__main__':
    main()
        



