import os, math, numpy

from matplotlib import pylab 

from .math_utils import find_closest_index

def mark_saccades(rows, saccades):
    a = pylab.axis()
    timestamp = rows['timestamp']
    
    for i in range(len(saccades)):
        if not (timestamp[0] <= saccades[i]['time_middle'] <= timestamp[-1]):
            continue
            
        # n_start = saccades[i]['time_start'] - timestamp[0]
        # n_stop = saccades[i]['time_stop'] - timestamp[0]
        n_middle = saccades[i]['time_middle'] - timestamp[0]
        
        #pylab.plot([n_start, n_start], [a[2], a[3]], 'g-')
        pylab.plot([n_middle, n_middle], [a[2], a[3]], 'r-')
        #pylab.plot([n_stop, n_stop], [a[2], a[3]], 'b-')
        pylab.text(n_middle, a[3], "%d" % i)
        
def plot_saccades(rows, saccades):
    timestamp = rows['timestamp']
    
    for i in range(len(saccades)):
        if not (timestamp[0] <= saccades[i]['time_middle'] <= timestamp[-1]):
            continue
        # index in rows
        k = find_closest_index(timestamp, saccades[i]['time_middle'])
        
        x = rows['x'][k]
        y = rows['y'][k]
        
        L = 0.03
        orientation_start = numpy.radians(saccades[i]['orientation_start'])
        orientation_stop = numpy.radians(saccades[i]['orientation_stop'])
        
        x1 = x + L * numpy.cos(orientation_stop)
        y1 = y + L * numpy.sin(orientation_stop)
        x2 = x - L * numpy.cos(orientation_start)
        y2 = y - L * numpy.sin(orientation_start)
        
        pylab.plot([x, x1], [y, y1], 'r-')
        pylab.plot([x, x2], [y, y2], 'g-')
        pylab.plot(x, y, 'rx')
        
        pylab.text(x, y, "%d" % i)
        
         

def create_pictures(rows, saccades, outdir, basename):
    ''' Returns a list of the images created. '''
    fignames = []
    x = rows['x']
    y = rows['y']
    #vx = rows['xvel']
    #vy = rows['yvel'] 
    T = rows['timestamp'] 
    T = T - T[0]
    
    fignames.append(basename + '-xy.png')
    pylab.figure()
    pylab.plot(x, y, 'k-')
    pylab.axis('equal')
    pylab.title('x,y') 
    plot_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()
    
    candidates, = numpy.nonzero(rows['candidate'])
    
    fignames.append(basename + '-candidates.png')
    pylab.figure()
    pylab.plot(x, y, 'b.')
    pylab.plot(x[candidates], y[candidates], 'rx')
    pylab.axis('equal')
    pylab.title('x,y candidates') 
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()
    
    fignames.append(basename + '-velocity_modulus.png')
    pylab.figure()
    pylab.plot(T, rows['linear_velocity_modulus_smooth'], 'g-')
    pylab.plot(T, rows['linear_velocity_modulus'], '.')
    pylab.title('velocity modulus')
    mark_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()

    fignames.append(basename + '-acceleration_modulus.png')
    pylab.figure()
    pylab.plot(T, rows['linear_acceleration_modulus_smooth'], 'g-')
    pylab.plot(T, rows['linear_acceleration_modulus'], '.')
    pylab.title('acceleration modulus')
    mark_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()


    fignames.append(basename + '-angular_velocity_modulus.png')
    pylab.figure()
    pylab.plot(T, numpy.degrees(rows['angular_velocity_modulus']), '.')
    pylab.title('angular velocity modulus')
    pylab.ylabel('deg/s')
    mark_saccades(rows, saccades)
    a = pylab.axis()
    pylab.axis([a[0], a[1], 0, 6000])
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()


    fignames.append(basename + '-amplitude.png')
    pylab.figure()
    pylab.plot(T, numpy.degrees(rows['amplitude']), '.')
    pylab.title('amplitude (deg)')
    mark_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()

    fignames.append(basename + '-before_dispersion.png')
    pylab.figure()
    pylab.plot(T, numpy.degrees(rows['before_dispersion']), '.')
    pylab.title('before_dispersion (deg)')
    mark_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()

    fignames.append(basename + '-after_dispersion.png')
    pylab.figure()
    pylab.plot(T, numpy.degrees(rows['after_dispersion']), '.')
    pylab.title('after_dispersion (deg)')
    mark_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()

    fignames.append(basename + '-preference.png')
    pylab.figure()
    pylab.plot(T, rows['preference'], '.')
    pylab.title('preference ')
    mark_saccades(rows, saccades)
    a = pylab.axis()
    pylab.axis([a[0], a[1], 0, a[3]])
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()

    fignames.append(basename + '-marked_as_used.png')
    pylab.figure()
    pylab.plot(T, rows['marked_as_used'], 'rx')
    pylab.axis([T[0], T[-1], -0.1, 1.1])
    pylab.title('marked_as_used')
    mark_saccades(rows, saccades)
    pylab.savefig(os.path.join(outdir, fignames[-1]))
    pylab.close()


    return fignames


def write_debug_output(output_dir, sample_name, all_data, saccades):
    max_length_picture = 3.0
    
    output_index = os.path.join(output_dir, 'index.html')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir) 
    
    f = open(output_index, 'w')
    f.write('''
<html>
<head>
<title>%s</title>
<style type='text/css'>
.logpic { display: block; }
img { width: 40%%; }
</style> 
</head>
<body>
''' % sample_name)

    dt = 1.0 / 60
    max_rows_per_picture = max_length_picture / dt
    
    # iterate over each obj_id
    obj_ids = all_data['obj_id']
    for obj_id in  numpy.unique(obj_ids):
        indices_for_obj_id, = numpy.nonzero(obj_ids == obj_id) 
        rows = all_data[indices_for_obj_id]
        
        num_pictures = int(math. ceil(len(rows) / max_rows_per_picture))
        for i in range(num_pictures):
            from_index = max_rows_per_picture * i
            to_index = min(len(rows), from_index + max_rows_per_picture)
            
            rows_for_this_picture = rows[from_index:to_index]

            write_saccade_info_table(f, saccades,
                         t0=rows_for_this_picture[0]['timestamp'],
                         t1=rows_for_this_picture[-1]['timestamp'])

            
            basename = 'objid%s-%s-%s' % (obj_id, from_index, to_index)             
            pictures = create_pictures(rows_for_this_picture, saccades,
                                       output_dir, basename)
    
            f.write('''<div class='logpic'> ''')
            
            for picture in pictures:
                f.write("<img src='%s'/>" % picture)
                        
    
            f.write('</div>')

    f.write('''
</body>
''')


def write_saccade_info_table(f, saccades, t0, t1):
    f.write('''
    <table>
        <tr style='font-size: 60%'>
            <th>Index</th>
            <th>Interval (s)</th>
            <th>Amplitude (deg)</th>
            <th>Duration (s)</th>
            <th>Angular velocity (deg/s)</th>
            <th>Sign</th>
            <th>Linear velocity  (m/s)</th>
            <th>Linear acceleration  (m/s^2)</th>
            <th>Orientation (before -> after)</th>
            <th>Samples used (before, after)</th>
            <th>sd</th>
        </tr>
    
    ''')
    for i in range(len(saccades)):
        if not (t0 <= saccades[i]['time_middle'] <= t1):
            continue

        f.write("<tr style='font-size: 60%'>\n")
        f.write(' <td>%s</td>\n' % i) 
        f.write(' <td>%.2f</td>\n' % saccades[i]['time_passed'])
        f.write(' <td>%.1f</td>\n' % saccades[i]['amplitude'])
        f.write(' <td>%.2f</td>\n' % saccades[i]['duration'])
        f.write(' <td>%.3f</td>\n' % saccades[i]['top_velocity'])
        f.write(' <td>%d</td>\n' % saccades[i]['sign'])
        f.write(' <td>%.2f</td>\n' % saccades[i]['linear_velocity_modulus'])
        f.write(' <td>%.2f</td>\n' % saccades[i]['linear_acceleration_modulus'])
        f.write(' <td>%d, %d</td>\n' % (saccades[i]['orientation_start'],
                                    saccades[i]['orientation_stop']))
        f.write(' <td>%d,%d</td>\n' % (
                saccades[i]['num_samples_used_before'],
                saccades[i]['num_samples_used_after'])) 
        f.write(' <td>%.1f</td>\n' % saccades[i]['smooth_displacement'])
        f.write('</tr>\n')
    f.write('''
    </table>
    ''')
