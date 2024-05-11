import os
import toml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor

# Path to the folder containing files to analyze
folder_path = '/path/to/your/folder'

# Path to the TOML file tracking processed files
tracking_file_path = '/path/to/your/processed_files.toml'

def load_processed_files():
    """ Load the list of processed files from a TOML file. """
    try:
        with open(tracking_file_path, 'r') as file:
            data = toml.load(file)
            return set(data['processed'])
    except FileNotFoundError:
        return set()

def save_processed_files(processed):
    """ Save the list of processed files to a TOML file. """
    with open(tracking_file_path, 'w') as file:
        toml.dump({"processed": list(processed)}, file)

def process_file(file_path):
    """ Your file processing logic goes here. """
    print(f"Processing {file_path}...")

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, processed_files):
        self.processed_files = processed_files
        self.executor = ThreadPoolExecutor(max_workers=10)  # Setting up a ThreadPoolExecutor

    def on_created(self, event):
        """ Event is triggered when a file is created. """
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            if file_name not in self.processed_files:
                self.executor.submit(self.handle_new_file, file_path, file_name)

    def handle_new_file(self, file_path, file_name):
        """ Handles processing of new files in a separate thread. """
        process_file(file_path)
        self.processed_files.add(file_name)
        save_processed_files(self.processed_files)

def main():
    # Load the list of already processed files
    processed_files = load_processed_files()

    # Create an event handler
    event_handler = NewFileHandler(processed_files)

    # Set up a watchdog observer
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    try:
        while True:
            # Keep the script running
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()