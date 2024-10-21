
# STAVE - ShadowTEAM Automated Video Encoder
![17295527154668899318283088850355](https://github.com/user-attachments/assets/5773bd10-ece6-4983-a7dd-79bd14143e2b)

**STAVE** is a lightweight, automated video encoding tool designed to handle incoming video files, encode them using **FFmpeg** with **H.265 (NVENC)** for GPU acceleration and **Opus** for audio, and organize the output efficiently. STAVE monitors directories for new video files, processes them in a reliable queue, and provides real-time feedback on progress and queue status.

## Features
- **Automatic Video Encoding**: Detects new files and encodes them automatically.
- **GPU Accelerated**: Leverages NVIDIA NVENC for H.265 encoding.
- **Opus Audio**: Efficient Opus codec for high-quality audio at reduced file sizes.
- **Queue Management**: Persistent task queue using Redis to manage multiple video encoding tasks.
- **Real-Time Feedback**: Shows current encoding status, queue length, and task progress using `tqdm`.
- **Metadata Preservation**: Transfers metadata from the source file to the encoded file using `mutagen`.
- **Configurable**: Flexible options to configure directories, update frequency, and more.

## Installation

STAVE can be installed in two ways:

### 1. Install directly from GitHub:
```bash
pip install git+https://github.com/djstompzone/stave
```

## Usage

Once installed, STAVE can be run as a command-line tool using Python's module interface.

```bash
python -m stave -w /path/to/watch/folder -u 5 -n -o /path/to/output/folder -r localhost -p 6379 -d 0
```

### Command-line Options:
| Option                   | Description                                                                           |
|---------------------------|---------------------------------------------------------------------------------------|
| `-w, --watch-dir`          | Directory to watch for new video files (required).                                    |
| `-u, --update-frequency`   | Time (in seconds) between progress updates (default: 5 seconds).                      |
| `-n, --no-squash`          | Skip encoding if the output file already exists.                                      |
| `-o, --output-dir`         | Directory to save the encoded files (required).                                       |
| `-r, --redis-host`         | Hostname or IP address of the Redis server (default: localhost).                      |
| `-p, --redis-port`         | Port number of the Redis server (default: 6379).                                      |
| `-d, --redis-db`           | Redis database index (default: 0).                                                    |

## Example

Watch a directory for new `.mp4`, `.mkv`, and `.avi` files, encode them using **H.265 (NVENC)**, and save the output to the specified directory:

```bash
python -m stave -w /home/user/videos -u 5 -n -o /home/user/encoded -r localhost -p 6379 -d 0
```

### Key Features in Action:
- **Skip Encoding**: If the output file already exists, the `--no-squash` flag will skip re-encoding that file.
- **Real-Time Feedback**: The encoding process is monitored and updated in real-time with progress bars and queue length.
- **Persistent Queue**: The Redis queue ensures that even in case of failure, tasks will be retained and processed when possible.

## Requirements

- **Python 3.10+**
- **FFmpeg** (with NVIDIA NVENC support recommended)
- **Redis** server
- **NVIDIA GPU** for hardware acceleration (optional but recommended)

## Installation of FFmpeg with NVENC (Optional)

For STAVE to take full advantage of GPU acceleration, ensure you have **FFmpeg** installed with **NVIDIA NVENC** support.

- On Linux, you can compile FFmpeg with NVENC:
```bash
sudo apt-get install nvidia-cuda-toolkit
sudo apt-get install ffmpeg
```

- On Windows
```
Write-Host Yeah good luck with that one m8
```

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Contributing
We welcome contributions to improve STAVE! Feel free to submit a pull request or open an issue.

## Author
STAVE is developed and maintained by [DJ Stomp](https://discord.stomp.zone) in collaboration with ShadowTEAM.
