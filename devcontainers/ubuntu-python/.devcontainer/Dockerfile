FROM ubuntu:22.04

SHELL ["/bin/bash", "-c"]

COPY ./host_uid ./host_gid /tmp/

RUN <<EOF
yes | unminimize
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade --yes
apt-get install --yes --no-install-recommends \
    locales \
    man-db \
    sudo \
    bash-completion \
    openssh-client \
    rsync \
    git \
    curl \
    ca-certificates \
    less \
    vim \
    lsb-release \
    build-essential \
    pkg-config \
    python3 \
    python3-venv \
    python3-dev \
    pipx \
    default-libmysqlclient-dev \
    libsasl2-dev \
    libldap2-dev \
    openjdk-21-jdk-headless

curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh
sudo -E bash nodesource_setup.sh

apt-get install --yes --no-install-recommends nodejs

apt-get clean --yes
rm -rf /var/lib/apt/lists/*

locale-gen en_US.UTF-8
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
EOF

RUN <<EOF

# Remove user ubuntu if exists
if id "ubuntu" &>/dev/null; then
    deluser --remove-home ubuntu
fi

host_uid=$(cat /tmp/host_uid)
host_gid=$(cat /tmp/host_gid)

current_user=$(getent passwd $host_uid | cut -d: -f1)
current_group=$(getent group $host_gid | cut -d: -f1)

# Delete user by the name stored in $current_user if it exists
if [ ! -z "$current_user" ]; then
    deluser --remove-home $current_user
fi

# Delete group by the name stored in $current_group if it exists
if [ ! -z "$current_group" ]; then
    delgroup $current_group
fi

addgroup --gid $host_gid ubuntu
adduser --uid $host_uid --gid $host_gid --disabled-password --gecos "" ubuntu
usermod --append --groups sudo ubuntu

echo '%sudo ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/sudo-nopasswd
echo 'Defaults:root runcwd=*' > /etc/sudoers.d/root-cwd
chmod 440 /etc/sudoers.d/sudo-nopasswd /etc/sudoers.d/root-cwd
EOF

RUN <<EOF
mkdir --parents /home/ubuntu/workdir
chown ubuntu:ubuntu /home/ubuntu/workdir
mkdir --parents /home/ubuntu/.ssh
chown ubuntu:ubuntu /home/ubuntu/.ssh
sudo --user=ubuntu --chdir=/home/ubuntu pipx ensurepath
EOF

USER ubuntu

RUN pipx ensurepath
RUN pipx install poetry
