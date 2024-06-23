import os
import time
import shutil


def split_name(name):
    # Split the string into a list of words
    words = name.split()
    # The last name is the first word, and the first name is the second word
    last_name = words[0]
    first_names = ' '.join(words[1:])
    # Return the last name and first name as a tuple
    return (last_name, first_names)


def to_upper_camel_case(string):
    # Split the string into words
    words = string.split()
    # Capitalize the first letter of each word and join them together
    camel_case_string = ''.join(word.capitalize() for word in words)
    return camel_case_string


def is_file_size_stable(file_path, retries, sleep_time):
    last_size = -1
    for _ in range(retries):
        current_size = os.path.getsize(file_path)
        if current_size == last_size:
            return True
        last_size = current_size
        time.sleep(sleep_time)
    return False


def move_file_to_folder(folder_path, file_path_to_move):
    # Check if the new folder exists
    if not os.path.exists(folder_path):
        # If not, create it
        os.makedirs(folder_path)

    # Check if the file exists
    if os.path.exists(file_path_to_move):
        # If it does, move it to the new folder
        shutil.move(file_path_to_move, folder_path)
    else:
        print(f"The file {file_path_to_move}"
              " does not exist in the download path.")


def wait_for_download(directory, max_wait_time=10, sleep_time=0.2, size_check_retries=5):
    start_time = time.time()
    while True:
        files_in_directory = os.listdir(directory)
        if files_in_directory:
            try:
                latest_file = max(files_in_directory, key=lambda f: os.path.getctime(
                    os.path.join(directory, f)))
                file_path = os.path.join(directory, latest_file)

                if not os.path.isfile(file_path):
                    continue

                # Check if file size is stable
                if is_file_size_stable(file_path, size_check_retries, sleep_time):
                    return True, latest_file
            except FileNotFoundError:
                print("File not found. Skipping...")
                continue

        if time.time() - start_time > max_wait_time:
            print("Max wait time reached. Download not completed.")
            return False, None

        time.sleep(sleep_time)


def rename_file(directory, current_filename, new_filename):
    current_file_path = os.path.join(directory, current_filename)
    new_file_path = os.path.join(directory, new_filename)
    new_file_path_without_ext = os.path.splitext(new_file_path)[0]
    new_file_ext = os.path.splitext(new_file_path)[1]
    counter = 1

    while os.path.exists(new_file_path):
        new_file_path = f"{new_file_path_without_ext}_{counter}{new_file_ext}"
        counter += 1

    try:
        os.rename(current_file_path, new_file_path)
        return new_file_path
    except FileNotFoundError:
        print(f"File {current_filename} not found.")
        return ""
    except Exception as e:
        print(f"Error renaming file: {str(e)}")
        return ""
