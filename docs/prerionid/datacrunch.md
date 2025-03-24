# DataCrunch Module

The `datacrunch.py` module provides a multithreaded system for processing `.tiq` files in a directory. It monitors the directory for new or modified files, processes them to generate spectrograms, and saves the results in various formats. The module also tracks processed files to avoid redundant processing.

## Classes

### `Watcher`

The `Watcher` class monitors a directory for new or modified `.tiq` files and adds them to a processing queue.

#### Constructor: `__init__(self, directory, queue)`
Initializes the `Watcher` instance.

#### Parameters:
- `directory` (str): Path to the directory to monitor.
- `queue` (Queue): Queue to store files for processing.

#### Methods:
- `run(self)`: Starts the directory monitoring process using `watchdog`.

---

### `Handler`

The `Handler` class extends `FileSystemEventHandler` to handle file system events.

#### Constructor: `__init__(self, queue)`
Initializes the `Handler` instance.

#### Parameters:
- `queue` (Queue): Queue to store files for processing.

#### Methods:
- `on_created(self, event)`: Adds newly created `.tiq` files to the queue.
- `on_modified(self, event)`: Adds modified `.tiq` files to the queue.

---

## Functions

### File Processing

#### `process_file(file_path, output_path, lframes, nframes, n_avg, zoom_center, www_path='')`
Processes a single `.tiq` file to generate spectrograms and save results.

#### Parameters:
- `file_path` (str): Path to the `.tiq` file.
- `output_path` (str): Directory to save processed files.
- `lframes` (int): Length of each frame.
- `nframes` (int): Number of frames to process.
- `n_avg` (int): Number of frames to average.
- `zoom_center` (float): Center frequency for zoomed spectrograms.
- `www_path` (str, optional): Directory to copy files for web access.

---

#### `worker(task_queue, processed_files, tracking_file_path, lframes, nframes, output_path, n_avg, zoom_center, www_path)`
Processes files from the queue in a separate thread.

#### Parameters:
- `task_queue` (Queue): Queue containing files to process.
- `processed_files` (set): Set of already processed files.
- `tracking_file_path` (str): Path to the TOML file tracking processed files.
- `lframes` (int): Length of each frame.
- `nframes` (int): Number of frames to process.
- `output_path` (str): Directory to save processed files.
- `n_avg` (int): Number of frames to average.
- `zoom_center` (float): Center frequency for zoomed spectrograms.
- `www_path` (str): Directory to copy files for web access.

---

### File Tracking

#### `load_processed_files(tracking_file_path)`
Loads the list of processed files from a TOML file.

#### Parameters:
- `tracking_file_path` (str): Path to the TOML file.

#### Returns:
- `set`: Set of processed files.

---

#### `save_processed_files(processed, tracking_file_path)`
Saves the list of processed files to a TOML file.

#### Parameters:
- `processed` (set): Set of processed files.
- `tracking_file_path` (str): Path to the TOML file.

---

### Spectrogram Plotting

#### `plot_and_save_spectrogram(xx, yy, zz, filename, span=None)`
Generates and saves a spectrogram plot.

#### Parameters:
- `xx` (array): Frequency data.
- `yy` (array): Time data.
- `zz` (array): Power data.
- `filename` (str): Name of the output file.
- `span` (float, optional): Frequency span for zoomed plots.

---

#### `average_spectrogram(xx, yy, zz, n_avg)`
Averages the spectrogram data over a specified number of frames.

#### Parameters:
- `xx` (array): Frequency data.
- `yy` (array): Time data.
- `zz` (array): Power data.
- `n_avg` (int): Number of frames to average.

#### Returns:
- Averaged spectrogram data.

---

### Configuration

#### `load_config_file(configfile)`
Loads and validates a TOML configuration file.

#### Parameters:
- `configfile` (str): Path to the TOML configuration file.

#### Returns:
- `dict`: Configuration dictionary.

---

### Main Workflow

#### `main(folder_path, tracking_file_path, num_threads, nframes, lframes, output_path, n_avg, zoom_center, www_path)`
Main function to initialize and run the file processing workflow.

#### Parameters:
- `folder_path` (str): Directory to monitor for `.tiq` files.
- `tracking_file_path` (str): Path to the TOML file tracking processed files.
- `num_threads` (int): Number of threads for processing files.
- `nframes` (int): Number of frames to process.
- `lframes` (int): Length of each frame.
- `output_path` (str): Directory to save processed files.
- `n_avg` (int): Number of frames to average.
- `zoom_center` (float): Center frequency for zoomed spectrograms.
- `www_path` (str): Directory to copy files for web access.

---

## Command-Line Interface

The `datacrunch.py` module can be executed as a standalone script. It accepts the following command-line arguments:

### Arguments:
- `--folder_path` (str): Path to the folder containing `.tiq` files.
- `--tracking_file_path` (str): Path to the TOML file tracking processed files.
- `--output_path` (str): Directory to save processed files.
- `--www_path` (str): Directory to copy files for web access.
- `--num_threads` (int): Number of threads to use for processing files.
- `--lframes` (int): Length of each frame.
- `--nframes` (int): Number of frames to process.
- `--n_avg` (int): Number of frames to average.
- `--zoom_center` (float): Center frequency for zoomed spectrograms.
- `--config` (str): Path to the TOML configuration file.

### Example Usage:
```bash
python [datacrunch.py](http://_vscodecontentref_/3) --config config.toml