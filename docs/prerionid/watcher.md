# Watcher Module

The `watcher.py` module provides functionality to monitor a directory for file system events such as file creation, deletion, modification, and movement. It uses the `watchdog` library to observe changes in real-time and logs these events using `loguru`.

## Classes

### `Watcher`

The `Watcher` class is responsible for setting up and running the directory monitoring process.

#### Constructor: `__init__(self, directory)`
Initializes the `Watcher` instance.

#### Parameters:
- `directory` (str): The directory to monitor.

#### Methods:

##### `run(self)`
Starts the directory monitoring process.

- Creates an instance of the `Handler` class to handle file system events.
- Schedules the observer to monitor the specified directory recursively.
- Starts the observer and logs events until interrupted by the user.

---

### `Handler`

The `Handler` class extends `FileSystemEventHandler` and defines methods to handle specific file system events.

#### Methods:

##### `on_created(self, event)`
Logs when a file is created.

##### `on_deleted(self, event)`
Logs when a file is deleted.

##### `on_modified(self, event)`
Logs when a file is modified.

##### `on_moved(self, event)`
Logs when a file is moved.

---

## Functions

### `count_files(file)`
Logs the addition of a file.

#### Parameters:
- `file` (str): The name of the file added.

---

### `main(directory)`
Starts the directory watcher.

#### Parameters:
- `directory` (str): The directory to monitor.

---

## Command-Line Interface

The `watcher.py` module can be executed as a standalone script to monitor a directory. It accepts the following command-line arguments:

### Arguments:
- `--directory` (str, required): The directory to monitor.
