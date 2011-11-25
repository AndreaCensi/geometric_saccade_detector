from . import logger, np
from .. import __version__
from ..utils import (LenientOptionParser, wrap_script_entry_point,
    get_computed_string)
from flydra_db import safe_flydra_db_open
from flydra_db.constants import NamingConventions
import warnings
from geometric_saccade_detector.angvel.angvel_detect import angvel_saccade_detect, \
    plot_angvel_saccade_detect_results
import os
from reprep import Report
from geometric_saccade_detector.well_formed_saccade import check_saccade_is_well_formed


usage = """

    %prog  --db <flydra_db> --version row_version

"""

def detect_angvel(argv):
    np.seterr(all='raise')
                 
    parser = LenientOptionParser(usage=usage)

    parser.add_option("--db", help="FlydraDB directory.")

    parser.add_option("--version", default='smooth', type='string',
                      help="[=%default] Which version of the 'rows' table to use.")
     
    parser.add_option("--saccades_table_version", default='angvel', type='string',
                      help='[=%default] Version of output saccades tables.')

    parser.add_option("--nocache", help="Ignores already computed results.",
                      default=False, action="store_true")


    parser.add_option("--out", help="Output directory for graphic representation.")


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
    
    (options, args) = parser.parse_args(argv)
    
    if not options.db:
        raise Exception('No flydra DB directory  specified.')
    
    if args:
        raise Exception('Spurious arguments')
    
        
    # Create processed string
    processed = get_computed_string('angvel_saccade_detector', __version__)
        
    rows_table_name = NamingConventions.ROWS_TABLE
    rows_table_version = options.version
    saccades_table_name = NamingConventions.SACCADES_TABLE
    annotations_table_name = 'annotated'
    saccades_table_version = options.saccades_table_version

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
                 
                rows = np.array(rows[:])
                params = {}
#                saccades, annotated 
                data = angvel_saccade_detect(rows, **params)
                saccades = data['saccades'] 
                
        
                for saccade in saccades:
                    check_saccade_is_well_formed(saccade)
        
                
                DT = rows['timestamp'][-1] - rows['timestamp'][0]  
                logger.info("%4d/%d %s: %6d saccades for %6d rows (%6g saccades/s)" % 
                    (i, len(samples), sample,
                     len(saccades), len(rows), DT / len(saccades))) 
       
       
                if True:
                    db.set_table(sample=sample,
                                 table=saccades_table_name,
                                 data=saccades,
                                 version=saccades_table_version)
                     
                    db.set_attr(sample,
                                'saccades_%s_processed' % saccades_table_version,
                                processed)
                
                if options.out is not None:
                    outdir = os.path.join(options.out, 'angvel_sac_detect')
                    if not os.path.exists(outdir):
                        os.makedirs(outdir)
                    resources = os.path.join(outdir, 'images')
                    filename = os.path.join(outdir, '%s.html' % sample)
                 
                    r = Report()
                    
                    chunks = enumerate_chunks(len(rows), max_chunk_size=300)
                    for i, select in enumerate(chunks):
                        rows_i = rows[select]
                    
                        ri = plot_angvel_saccade_detect_results(rows_i)
                        ri.nid = 'chunk_%s' % i
                        r.add_child(ri)
                    
                    logger.info('Writing to %r.' % filename)
                    r.to_html(filename, resources_dir=resources)
                    #sys.exit(0)
                
def enumerate_chunks(N, max_chunk_size):
    nchunks = int(np.ceil(N * 1.0 / max_chunk_size))
    
    for i in range(nchunks):
        begin = i * max_chunk_size
        end = min(begin + max_chunk_size, N)
        yield range(begin, end)

def main():
    wrap_script_entry_point(detect_angvel, logger)


if __name__ == '__main__':
    main()
        

