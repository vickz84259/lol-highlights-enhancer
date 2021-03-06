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


def get_appropriate_size(bytes):
    kilobytes = bytes/1024
    megabytes = kilobytes/1024
    gigabyte = megabytes/1024

    sizes = {'KB': kilobytes, 'MB': megabytes, 'GB': gigabyte}
    for key, value in sizes.items():
        if value >= 0.1 and value < 1000:
            return f'{round(value, 2)} {key}'


def get_mode(game_mode, queue_id):
    modes = {'ODIN': 'Dominion/Crystal Scar', 'ARAM': 'ARAM', 'URF': 'URF',
             'DOOMBOTSTEEMO': 'Doom Bots', 'ONEFORALL': 'One for all',
             'ASCENSION': 'Ascension', 'FIRSTBLOOD': 'Snowdown Showdown',
             'KINGPORO': 'Legend of the Poro King', 'SIEGE': 'Nexus Siege',
             'ASSASSINATE': 'Blood Hunt Assassin', 'GAMEMODEX': 'Nexus Blitz',
             'ARSR': 'All Random Summoner\'s Rift',
             'DARKSTAR': 'Dark Star: Singularity',
             'PROJECT': 'PROJECT: Hunters', 'ODYSSEY': 'Odyssey: Extraction',
             'STARGUARDIAN': 'Star Guardian Invasion'}

    queue_ids = {'75': '6v6 Hexakill', '98': '6v6 Hexakill', '310': 'Nemesis',
                 '313': 'Black Market Brawlers', '325': 'All Random games',
                 '400': '5V5 Draft Pick', '420': '5v5 Ranked Solo',
                 '430': '5v5 Blind Pick', '440': '5v5 Ranked Flex',
                 '460': '3v3 Blind Pick', '470': '3v3 Ranked Flex',
                 '700': 'Clash', '900': 'ARURF', '76': 'Ultra Rapid Fire',
                 '1010': 'Snow ARURF', '2': '5v5 Blind Pick',
                 '4': '5v5 Ranked Solo', '8': '3v3 Normal',
                 '9': '3v3 Ranked Flex', '14': '5v5 Draft Pick',
                 '318': 'ARURF'}

    if game_mode == 'URF' or game_mode == 'CLASSIC':
        result = queue_ids.get(str(queue_id), '')
    else:
        result = modes.get(game_mode, '')

    return result
