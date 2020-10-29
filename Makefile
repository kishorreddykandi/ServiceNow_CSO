SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help
.PHONY: help ansible apply backup bootstrap build config shell netbox-get

DOCKER_IMG = packetferret/snow-automation
DOCKER_TAG = 0.0.1

help:
	@echo ''
	@echo 'Makefile will help us build with the following commands'
	@echo '		make ansible				builds the configuration and applies them to the network devices'
	@echo '		make build				build the container image'
	@echo '		make dry				will only build the configurations, will not push to devices'

ansible:
	docker run -it \
	--rm \
	-v $(PWD)/files/:/home/tmp/files \
	-v $(PWD)/files/tmp:/tmp \
	-w /home/tmp/files/ansible/ \
	$(DOCKER_IMG):$(DOCKER_TAG) ansible-playbook pb.cso.create.site.yml \
	-e site_name=Clear-Lake \
	-e tenant_name=Redtail \
	-e cpe_device_type=srx

build:
	docker build -t $(DOCKER_IMG):$(DOCKER_TAG) tests/

dry:
	docker run -it \
	--rm \
	-v $(PWD)/files/:/home/tmp/files \
	-v $(PWD)/files/tmp:/tmp \
	-w /home/tmp/files/ansible/ \
	$(DOCKER_IMG):$(DOCKER_TAG) ansible-playbook tests/pb.cso.create.site.yml \
	-e site_name=Clear-Lake \
	-e tenant_name=Redtail \
	-e cpe_device_type=srx
