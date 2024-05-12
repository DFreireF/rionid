import os
import toml
import threading
from time import sleep

# Paths configuration
folder_path = '/path/to/your/folder'  # Change this to your folder path
tracking_file_path = '/path/to/your/processed_files.toml'
lock = threading.Lock()

def load_processed_files():
    """ Load the list of processed files from a TOML file. """
    try:
        with open(tracking_file_path, 'r') as file:
            data = toml.load(file)
            return set(data.get('processed', []))
    except FileNotFoundError:
        return set()

def save_processed_files(processed):
    """ Save the list of processed files to a TOML file with thread safety. """
    with lock:
        with open(tracking_file_path, 'w') as file:
            toml.dump({"processed": list(processed)}, file)

def process_file(file_path):
    """ Simulate file processing. """
    print(f"Processing {file_path}...")
    # Add your file processing logic here

def worker(file_path, processed_files):
    """ Thread worker function to process files if not already processed. """
    if file_path not in processed_files:
        process_file(file_path)
        with lock:
            processed_files.add(file_path)
            save_processed_files(processed_files)

def main():
    processed_files = load_processed_files()  # Load the list of already processed files
    
    while True:
        current_files = {f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))}
        threads = []
        for file_name in current_files:
            file_path = os.path.join(folder_path, file_name)
            if file_name not in processed_files:
                thread = threading.Thread(target=worker, args=(file_path, processed_files))
                thread.start()
                threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        print("Waiting for new files... Stop otherwise.")
        sleep(1)  # Check the folder every 1 second

if __name__ == "__main__":
    main()
