import os
import toml
import threading
from queue import Queue
from time import sleep
from loguru import logger
import argparse
import matplotlib.pyplot as plt
from iqtools import *

lock = threading.Lock()
font = {#'family' : 'normal',
            'weight' : 'bold',
            'size'   : 5}

plt.rc('font', **font)

def plot_and_save_spectrogram(xx,yy,zz, filename):
    
    fig, ax = plt.subplots()    
    # Plot the spectrogram in the center
    ax.imshow(zz[:,:][::-1], extent=[xx[0,0]*1e-6,xx[0,-1]*1e-6,yy[0,0],yy[-1,0]], cmap='jet', aspect='auto')
    delta_f = np.round(np.abs(np.abs(xx[0, 1]) - np.abs(xx[0, 0])),3)
    delta_t = np.round(np.abs(np.abs(yy[1, 0]) - np.abs(yy[0, 0])),3)*1e3
    ax.set_xlabel(f' f [MHz] ({delta_f} Hz)')
    ax.set_ylabel(f'T [s] ({delta_t} ms)')
    plt.title(filename)
    plt.savefig(filename+'.png', dpi=150)
    plt.close()    
    
    

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

def process_file(file_path):
    """ Simulate file processing. """
    logger.info(f"Processing {file_path}...")
    iq = get_iq_object(file_path)
    lframes = 2**12
    nframes = 2**10
    iq.read(nframes = nframes, lframes = lframes)
    
    xx, yy, zz = iq.get_power_spectrogram(nframes = nframes, lframes = lframes, sparse = True)
    logger.info('Plotting into a png file...')
    plot_and_save_spectrogram(xx, yy, zz, file_path)
    logger.info('Creating a NPZ file...')
    np.savez(f'{file_path}_p', arr_0 = xx + iq.center, arr_1 = yy, arr_2 = zz)


def worker(task_queue, processed_files, tracking_file_path):
    """ Thread worker function to process files from a queue if not already processed. """
    while True:
        file_path = task_queue.get()
        if file_path is None:
            task_queue.task_done()
            break  # None is the signal to stop
        
        if file_path not in processed_files:
            process_file(file_path)
            processed_files.add(file_path)
            save_processed_files(processed_files, tracking_file_path)
            task_queue.task_done()

def file_needs_processing(file_path, processed_files):
    # Define when a file needs to be reprocessed
    npz_file = f"{file_path}_p.npz"
    return not os.path.exists(npz_file) or file_path not in processed_files

def main(folder_path, tracking_file_path, num_threads):
    processed_files = load_processed_files(tracking_file_path)  # Load or create the list of processed files
    task_queue = Queue()

    # Start worker threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(task_queue, processed_files, tracking_file_path))
        thread.start()
        threads.append(thread)

    try:
        while True:
            current_files = {os.path.join(folder_path, f) for f in os.listdir(folder_path)
                             if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.tiq')}
            new_files = {f for f in current_files if file_needs_processing(f, processed_files)}
            for file_path in new_files:
                with lock:
                    #if file_path not in processed_files:  # Double-check pattern to reduce lock contention
                    task_queue.put(file_path)

            print("Waiting for new files... Stop otherwise.")
            sleep(1)  # Check the folder every 1 second
    except KeyboardInterrupt:
        print("Shutdown signal received. Stopping threads.")
        # Signal threads to stop
        for _ in range(num_threads):
            task_queue.put(None)
    finally:
        # Stop workers
        for thread in threads:
            thread.join()
        print("All threads have been stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process files in a folder with a fixed number of threads.')
    parser.add_argument('--folder_path', type=str, required=True, help='Path to the folder containing files to analyze')
    parser.add_argument('--tracking_file_path', type=str, required=True, help='Path to the TOML file tracking processed files')
    parser.add_argument('--num_threads', type=int, default=10, help='Number of threads to use for processing files')

    args = parser.parse_args()

    main(args.folder_path, args.tracking_file_path, args.num_threads)
