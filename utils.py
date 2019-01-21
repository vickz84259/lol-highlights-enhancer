import os.path
import re


def get_filename(file_path, with_extension=False):
    """Extracts the filename from the file path given

    Args:
        file_path (string): a path to a certain file
        with_extension (bool, optional): Defaults to False. Determines if the
            filename returned should include it's extension

    Returns:
        A string representing the filename without the leading parts of the
        path.
    """
    basename = os.path.basename(file_path)

    if with_extension:
        filename = basename
    else:
        filename = os.path.splitext(basename)[0]

    return filename


def get_match_details(string):
    regex = re.match(r'(\d+)-(\d+)_(\w{2,3}\d?)-(\d+)_\d{2}', string)

    result = {
        'patch_major': regex.group(1),
        'patch_minor': regex.group(2),
        'region': regex.group(3),
        'match_id': regex.group(4)
    }

    return result


def is_highlight(file_name):
    result = False

    if re.match(r'^\d+-\d+_(\w{2,3}\d?)-(\d+)_\d{2}\.webm$', file_name):
        result = True

    return result
