#!/usr/bin/env python
import pickle, os, scipy.io, numpy, sys
from optparse import OptionParser 

from geometric_saccade_detector import logger
from geometric_saccade_detector.debug_output import write_debug_output
from geometric_saccade_detector.flydra_db_utils import get_good_smoothed_tracks, \
    get_good_files
from geometric_saccade_detector.algorithm import geometric_saccade_detect


def main():
    parser = OptionParser()

    parser.add_option("--output_dir", default='saccade_detect_output',
                      help="Output directory")

    parser.add_option("--min_frames_per_track", default=400,
        help="Minimum number of frames per track [default: %default]")

    parser.add_option("--confirm_problems",
                      help="Stop interactively on problems with log files'\
                      '(e.g.: cannot find valid obj_ids) [default: %default]",
                      default=False, action="store_true")

    parser.add_option("--dynamic_model_name",
                      help="Smoothing dynamical model [default: $default]",
                      default="mamarama, units: mm")
    
    parser.add_option("--debug_output", help="Creates debug figures",
                      default=False, action="store_true")

    parser.add_option("--smoothing", help="Uses Kalman-smoothed data.",
                      default=False, action="store_true")

    # detection parameters
    dt = 1.0 / 60
    parser.add_option("--deltaT_inner_sec", default=4 * dt, type='float',
                      help="Inner interval")
    parser.add_option("--deltaT_outer_sec", default=10 * dt, type='float',
                      help="Outer interval")
    parser.add_option("--min_amplitude_deg", default=15, type='float',
                      help="Minimum saccade amplitude (deg)")
    parser.add_option("--min_linear_velocity", default=0.05, type='float',
                      help="Minimum linear velocity when saccading (m/s)")
    parser.add_option("--max_orientation_dispersion_deg", default=15, type='float',
                      help="Maximum dispersion (deg)")
    parser.add_option("--minimum_interval_sec", default=10 * dt, type='float',
                      help="Minimum interval between saccades.")
    
    (options, args) = parser.parse_args()

    if not os.path.exists(options.output_dir):
        os.makedirs(options.output_dir)


    good_files = get_good_files(where=args, pattern="*.kh5",
                                confirm_problems=options.confirm_problems)

    if len(good_files) == 0:
        logger.error("No good files to process")
        sys.exit(1)

    n = len(good_files)
    for i in range(n):
        (filename, obj_ids, stim_fname) = good_files[i]
    
        basename = os.path.splitext(os.path.basename(filename))[0]
        
        output_saccades_mat = os.path.join(options.output_dir,
                                           basename + '-saccades.mat')        
        output_saccades_pickle = os.path.join(options.output_dir,
                                              basename + '-saccades.pickle')
        if os.path.exists(output_saccades_mat):
            logger.info('File %s exists; skipping.' % output_saccades_mat)
            continue
        
        logger.info("File %d/%d %s %s %s " % (i, n, str(filename), str(obj_ids), stim_fname))
        
        # concatenate all in one track
        all_data = None

        for obj_id, rows in get_good_smoothed_tracks(
                filename=filename,
                obj_ids=obj_ids,
                min_frames_per_track=options.min_frames_per_track,
                dynamic_model_name=options.dynamic_model_name,
                use_smoothing=options.smoothing):

            all_data = rows.copy() if all_data is None \
                        else numpy.concatenate((all_data, rows))                
        
        if all_data is None:
            logger.info('Not enough data found for %s; skipping.' % filename)
            continue
        
        params = {
          'deltaT_inner_sec': options.deltaT_inner_sec   ,
          'deltaT_outer_sec':  options. deltaT_outer_sec  ,
          'min_amplitude_deg':  options.min_amplitude_deg   ,
          'max_orientation_dispersion_deg': options.max_orientation_dispersion_deg   ,
          'minimum_interval_sec':  options.minimum_interval_sec,
          'min_linear_velocity': options.min_linear_velocity
        }
        saccades, annotated_data = geometric_saccade_detect(all_data, params)

        
        # Write matlab output
        
        logger.info("Writing to %s" % output_saccades_mat)
        scipy.io.savemat(output_saccades_mat, {'saccades':saccades},
                         oned_as='column')
    
        # Write pickle output
        logger.info("Writing to %s" % output_saccades_pickle)
        pickle.dump(saccades, open(output_saccades_pickle, 'wb'))
    
        # Write debug figures
        if options.debug_output:
            debug_output_dir = os.path.join(options.output_dir, basename)
            logger.info("Writing HTML+png to %s" % debug_output_dir)    
            write_debug_output(debug_output_dir, basename,
                               annotated_data, saccades)
      

    sys.exit(0)



if __name__ == '__main__':
    main()






