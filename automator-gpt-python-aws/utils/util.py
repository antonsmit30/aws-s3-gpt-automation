from functools import wraps
import time

def log_full_message(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # loop through attributes. if attribute is a class object print out each attribute of that object
        for arg in args:
            if hasattr(arg, "__dict__"):
                for key, value in arg.__dict__.items():
                    if key == "_full_message":
                        print(f"full message debug: {value}")
        print(f"kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper


def log_all_attributes(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # log all args
        for arg in args:
            if hasattr(arg, "__dict__"):
                for key, value in arg.__dict__.items():
                    # if type of value is list, loop through each list item and print individually
                    if type(value) == list:
                        for item in value:
                            print(f"value: {item}")
                    else:
                        print(f"key: {key}, value: {value}")
        return func(*args, **kwargs)
    return wrapper


def enable_audio_wrap(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if hasattr(arg, "__dict__"):
                for key, value in arg.__dict__.items():
                    if key == "_enable_audio":
                        arg.__dict__['_enable_audio'] = True
        return func(*args, **kwargs)
    return wrapper

def run_on_schedule(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            func(*args, **kwargs)
            time.sleep(30)
    return wrapper

def temp_dir_appender(func):
    """Temporarily appends a directory to file create and directory create functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            print(f"temp appender: k {arg}")
            if hasattr(arg, "__dict__"):
                for key, value in arg.__dict__.items():
                    print(f"temp appender: k {key} v: {value} ")
                    if key == "file_path":
                        arg.__dict__["file_path"] = f"./data/{value}"
                    elif key == "directory_path":
                        arg.__dict__["directory_path"] = f"./data/{value}"
        return func(*args, **kwargs)
    return wrapper