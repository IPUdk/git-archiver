# git-archiver

This is a collection of simple scripts to export and archive projects in various version control systems.

> Portable binaries are available on the [releases page](https://github.com/IPUdk/git-archiver/releases)

## GitHub

The GitHub archiving script (`github_archiver.py`) is a Python script that uses the GitHub API to export and archive all projects in an *organization*.
It will trigger and download a GitHub migration archive and a repository archive for each project.

Downloads are placed next to the script in the `exports/github/` folder.

To run, do:

> ~Note: your GitHub Personal Access Token must have the `admin:org` and `repo` scopes.~

> Note: your GitHub Personal Access Token (fine-grained permissions) must have read-only access to the following scopes:
> - Repositories
>   - Contents
>   - Deployments
>   - Issues
>   - Metadata
>   - Pages
>   - Pull Requests
> - Organization
>   - Administration
 
```bash
GITHUB_API_TOKEN="<your_token>" GITHUB_ORG_NAME="<your_org>" python3 github_archiver.py
```

```powershell
$env:GITHUB_API_TOKEN = '<your_token>'; $env:GITHUB_ORG_NAME = '<your_group>'
poetry run python git_archiver\github_archiver.py
Remove-Item Env:\GITHUB_API_TOKEN; Remove-Item Env:\GITHUB_ORG_NAME
```

Optionally, you can specify a list of repositories to archive by setting the `GITHUB_REPOSITORIES` environment variable to a list of repository names/IDs separated by spaces. The list will be interpreted as a filter, skipping repositories not listed.

The following example will only archive the repositories `my-repo-name` and whichever repository has ID `12345678`:

```bash
GITHUB_API_TOKEN="<your_token>" GITHUB_ORG_NAME="<your_org>" GITHUB_REPOSITORIES="my-repo-name 12345678" python3 github_archiver.py
```



## GitLab

The GitLab archiving script (`gitlab_archiver.py`) is a Python script that uses the GitLab API to export and archive all projects in a *group*.
It will trigger and download a GitLab Export and a repository archive for each project.

Downloads are placed next to the script in the `exports/gitlab/` folder.

To run, do:

> Note: your GitLab Personal Access Token must have the `api` scope.

```bash
GITLAB_API_TOKEN="<your_token>" GITLAB_GROUP_ID="<your_group>" python3 gitlab_archiver.py
```

```powershell
$env:GITLAB_API_TOKEN = '<your_token>'; $env:GITLAB_GROUP_ID = '<your_group>'
poetry run python git_archiver\gitlab_archiver.py
Remove-Item Env:\GITLAB_API_TOKEN; Remove-Item Env:\GITLAB_GROUP_ID
```

Optionally, you can specify a list of repositories to archive by setting the `GITLAB_REPOSITORIES` environment variable to a list of repository names/IDs separated by spaces. The list will be interpreted as a filter, skipping repositories not listed.

The following example will only archive the repositories `my-repo-name` and whichever repository has ID `12345678`:

```bash
GITLAB_API_TOKEN="<your_token>" GITLAB_GROUP_ID="<your_group>" GITLAB_REPOSITORIES="my-repo-name 12345678" python3 gitlab_archiver.py
```
