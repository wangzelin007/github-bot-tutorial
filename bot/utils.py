import logging
import re

logger = logging.getLogger('bot')


def get_latest_from_github(package_path='azure-cli'):
    try:
        import requests
        git_url = "https://raw.githubusercontent.com/Azure/azure-cli/main/src/{}/setup.py".format(package_path)
        response = requests.get(git_url, timeout=10)
        if response.status_code != 200:
            logger.info("Failed to fetch the latest version from '%s' with status code '%s' and reason '%s'",
                        git_url, response.status_code, response.reason)
            return None
        for line in response.iter_lines():
            txt = line.decode('utf-8', errors='ignore')
            if txt.startswith('VERSION'):
                match = re.search(r'VERSION = \"(.*)\"$', txt)
                if match:
                    logger.info("====== Latest azure cli version: %s ======", match.group(1))
                    return match.group(1)
    except Exception as ex:  # pylint: disable=broad-except
        logger.info("Failed to get the latest version from '%s'. %s", git_url, str(ex))
        return None


if __name__ == '__main__':
    get_latest_from_github()