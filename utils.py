import os.path


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
