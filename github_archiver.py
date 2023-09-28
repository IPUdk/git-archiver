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
    Function to get the list of repositories for the organization
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


def create_migration(repo_name):
    """
    Function to create a migration archive for a repository
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

    log.info(f"Migration with migration_id={migration_id} created for {repo_name}")

    return response_obj
# Loop through the list of repositories and create a migration archive for each one
repos = get_repos()
for repo in repos:
    print(f"{repo['id']}: {repo['name']}")
