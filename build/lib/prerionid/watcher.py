import os
from time import sleep
from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse

class Watcher:
    def __init__(self, directory):
        self.observer = Observer()
        self.directory = directory

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()
        try:
            while True:
                logger.info("Monitoring directory... Press Ctrl+C to stop.")
                sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Observer stopped")
        self.observer.join()

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            logger.info(f"File moved from {event.src_path} to {event.dest_path}")


def count_files(file):
    # Count all files in the directory
    logger.info(f"File added {file}")

def main(directory):
    logger.info("Starting directory watcher...")
    watcher = Watcher(directory)
    watcher.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor and count files in a directory.')
    parser.add_argument('--directory', type=str, required=True, help='Directory to monitor')
    args = parser.parse_args()

    main(args.directory)
