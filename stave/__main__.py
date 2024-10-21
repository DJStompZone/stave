import ffmpeg
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from tqdm import tqdm
import logging
from mutagen import File
import redis
import time
import argparse


def redis_connection(host, port, db):
    try:
        return redis.Redis(host=host, port=port, db=db)
    except redis.ConnectionError as e:
        log_error(f"Failed to connect to Redis: {str(e)}")
        return None

def parse_arguments():
    parser = argparse.ArgumentParser(description="ShadowTEAM Automated Video Encoder")
    
    parser.add_argument("-w", "--watch-dir", required=True, help="Directory to watch for new video files")
    parser.add_argument("-u", "--update-frequency", type=int, default=5, help="Update frequency for progress (seconds)")
    parser.add_argument("-n", "--no-squash", action="store_true", help="Skip existing encoded files")
    parser.add_argument("-o", "--output-dir", required=True, help="Directory to save encoded video files")
    parser.add_argument("-r", "--redis-host", default="localhost", help="Redis server host")
    parser.add_argument("-p", "--redis-port", type=int, default=6379, help="Redis server port")
    parser.add_argument("-d", "--redis-db", type=int, default=0, help="Redis database index")
    
    return parser.parse_args()

def enqueue_video(file_path):
    r.lpush('video_queue', file_path)

def dequeue_video():
    return r.rpop('video_queue')

def get_queue_length():
    return r.llen('video_queue')

def set_current_task(file_path):
    r.set('current_task', file_path)

def get_current_task():
    return r.get('current_task')

def clear_current_task():
    r.delete('current_task')

def encode_video(input_file, output_dir, no_squash):
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '_encoded.mkv')
    
    if no_squash and os.path.exists(output_file):
        print(f"Skipping encoding of {input_file}, output already exists.")
        return
    
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, vcodec='hevc_nvenc', preset='slow', qp=0, acodec='libopus', audio_bitrate='192k')
            .run()
        )
        print(f"Encoded: {input_file} -> {output_file}")
        
        copy_metadata(input_file, output_file)
        
    except Exception as e:
        log_error(f"Failed to encode {input_file}: {str(e)}")

def copy_metadata(source, destination):
    src_file = File(source)
    dst_file = File(destination)
    dst_file.tags = src_file.tags
    dst_file.save()

logging.basicConfig(filename='video_encoder.log', level=logging.INFO)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def show_real_time_feedback(update_frequency):
    while True:
        queue_length = get_queue_length()
        current_task = get_current_task()
        with tqdm(total=queue_length + (1 if current_task else 0), unit='file') as pbar:
            if current_task:
                pbar.set_description(f"Currently encoding: {current_task.decode()}")
                pbar.update(1)
            else:
                pbar.set_description("No encoding in progress.")

            pbar.set_postfix(queue_length=queue_length)
            pbar.refresh()

        time.sleep(update_frequency)  # Refresh based on the provided frequency

class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, queue_func):
        self.queue_func = queue_func

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.mp4', '.mkv', '.avi')):
            print(f"New file detected: {event.src_path}")
            self.queue_func(event.src_path)

def start_watchdoggo(directory, queue_func):
    event_handler = VideoFileHandler(queue_func)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print(f"Watching directory: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    args = parse_arguments()
    global r
    r = redis_connection(args.redis_host, args.redis_port, args.redis_db)

    watchdoggo_thread = threading.Thread(target=start_watchdoggo, args=(args.watch_dir, enqueue_video))
    watchdoggo_thread.daemon = True
    watchdoggo_thread.start()
    feedback_thread = threading.Thread(target=show_real_time_feedback, args=(args.update_frequency,))
    feedback_thread.daemon = True
    feedback_thread.start()

    while True:
        file_path = dequeue_video()
        if file_path:
            set_current_task(file_path)
            encode_video(file_path, args.output_dir, args.no_squash)
            clear_current_task()
        else:
            time.sleep(args.update_frequency)

if __name__ == "__main__":
    main()