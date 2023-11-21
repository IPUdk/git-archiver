import os
import time
import logging
import gitlab


def recurse_groups_for_projects(group_id):
    group = gl.groups.get(group_id)
    projects = []
    log.info(f"  Fetching groups for group: {group.attributes['full_name']}")
    subgroups = group.subgroups.list(all=True)
    if len(subgroups) > 0:
        for subgroup in subgroups:
            projects += recurse_groups_for_projects(subgroup.get_id())

    group_projects = group.projects.list(get_all=True)

    projects += [
        {
            "name": p.attributes["name"].replace(" ", ""),
            "name_with_namespace": p.attributes["name_with_namespace"].replace(" ", ""),
            "id": p.attributes["id"],
        }
        for p in group_projects
    ]

    return projects

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="UTC %(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("gitlab_archiver.log"),  # Log to file
            logging.StreamHandler(),  # Log to console
        ],
    )
    logging.Formatter.converter = time.gmtime  # Use UTC time
    log = logging.getLogger()  # Get root logger


    log.info("-" * 80)
    log.info("Authenticating to GitLab...")
    access_token = os.environ.get("GITLAB_API_TOKEN")  # Needs "api" scope
    gl = gitlab.Gitlab("https://gitlab.com", private_token=access_token)
    gl.auth()


    log.info("-" * 80)
    group_id = os.environ.get("GITLAB_GROUP_ID")  # Can be name or ID
    repositories = os.environ.get("GITLAB_REPOSITORIES")  # Get the repositories to archive
    if repositories is not None:
        repositories = repositories.strip()
        repositories = repositories.replace(",", " ")
        repositories = repositories.replace(";", " ")
        repositories = repositories.split(" ")
        
        log.info(f"Filtering by repositories: {repositories}")
    log.info(f"Starting export of projects in group {group_id}")
    log.info("Recursing groups to get projects: ")
    projects = recurse_groups_for_projects(group_id)

    log.info("-" * 80)
    log.info("Projects found: ")
    for project in projects:
        print(f"  {project['name_with_namespace']} ({project['id']})")

    log.info("-" * 80)
    i = 0
    total = len(projects)
    digits = len(str(total))
    for project in projects:
        i += 1

        # Log
        log.info(f"Project {str(i).zfill(digits)}/{str(total)}")

        # Filter repositories
        if repositories is not None:
            repo_in_filter = (str(project["name"]) in repositories) or (str(project["id"]) in repositories)
            if repo_in_filter is False:
                log.info(f"Skipping {project['name']} - not in filter")
                continue
        log.info(f"Processing {project['name']} ({project['name_with_namespace']} - {project['id']})")

        # Create directory
        path = os.path.join(os.getcwd(), f"exports/gitlab/{project['name_with_namespace']}")
        os.makedirs(path, exist_ok=True)
        log.info(f"  Exporting to {path}")

        # Get project
        p = gl.projects.get(project["id"])

        # Trigger an export
        # Contents: https://docs.gitlab.com/ee/user/project/settings/import_export.html#items-that-are-exported
        log.info("  Triggering export...")
        export = p.exports.create({})  # <-- Sends an email to the token owner

        # Wait for the operation to finish
        server_ready = False
        while not server_ready:
            try:
                export.refresh()
                server_ready = True
            except Exception as e:
                print(e)
                server_ready = False
        # Check export status
        log.info(f"  Export status: {export.export_status}")
        while export.export_status != "finished":
            time.sleep(1)
            export.refresh()
            log.info(f"  Export status: {export.export_status}")

        # Download the export
        log.info("  Downloading and saving export...")
        file = os.path.join(path, f"export_{p.name}_{p.id}_{gl.version()[0]}.tgz")
        try:
            with open(
                file,
                "wb",
            ) as f:
                export.download(streamed=True, action=f.write)
        except Exception as e:
            log.error(e)
            log.error("  Download of export failed!")

        # Download the project as a repository archive
        # Get the latest commit SHA
        commits = p.commits.list(per_page=1, get_all=False)
        sha = commits[0].attributes["id"] if len(commits) > 0 else "null"
        # Download the archive
        log.info(f"  Downloading and saving repository archive (SHA: {sha})...")
        file = os.path.join(path, f"repository_archive_{p.name}_{p.id}_{sha}.tgz")
        try:
            tgz = p.repository_archive()
            with open(
                file,
                "wb",
            ) as f:
                f.write(tgz)
        except Exception as e:
            log.error(e)
            log.error("  Download of repository archive failed!")

    log.info("Done!")
