from . import logger, __version__, np  # XXX: make this coherent
from .algorithm import geometric_saccade_detect
from .debug_output import write_debug_output
from .flydra_db_utils import (get_good_smoothed_tracks, get_good_files,
    timestamp_string_from_filename)
from .io import saccades_write_all
from .utils import get_user
from .well_formed_saccade import check_saccade_is_well_formed
from datetime import datetime
from optparse import OptionParser
import os
import sys
import platform
import traceback

import flydra.a2.core_analysis as core_analysis  # @UnresolvedImport
   

def main():
    np.seterr(all='raise')
                 
    parser = OptionParser()

    parser.add_option("--output_dir", default='saccade_detect_output',
                      help="Output directory")

    parser.add_option("--min_frames_per_track", default=400,
        help="Minimum number of frames per track [= %default]")

    parser.add_option("--confirm_problems",
                      help="Stop interactively on problems with log files'\
                      '(e.g.: cannot find valid obj_ids) [default: %default]",
                      default=False, action="store_true")

    parser.add_option("--dynamic_model_name",
                      help="Smoothing dynamical model [default: %default]",
                      default="mamarama, units: mm")
    
    parser.add_option("--debug_output", help="Creates debug figures.",
                      default=False, action="store_true")

    parser.add_option("--nocache", help="Ignores already computed results.",
                      default=False, action="store_true")

    parser.add_option("--smoothing", help="Uses Kalman-smoothed data.",
                      default=False, action="store_true")

    # detection parameters
    dt = 1.0 / 60
    parser.add_option("--deltaT_inner_sec", default=4 * dt, type='float',
                      help="Inner interval [= %default]")
    parser.add_option("--deltaT_outer_sec", default=10 * dt, type='float',
                      help="Outer interval [= %default]")
    parser.add_option("--min_amplitude_deg", default=25, type='float',
                      help="Minimum saccade amplitude (deg) [= %default]")
    parser.add_option("--min_linear_velocity", default=0.1, type='float',
                      help="Minimum linear velocity when saccading (m/s) "
                            "[= %default]")
    parser.add_option("--max_linear_acceleration", default=20, type='float',
                      help="Maximum linear acceleration when saccading "
                      "(m/s^2) [= %default]")
    parser.add_option("--max_angular_velocity", default=8000, type='float',
                      help="Maximum angular velocity when saccading (deg/s) "
                      "[= %default]")
    parser.add_option("--max_orientation_dispersion_deg", default=15,
                      type='float',
                      help="Maximum dispersion (deg) [= %default]")
    parser.add_option("--minimum_interval_sec", default=10 * dt, type='float',
                      help="Minimum interval between saccades. [= %default]")
    
    (options, args) = parser.parse_args()
    
    if not args:
        logger.error('No files or directories specified.')
        sys.exit(-1)
        
    # Create processed string
    processed = 'geometric_saccade_detector %s %s %s@%s Python %s' % \
                (__version__, datetime.now().strftime("%Y%m%d_%H%M%S"),
                 get_user(), platform.node(), platform.python_version())
        
    if not os.path.exists(options.output_dir):
        os.makedirs(options.output_dir)

    good_files = get_good_files(where=args, pattern="*.kh5",
                                confirm_problems=options.confirm_problems)

    if len(good_files) == 0:
        logger.error("No good files to process.")
        sys.exit(1)

    try:
        n = len(good_files)
        for i in range(n):
            (filename, obj_ids, stim_fname) = good_files[i]
            # only maintain basename
            stim_fname = os.path.splitext(os.path.basename(stim_fname))[0]
            basename = os.path.splitext(os.path.basename(filename))[0]
            
            output_basename = os.path.join(options.output_dir,
                                           basename + '-saccades')        
            output_saccades_hdf = output_basename + '.h5'
                
            if os.path.exists(output_saccades_hdf) and not options.nocache:
                logger.info('File %r exists; skipping. '
                            '(use --nocache to ignore)' % 
                                 output_saccades_hdf)
                continue
            
            logger.info("File %d/%d %s %s %s " % 
                        (i, n, str(filename), str(obj_ids), stim_fname))
            
            # concatenate all in one track
            all_data = None
    
            for _, rows in get_good_smoothed_tracks(
                    filename=filename,
                    obj_ids=obj_ids,
                    min_frames_per_track=options.min_frames_per_track,
                    dynamic_model_name=options.dynamic_model_name,
                    use_smoothing=options.smoothing):
    
                all_data = rows.copy() if all_data is None \
                            else np.concatenate((all_data, rows))                
            
            if all_data is None:
                logger.info('Not enough data found for %s; skipping.' % 
                            filename)
                continue
            
            params = {
              'deltaT_inner_sec': options.deltaT_inner_sec,
              'deltaT_outer_sec': options. deltaT_outer_sec,
              'min_amplitude_deg': options.min_amplitude_deg,
              'max_orientation_dispersion_deg': 
                        options.max_orientation_dispersion_deg,
              'minimum_interval_sec': options.minimum_interval_sec,
              'max_linear_acceleration': options.max_linear_acceleration,
              'min_linear_velocity': options.min_linear_velocity,
              'max_angular_velocity': options.max_angular_velocity,
            }
            saccades, annotated_data = geometric_saccade_detect(all_data,
                                                                params)
    
            for saccade in saccades:
                check_saccade_is_well_formed(saccade)
                
            # other fields used for managing different samples, 
            # used in the analysis
            saccades['species'] = 'Dmelanogaster'
            saccades['stimulus'] = stim_fname
            sample_name = 'DATA' + timestamp_string_from_filename(filename)
            saccades['sample'] = sample_name
            saccades['sample_num'] = -1  # will be filled in by someone else
            saccades['processed'] = processed    
        
            logger.info("Writing to %s {h5,mat,pickle}" % output_basename)
            saccades_write_all(output_basename, saccades)
            
            # Write debug figures
            if options.debug_output:
                debug_output_dir = os.path.join(options.output_dir, basename)
                logger.info("Writing HTML+png to %s" % debug_output_dir)    
                write_debug_output(debug_output_dir, basename,
                                   annotated_data, saccades)
 
    except Exception as e:
        logger.error('Error while processing. Exception and traceback follow.')
        logger.error(str(e))
        logger.error(traceback.format_exc())
        sys.exit(-2)
        
    finally:
        print('Closing flydra cache')
        ca = core_analysis.get_global_CachingAnalyzer()
        ca.close()
        
    sys.exit(0)


if __name__ == '__main__':
    main()


