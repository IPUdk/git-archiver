# Repository Archiver

This is a collection of simple scripts to export and archive projects in various version control systems.

> Portable binaries are available on the [releases page](https://github.com/IPUdk/git-archiver/releases)

## GitHub

The GitHub archiving script (`github_archiver.py`) is a Python script that uses the GitHub API to export and archive all projects in an *organization*.
It will trigger and download a GitHub migration archive and a repository archive for each project.

Downloads are placed next to the script in the `exports/github/` folder.

To run, do:

> Note: your GitHub Personal Access Token must have the `admin:org` and `repo` scopes.

```bash
GITHUB_API_TOKEN=<your_token> GITHUB_ORG_NAME=<your_org> python3 github_archiver.py
```

## GitLab

The GitLab archiving script (`gitlab_archiver.py`) is a Python script that uses the GitLab API to export and archive all projects in a *group*.
It will trigger and download a GitLab Export and a repository archive for each project.

Downloads are placed next to the script in the `exports/gitlab/` folder.

To run, do:

> Note: your GitLab Personal Access Token must have the `api` scope.

```bash
GITLAB_API_TOKEN=<your_token> GITLAB_GROUP_ID=<your_group> python3 gitlab_archiver.py
```
