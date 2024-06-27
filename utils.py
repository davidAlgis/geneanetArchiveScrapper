import os
import time
import shutil
import re
from datetime import datetime


def date_to_string(date):
    if isinstance(date, datetime):
        if date.day == 1 and date.month == 1:
            return date.strftime("%Y")
        elif date.day == 1:
            return date.strftime("%m-%Y")
        else:
            return date.strftime("%d-%m-%Y")
    else:
        raise ValueError("Input is not a datetime object")


def parse_date(date_str):
    if (date_str is None):
        return None
    if isinstance(date_str, datetime):
        return date_str  # Return if already parsed
    try:
        if len(date_str) == 4:  # YYYY
            return datetime.strptime(date_str, "%Y")
        elif len(date_str) == 7:  # YYYY-MM
            return datetime.strptime(date_str, "%m-%Y")
        elif len(date_str) == 10:  # YYYY-MM-DD
            return datetime.strptime(date_str, "%d-%m-%Y")
        else:
            raise ValueError("Date format not recognized")
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None


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


def sanitize_path_component(component):
    """
    Removes invalid characters from the path component.
    """
    return re.sub(r'[\\/:*?"<>|]', '', component)


def sanitize_path(path):
    # Split the folder path into components
    components = path.split('\\')

    # Sanitize each component
    sanitized_components = [sanitize_path_component(
        component) for component in components]

    # Join the sanitized components back into a path
    sanitized_folder_path = '\\'.join(sanitized_components)
    return sanitized_folder_path


def move_file_to_folder(folder_path, file_path_to_move):
    sanitized_folder_path = sanitize_path(folder_path)

    # Check if the new folder exists
    if not os.path.exists(sanitized_folder_path):
        # If not, create it
        os.makedirs(sanitized_folder_path)

    # Check if the file exists
    if os.path.exists(file_path_to_move):
        # Split the file path into a directory and a file name
        file_directory, file_name = os.path.split(file_path_to_move)

        # Sanitize the file name
        sanitized_file_name = sanitize_path_component(file_name)

        # Define the destination file path
        destination_file_path = os.path.join(
            sanitized_folder_path, sanitized_file_name)

        try:
            # Copy the file to the new folder
            shutil.copy2(file_path_to_move, destination_file_path)
            # If the copy operation is successful, remove the original file
            os.remove(file_path_to_move)
        except Exception as e:
            print(f"An error occurred while moving the file: {e}")
    else:
        print(f"The file {file_path_to_move}"
              "does not exist in the download path.")


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
                print(f"\nDownload file in "
                      f"{directory} not found. Skipping...\n")
                continue

        if time.time() - start_time > max_wait_time:
            print(f"\nMax wait time reached. "
                  f"Download not completed in {directory}.\n")
            return False, None

        time.sleep(sleep_time)


def format_string_to_bullets(s):
    # Split the string into lines
    lines = s.strip().split('\n')

    # Initialize an empty list to hold the bullet points
    bullets = []

    # Iterate over each pair of lines
    for i in range(0, len(lines), 2):
        # Get the key and value
        key = lines[i]
        value = lines[i + 1] if i + 1 < len(lines) else ''

        # Add the bullet point to the list
        bullets.append(f'\t- {key} : {value}')

    # Join the bullet points into a single string and return it
    return '\n'.join(bullets)


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
