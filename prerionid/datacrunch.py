import os
import toml
import threading
from queue import Queue
from time import sleep
from loguru import logger
import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import argparse
import matplotlib.pyplot as plt
from iqtools import *

lock = threading.Lock()
font = {#'family' : 'normal',
            'weight' : 'bold',
            'size'   : 5}

plt.rc('font', **font)

class Watcher:
    def __init__(self, directory, queue):
        self.observer = Observer()
        self.directory = directory
        self.queue = queue

    def run(self):
        event_handler = Handler(self.queue)
        self.observer.schedule(event_handler, self.directory, recursive=False)
        self.observer.start()
        try:
            while True:
                logger.info("Waiting for new files... Stop otherwise.")
                sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Observer stopped")
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.tiq'):
            logger.info(f"New file detected: {event.src_path}")
            self.queue.put(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.tiq'):
            logger.info(f"File modified: {event.src_path}")
            self.queue.put(event.src_path)


def load_config_file(configfile):
    logger.info(f"Configuration file has been provided: {configfile}")
    try:
        # Load calibration file
        config_dic = toml.load(configfile)
        #print(config_dic)
        for key in ['folder_path', 'tracking_file_path', 'output_path', 'www_path']:
            assert key in config_dic['paths'].keys()
        for key in ['lframes', 'nframes', 'n_avg', 'num_threads', 'zoom_center']:
            assert key in config_dic['settings'].keys()
            
    except:
        logger.error('Config file does not have required format.')
        exit()
       
    logger.success("Config file is good.")
    return config_dic

def plot_spectrogram_2(xx, yy, zz, cen=0.0, cmap=cm.jet, dpi=150, dbm=False, filename=None, title='Spectrogram', zzmin=0, zzmax=1e6, mask=False, span=None, decimal_place=2):

    fig, ax = plt.subplots()

    if zzmin >= 0 and zzmax <= 1e6 and zzmin < zzmax:
        zz = zz / np.max(zz) * 1e6
        mynorm = Normalize(vmin=zzmin, vmax=zzmax)

        # mask arrays for transparency in pcolormesh
        if mask:
            zz = np.ma.masked_less_equal(zz, zzmin)

    else:
        # pcolormesh ignores if norm is None
        mynorm = None

    if dbm:
        zz = IQBase.get_dbm(zz)

    # here comes span in [Hz]
    if not span:
        spanmask = (xx[0, :] != 0) | (xx[0, :] == 0)
    else:
        spanmask = (xx[0, :] <= span / 2) & (xx[0, :] >= -span / 2)
    xx = xx[:, spanmask]
    zz = zz[:, spanmask]
    # we have to check yy before, make sure it is sparse or not
    yy = yy[:,spanmask] if np.shape(yy)[1] > 1 else yy
    
    # here comes the plot
    sp = plt.pcolormesh(xx, yy, zz, cmap=cmap, norm=mynorm, shading='auto')
    
    # here is the color bar
    cb = plt.colorbar(sp, format=f'%.{decimal_place}e')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FormatStrFormatter(f'%.{decimal_place}e'))

    delta_f = np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0]))
    delta_t = np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0]))

    plt.xlabel(
        "Delta f [Hz] @ {} (resolution = {})".format(get_eng_notation(cen, unit='Hz', decimal_place=decimal_place), get_eng_notation(delta_f, unit='Hz', decimal_place=decimal_place)))
    plt.ylabel('Time [sec] (resolution = {})'.format(
        get_eng_notation(delta_t, 's', decimal_place=decimal_place)))
    plt.title(title)

    if dbm:
        cb.set_label('Power Spectral Density a.u. [dBm/Hz]')
    else:
        cb.set_label('Power Spectral Density a.u.')

    if filename is not None:
        plt.savefig(filename + '.png', dpi=dpi, bbox_inches='tight')
        plt.close()

def plot_and_save_spectrogram(xx,yy,zz, filename, span = None):
    
    fig, ax = plt.subplots()
    if not span:
        spanmask = (xx[0, :] != 0) | (xx[0, :] == 0)
    else:
        spanmask = (xx[0, :] <= span / 2) & (xx[0, :] >= -span / 2)
    xx = xx[:, spanmask]
    zz = zz[:, spanmask]
    # we have to check yy before, make sure it is sparse or not
    yy = yy[:,spanmask] if np.shape(yy)[1] > 1 else yy

    # Plot the spectrogram in the center
    ax.imshow(zz[:,:][::-1], extent=[xx[0,0]*1e-6,xx[0,-1]*1e-6,yy[0,0],yy[-1,0]], cmap='jet', aspect='auto')
    delta_f = np.round(np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0])),3)
    delta_t = np.round(np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0])),3)*1e3
    ax.set_xlabel(f' f [MHz] ({delta_f} Hz)')
    ax.set_ylabel(f'T [s] ({delta_t} ms)')
    plt.title(filename)
    plt.savefig(filename+'.png', dpi=150)
    plt.close()

def average_spectrogram(xx,yy,zz, n_avg):
    return get_averaged_spectrogram(xx, yy, zz, every = n_avg)

def load_processed_files(tracking_file_path):
    """ Load the list of processed files from a TOML file. If not found, create an empty set. """
    with lock:
        try:
            with open(tracking_file_path, 'r') as file:
                data = toml.load(file)
                return set(data.get('processed', []))
        except FileNotFoundError:
            return set()

def save_processed_files(processed, tracking_file_path):
    """ Save the list of processed files to a TOML file with thread safety. """
    with lock:
        with open(tracking_file_path, 'w') as file:
            toml.dump({"processed": list(processed)}, file)

def process_file(file_path, output_path, lframes, nframes, n_avg, zoom_center, www_path = ''):
    """ Simulate file processing. """
    logger.info(f"Processing {file_path}...")
    file_name = file_path.split('/')[-1]
    RSA_name = file_path.split('/')[-2]
    saved_name = output_path + file_name
    try:
        iq = get_iq_object(file_path)
        iq.read(nframes = nframes, lframes = lframes)

        xx, yy, zz = iq.get_power_spectrogram(nframes = nframes, lframes = lframes, sparse = True)
        logger.info('Plotting into a png file...')
        plot_and_save_spectrogram(xx, yy, zz, saved_name)
        #plot_spectrogram_2(xx, yy, zz, filename=saved_name, cen=iq.center, title=saved_name)
        logger.info('Creating a NPZ file...')
        np.savez(saved_name, arr_0 = xx + iq.center, arr_1 = yy, arr_2 = zz)

        axx, ayy, azz = average_spectrogram(xx,yy,zz, n_avg)
        logger.info('Save averaged spectrogram into png file...')
        plot_and_save_spectrogram(axx, ayy, azz, saved_name +'_zoom', span = 1000000)
        #plot_spectrogram_2(axx, ayy, azz, filename=saved_name+'_zoom', cen=iq.center+zoom_center, title=saved_name, span = 1000000)

        if www_path:
            logger.info(f'Copy files related to {file_path} to {www_path}...')
            shutil.copy(file_path, output_path)
            shutil.copy(saved_name+'.png', www_path + RSA_name + '.png')
            shutil.copy(saved_name+'_zoom.png', www_path + 'zoom_' + RSA_name + '.png')
            logger.info(f'Files  related to {file_path} to {www_path}...')
    except ValueError as e:
        logger.error(f"Error processing file {file_path}: {e}")
        # Handle specific errors e.g., retrying or moving file to error directory
    except Exception as e:
        logger.error(f"Unhandled exception for file {file_path}: {e}")

def worker(task_queue, processed_files, tracking_file_path, lframes, nframes, output_path,  n_avg, zoom_center, www_path):
    """ Thread worker function to process files from a queue if not already processed. """
    while True:
        file_path = task_queue.get()
        if file_path is None:
            task_queue.task_done()
            break  # None is the signal to stop
        
        #if file_path not in processed_files:
        process_file(file_path, output_path, lframes, nframes, n_avg, zoom_center, www_path)
        processed_files.add(file_path)
        save_processed_files(processed_files, tracking_file_path)
        task_queue.task_done()

def file_needs_processing(file_path, output_path, processed_files):
    # Define when a file needs to be reprocessed
    file_name = file_path.split('/')[-1]
    npz_file = f"{output_path}+{file_name}.npz"
    return not os.path.exists(npz_file) or file_path not in processed_files

def load_existing_files(directory, queue, processed_files):
    """ Load existing files into the queue at startup. """
    for filename in os.listdir(directory):
        if filename.endswith('.tiq'):
            file_path = os.path.join(directory, filename)
            if file_path not in processed_files:
                logger.info(f"Loading existing file: {filename}")
                queue.put(file_path)

def main(folder_path, tracking_file_path, num_threads, nframes, lframes, output_path,  n_avg, zoom_center,www_path):
    processed_files = load_processed_files(tracking_file_path)
    task_queue = Queue()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(task_queue, processed_files, tracking_file_path, lframes, nframes, output_path,  n_avg, zoom_center, www_path))
        thread.start()
        threads.append(thread)

    load_existing_files(folder_path, task_queue, processed_files)

    watcher = Watcher(folder_path, task_queue)
    watcher.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process files in a folder with a fixed number of threads.')
    parser.add_argument('--folder_path', type=str,  help='Path to the folder containing files to analyze')
    parser.add_argument('--tracking_file_path', type=str, help='Path to the TOML file tracking processed files')
    parser.add_argument('--output_path', type=str, help='Path to the folder with outputs')
    parser.add_argument('--www_path', type=str, help='Path to the WWW')

    parser.add_argument('--num_threads', type=int, default=10, help='Number of threads to use for processing files')
    parser.add_argument('--lframes', type=int, default=65536, help='Number of lframes')
    parser.add_argument('--nframes', type=int, default=94, help='Number of nframes')
    parser.add_argument('--n_avg', type=int, default=1, help='Average every n_avg frames')
    parser.add_argument('--zoom_center', type=float, default=0, help='Average every n_avg frames')


    parser.add_argument(
        "--config",
        nargs=1,
        type=str,
        default=None,
        help="Path and name of the TOML config file.",
    )

    args = parser.parse_args()


    if args.config:
        # Load configurations from a TOML file
        config_dic = load_config_file(args.config)

        args.lframes = config_dic['settings']['lframes']
        args.nframes = config_dic['settings']['nframes']
        args.num_threads = config_dic['settings']['num_threads']
        args.n_avg = config_dic['settings']['n_avg'] #handle it
        args.zoom_center = config_dic['settings']['zoom_center']

        args.folder_path = config_dic['paths']['folder_path']
        args.tracking_file_path = config_dic['paths']['tracking_file_path']
        args.output_path = config_dic['paths']['output_path']
        args.www_path = config_dic['paths']['www_path']

    main(args.folder_path, args.tracking_file_path, args.num_threads, args.nframes, args.lframes, args.output_path,  args.n_avg, args.zoom_center, args.www_path)
