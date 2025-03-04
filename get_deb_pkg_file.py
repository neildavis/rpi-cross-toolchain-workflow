import requests
import json
import argparse
import sys
import os

def get_package_versions(package_name):
    """
    Fetches version data for a given package from sources.debian.org API.

    Args:
        package_name (str): The name of the package.

    Returns:
        dict or None: Parsed JSON response as a dictionary, or None if an error occurs.
    """
    url = f"https://sources.debian.org/api/src/{package_name}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None

def normalize_version(version_string):
    """
    Normalizes a version string according to the specified rules.

    Args:
        version_string: The input version string.

    Returns:
        A normalized version string.
    """
    # 2. From the input string, remove and trailing text from (and including) a hyphen until the end
    last_hyphen_index = version_string.rfind('-')
    if last_hyphen_index != -1:
        version_string_no_hyphen = version_string[:last_hyphen_index]
    else:
        version_string_no_hyphen = version_string

    # 3. Split the remaining input string into components separated by the period character
    components = version_string_no_hyphen.split('.')

    # 4. If there are more than 3 components, discard the last ones
    if len(components) > 3:
        components = components[:3]

    # 5. If there are fewer than 3 components, add a zero character for each component until there are 3 components
    while len(components) < 3:
        components.append('0')

    # 6. Join the resulting components into a string using the period character as a separator and return the result
    return '.'.join(components)

def find_matching_version(package_data, version_prefix):
    """
    Finds the closest semantic version match for a given prefix in package versions.

    If an exact prefix match isn't found, it will look for the closest version
    based on semantic versioning rules.

    Args:
        package_data (dict): Parsed JSON data.
        version_prefix (str): The version prefix to search for (e.g., "1.2", "1.35.1").

    Returns:
        dict or None: The version entry of the closest semantic version match, or None if not found.
    """
    if not package_data or "versions" not in package_data:
        return None

    prefix_components = normalize_version(version_prefix).split('.')
    matched_score = 999
    matched_version = None
    for version_entry in package_data["versions"]:
        version_str = version_entry.get("version")
        if not version_str:
            continue # Skip if entry does not contain a 'version' field
        
        # normalize the candidate version and split
        normalized_version = normalize_version(version_str)
        normalized_components = normalized_version.split('.')

        if normalized_components[0] != prefix_components[0]:
            #print(f'Skipping version {version_str} ({normalized_version}) - mismatched MAJOR version')
            continue # Skip if Major version does not match
        if normalized_components[1] != prefix_components[1]:
            #print(f'Skipping version {version_str} ({normalized_version}) - mismatched MINOR version')
            continue # Skip if Minor version does not match
        if normalized_components[2] == prefix_components[2]:
            #print(f'Exact match found for version {version_str} ({normalized_version})')
            return version_str # exact match is returned immediately

        # score the candidate on minor version and check against current best match
        cand_score = abs(int(normalized_components[2]) - int(prefix_components[2]))
        if cand_score < matched_score:
            #print(f'Candidate version {version_str} ({normalized_version}) selected as best score so far: {cand_score}')
            matched_score = cand_score
            matched_version = version_str
        else:
            #print(f'Discarding version {version_str} ({normalized_version}) - inferior score {cand_score}')
            pass
        
    return matched_version

def download_file(download_url, filename):
    """
    Downloads a file from the given URL and saves it with the specified filename.

    Args:
        download_url (str): The URL of the file to download.
        filename (str): The name to save the file as.

    Returns:
        bool: True if download was successful, False otherwise.
    """
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file from {download_url}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find Debian package version and download a file using closest semantic version matching.")
    parser.add_argument("package", help="The name of the Debian package.")
    parser.add_argument("version_prefix", help="The version prefix to search for (e.g., '1', '1.2', '1.35.1').")
    parser.add_argument("path", help="The path to the file to download.")
    args = parser.parse_args()

    package_name = args.package
    version_prefix = args.version_prefix
    file_path = args.path

    package_info = get_package_versions(package_name)

    if package_info:
        version_string = find_matching_version(package_info, version_prefix)

        if version_string:
            print(f'Matched Debian version {version_string} (closest semantic match for prefix {version_prefix}) in package {package_name}')
            download_url = f"https://sources.debian.org/data/main/b/{package_name}/{version_string}/{file_path}"
            filename = os.path.basename(file_path)

            print(f"Attempting to download from: {download_url}")
            download_successful = download_file(download_url, filename)

            if download_successful:
                print(f"Successfully downloaded file as '{filename}'")
            else:
                sys.exit(1)

        else:
            print(f'Could not find a semantically close Debian version for version prefix {version_prefix} in package {package_name}')
            sys.exit(1)
    else:
        print(f"Could not retrieve package information for '{package_name}'.")
        sys.exit(1)