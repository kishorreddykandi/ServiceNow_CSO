FROM centos/python-36-centos7:latest

### -------------------------------------------------
### Metadata information
### -------------------------------------------------
LABEL name="snow-automation"
LABEL maintainer="packetferret@gmail.com"
LABEL description="ansible container"
LABEL license="GPLv2"
LABEL url="https://github.com/packetferret/snow-automation"
LABEL build-date="20200917"

### -------------------------------------------------
### Change directory to /home/tmp
### -------------------------------------------------
WORKDIR /home/tmp/files

### -------------------------------------------------
### Add and install python packages
### -------------------------------------------------
ADD config/requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install --upgrade pip

### -------------------------------------------------
### Install Ansible Galaxy roles
### -------------------------------------------------
RUN ansible-galaxy install juniper.junos

### -------------------------------------------------
### Change directory to /opt/app-root/src/ansible
### -------------------------------------------------
WORKDIR /opt/app-root/src/ansible

### -------------------------------------------------
### Environmentals
### -------------------------------------------------
ENV HAPPY True
ENV SHELL /usr/bin/zsh
ENV ANSIBLE_CONFIG /home/tmp/files/ansible/ansible.cfg
