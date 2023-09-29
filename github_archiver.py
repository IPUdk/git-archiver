import os
import logging
import time
import requests
import json


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="UTC %(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("github_archiver.log"),  # Log to file
        logging.StreamHandler(),  # Log to console
    ],
)
logging.Formatter.converter = time.gmtime  # Use UTC time
log = logging.getLogger()  # Get root logger

access_token = os.environ.get("GITHUB_API_TOKEN")  # Needs "repo", "admin:org" scope
org_name = os.environ.get("GITHUB_ORG_NAME")  # Get the organization name


def get_repos():
    """
    Get a list of repositories under the organization
    """

    log.info(f"Getting list of repos in organization \"{org_name}\"...")
    # Define endpoint
    endpoint = f"https://api.github.com/orgs/{org_name}/repos"
    # Define headers
    headers = {"Accept": "application/vnd.github+json",
               "Authorization": f"Bearer {access_token}"}
    # Initialize the output list
    repos = []

    # Paginate through the results
    page = 1
    per_page = 100
    while True:
        # Get page
        log.info(f"  Getting page {page} (page size: {per_page}) of repos...")
        response = requests.get(endpoint,
                                headers=headers,
                                params={"per_page": per_page, 
                                        "page": page})
        # Check response
        if response.status_code != 200:
            log.error("  Got non-200 response!")
            break
        # Convert JSON response to python object
        response_obj = json.loads(response.text)  # List of dicts
        # Add repos to list
        repos.extend(response_obj)
        # Check if there are no more repos to fetch
        if len(response_obj) < per_page:
            break
        # Increment page
        page += 1

    log.info(f"  Got {len(repos)} repos")

    return repos


def create_migration_export(repo_name):
    """
    Create a request for a migration archive for a repository
    """
    log.info(f"Starting generation migration archive for {repo_name}...")
    # Define endpoint
    endpoint = f"https://api.github.com/orgs/{org_name}/migrations"
    # Define headers
    headers = {"Accept": "application/vnd.github+json",
               "Authorization": f"Bearer {access_token}"}
    # Define data
    data = {"lock_repositories": True,  # Must be manually unlocked!
            "lock_reason": "migrating",
            "repositories": [f"{org_name}/{repo_name}"]}
    # Make request
    response = requests.post(
        endpoint,
        headers=headers,
        data=json.dumps(data),
    )
    # Check response
    if response.status_code != 201:
        log.error(f"Error creating migration for {repo_name}: {response.text}")
        return None
    # Convert JSON response to python object
    response_obj = json.loads(response.text)  # Dict
    migration_id = response_obj["id"]

    log.info(f"  Migration with migration_id={migration_id} created for {repo_name}")

    return response_obj


def get_migration_status(migration_id):
    """
    Get the status of a migration
    """
    log.info(f"Getting migration status for migration_id={migration_id}...")
    # Define endpoint
    endpoint = f"https://api.github.com/orgs/{org_name}/migrations/{migration_id}"
    # Define headers
    headers = {"Accept": "application/vnd.github+json",
               "Authorization": f"Bearer {access_token}"}
    # Make request
    response = requests.get(
        endpoint,
        headers=headers,
    )
    # Check response
    if response.status_code != 200:
        log.error(f"Error getting migration status for migration_id={migration_id}: {response.text}")
        return None
    # Convert JSON response to python object
    response_obj = json.loads(response.text)  # Dict
    migration_status = response_obj["state"]

    log.info(f"  Migration status for migration_id={migration_id} is {migration_status}")

    return migration_status


def get_commit_sha(repo, ref=""):
    """
    Get the commit SHA for a repository reference (defaults to the default branch)
    """
    specific_ref = ref != ""
    log.info(f"Getting the commit SHA for {repo['name']}{' at ' + ref if specific_ref else ''}...")
    # Define endpoint
    endpoint = f"https://api.github.com/repos/{org_name}/{repo['name']}/commits{'/' + ref if specific_ref else ''}"
    # Define headers
    headers = {"Accept": "application/vnd.github+json",
               "Authorization": f"Bearer {access_token}"}
    # Make request
    response = requests.get(
        endpoint,
        headers=headers,
    )
    # Check response
    if response.status_code != 200:
        log.error(f"Error getting the commit SHA: {response.text}")
        return None
    # Convert JSON response to python object
    sha = ""
    response_obj = json.loads(response.text)  # Dict or list of dicts depending on if a specific ref was provided
    if specific_ref:
        sha = response_obj["sha"]
    else:
        sha = response_obj[0]["sha"]

    log.info(f"  Commit SHA for {repo['name']} at {'default' if ref == '' else ref} is {sha}")

    return sha


def download_file(url, file_name):
    """
    Download a file from a URL to a local file
    """
    log.info(f"  Downloading {url} to {file_name}...")
    return file_name


def download_migration_export(repo, migration_id, file_path):
    """
    Download a migration archive for a repository
    """
    # Define endpoint
    endpoint = f"https://api.github.com/orgs/{org_name}/migrations/{migration_id}/archive"
    # Define headers
    headers = {"Authorization": f"Bearer {access_token}"}
    # Make request
    log.info(f"Getting migration archive download URL for {repo['name']}...")
    response = requests.get(
        endpoint,
        headers=headers,
    )
    # Check response
    if response.status_code != 302 and response.status_code != 200:
        log.error(f"Error downloading migration archive for {repo['name']}: {response.text}")

    file_name = os.path.join(file_path, f"export_{repo['name']}_{repo['id']}.tar.gz")
    log.info(f"  Downloading migration archive for {repo['name']} to {file_name}...")
    download_file(response.url, file_name)
    log.info(f"  Migration archive downloaded for {repo['name']}")


def download_project(repo, file_path, ref=""):
    """
    Download a project at a repository reference (defaults to the default branch) as a repository archive
    """
    specific_ref = ref != ""
    url = f"https://api.github.com/repos/{org_name}/{repo['name']}/tarball/{ref if specific_ref else ''}"
    file_name = os.path.join(file_path, f"repository_archive_{repo['name']}_{repo['id']}_{repo['sha']}.tar.gz")
    log.info(f"Downloading project archive for {repo['name']} to {file_name}...")
    download_file(url, file_name)
    log.info(f"  Project archive downloaded for {repo['name']}")



# Loop through the list of repositories and create a migration archive for each one
repos_raw = get_repos()
repos = []
for repo in repos_raw:
    repos.append({"id": repo["id"],
                  "name": repo["name"],
                  "sha": get_commit_sha(repo)})
print(repos)
