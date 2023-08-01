# Repository Archiver

This is a simple script to archive all projects found under a GitLab group.

It will trigger and download a GitLab Export and a repoistory archive for each project. Downloads are placed next to the script in the `export` folder.

To run, do:

> Note: your GitLab Personal Access Token must have the `api` scope. `read_api` is not sufficient.

```bash
GITLAB_API_TOKEN=<your_token> GITLAB_GROUP_ID=<your_group> python3 gitlab_archiver.sh
```
