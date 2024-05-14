#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Process several files as given in the command line argument

2024 xaratustrah
2024 DFreireF
"""

import sys
import argparse
import datetime
import time
from loguru import logger
import shutil
import toml
from iqtools import *

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

def process_loop(syncfile, logfile, lustrepath, queue):
    try:
        with open(syncfile) as sf:
            for line in sf.readlines():
                basefilename = line.strip().split('/')[-1]
                source_fullfilename = os.path.join(lustrepath, basefilename)
                if not already_processed(source_fullfilename, logfile):
                    put_into_logfile(source_fullfilename, logfile)
                    queue.put((source_fullfilename, basefilename))
    except Exception as e:
        logger.error(f"No sync file list on the specified location. Aborting: {str(e)}")
        exit()

def process_each(
    source_fullfilename, basefilename, outpath, wwwpath, n_avg, lframes, nframes
):
    """
    what to do with each file
    """
    try:
        logger.info(f"Now processing {basefilename}")
        iq = get_iq_object(source_fullfilename)
        logger.info("Reading file...")
        iq.read(nframes=nframes, lframes=lframes)
        iq.method = "fftw"
        logger.info("Do FFT...")
        xx, yy, zz = iq.get_power_spectrogram(lframes=lframes, nframes=nframes, sparse=True)
        axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, every=n_avg)

        font = {"weight": "bold", "size": 5}  #'family' : 'normal',

        plt.rc("font", **font)

        logger.info("Write to PNG...")
        plot_and_save_spectrogram(xx, yy, zz, outpath + basefilename)
        plot_and_save_spectrogram(axx, ayy, azz, outpath + basefilename +'_zoom', span = 1000000)

        logger.info("Write to NPZ...")
        np.savez(outpath + basefilename + ".npz", xx + iq.center, yy, zz)

        logger.info("Copying files...")
        shutil.copy(source_fullfilename, outpath)
        shutil.copy(outpath + basefilename + ".png", wwwpath + basefilename[:5] + ".png")
        shutil.copy(
            outpath + basefilename + "_zoom.png",
            wwwpath + "zoom_" + basefilename[:5] + ".png",
        )
        logger.success(f"Done processing {basefilename}\n\n")

    except ValueError as e:
        logger.error(f"Error processing file {basefilename}: {e}")
    except Exception as e:
        logger.error(f"Unhandled exception for file {basefilename}: {e}")

def put_into_logfile(file, logfilename):
    """
    Write into the log file.
    """

    with open(logfilename, "a") as file_object:
        file_object.write(file + "\n")


def already_processed(currentfilename, logfilename):
    """
    check whether the file is already in the log file
    """

    already_processed = False
    try:
        with open(logfilename, "r") as file_object:
            loglist = file_object.readlines()

            for line in loglist:
                if currentfilename in line:
                    already_processed = True

    except OSError as e:
        logger.warning("Log file does not exist, creating a new one.")

    return already_processed


def worker(queue, outpath, wwwpath, n_avg, lframes, nframes):
    while True:
        item = queue.get()
        if item is None:  # Sentinel value to end the thread
            break
        source_fullfilename, basefilename = item
        process_each(source_fullfilename, basefilename, outpath, wwwpath, n_avg, lframes, nframes)
        queue.task_done()

def main():
    scriptname = "e018_looper"
    __version__ = "v0.0.1"

    default_logfilename = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + ".txt"

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        nargs=1,
        type=str,
        default=None,
        help="Path and name of the TOML config file.",
    )

    logger.remove(0)
    logger.add(sys.stdout, level="INFO")

    args = parser.parse_args()

    logger.info("{} {}".format(scriptname, __version__))

    # read config file
    config_dic = None
    if args.config:
        logger.info("Configuration file has been provided: " + args.config[0])
        try:
            # Load calibration file
            config_dic = toml.load(args.config[0])
            # check structure of calibration file
            print(config_dic)
            for key in ["syncfile", "logfile", "lustrepath", "outpath", "wwwpath"]:
                assert key in config_dic["paths"].keys()
            for key in ["n_avg", "sleeptime", "lframes", "nframes"]:
                assert key in config_dic["settings"].keys()

        except:
            logger.error("Config file does not have required format.")
            exit()

        logger.success("Config file is good.")

        lframes = config_dic["settings"]["lframes"]
        nframes = config_dic["settings"]["nframes"]
        n_avg = config_dic["settings"]["n_avg"]
        sleeptime = config_dic["settings"]["sleeptime"]

        syncfile = config_dic["paths"]["syncfile"]
        logfile = config_dic["paths"]["logfile"]
        lustrepath = config_dic["paths"]["lustrepath"]
        outpath = config_dic["paths"]["outpath"]
        wwwpath = config_dic["paths"]["wwwpath"]

    else:
        logger.error("No Config file provided. Aborting...")
        exit()

    logger.info("Processing files from sync file list: ", syncfile)
    logger.info("Log file: " + logfile)
    logger.info("Taking files from (lustrepath): " + lustrepath)
    logger.info("Writing files to (outpath): " + outpath)
    logger.info("Copy files to (wwwpath): " + wwwpath)

    wwwpath = os.path.join(wwwpath, "")
    outpath = os.path.join(outpath, "")
    lustrepath = os.path.join(lustrepath, "")

    logger.info("Let us see if there are new files...")

    number_of_threads = 10
    file_queue = Queue()

    # Start worker threads
    threads = []
    for _ in range(number_of_threads):
        t = threading.Thread(target=worker, args=(file_queue, outpath, wwwpath, n_avg, lframes, nframes))
        t.start()
        threads.append(t)

    # Process loop adjusted to enqueue files
    try:
        while True:
            process_loop(syncfile, logfile, lustrepath, file_queue)
            time.sleep(sleeptime)
            logger.info("I am waiting for new files...")
    except KeyboardInterrupt:
        logger.info("Stopping, please wait for current operations to finish...")

    # Stop all threads by putting sentinel values in the queue
    for _ in range(number_of_threads):
        file_queue.put(None)
    for t in threads:
        t.join()

    logger.success("All files processed and threads have been closed.")

if __name__ == "__main__":
    main()