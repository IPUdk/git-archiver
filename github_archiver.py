import os
import logging
import time


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

