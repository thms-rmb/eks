# Ubuntu Python devcontainer

Simple dev container for working with e.g. Invenio.

On creation with VSCode, a volume named `ubuntu-python-workdir` gets created, and is mounted to `/home/ubuntu/workdir`. Once inside, you can e.g. clone Invenio repo and then use the `File: Open Folder...` action to navigate to it. This should improve IO performance by a lot.

**Note**: You should update [postcreate](.devcontainer/postcreate) to reference your git user name and email.
