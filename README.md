# CSO Ansible Netbox

[![N|Solid](https://upload.wikimedia.org/wikipedia/commons/3/31/Juniper_Networks_logo.svg)](https://www.juniper.net/us/en/products-services/sdn/contrail/contrail-service-orchestration/)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

## ⚙️ `Overview`

This project's goal is to be an easier way to interact with Juniper's CSO to build out a new SD-WAN site.

- ease the authentication process with CSO for tokens
- build out new SD-WAN sites

## 📋 `Expectations from the playbook`

This playbook is expecting data to be passed to it, specifically the data required to build out a new SD-WAN site. Below is an example:

```sh
cpe_device_type: srx
site_name: Pensacola
tenant_name: Redtail
```

You can either pass these variables to the playbook from a source like ServiceNow, or simply copy those listed above into a new file located under `group_vars/all` directory; make sure the file extension is `.yml` and you'll be good to go.

## 🚀 `Executing the playbook`

After, and only after, you've created your own `secrets.yml` file in the `group_vars/all/` directory, you'll be ready to execute the playbook. An example file is located in the root of this project. 

The playbook is executed with a single command (or through Ansible Tower).

```sh
ansible-playbook pb.cso.create.site.yml
```

If you used Ansible Vault to encrypt your `group_vars/all/secrets.yml`, you need to append the `--ask-vault-pass` to your command.

## ⚙️ `How this playbook works`

The core functionality of this project is found with the `pb.cso.create.site.yml` playbook. Taking it apart, we see that there are three seperate services the playbook will accomplish:

1. working with Netbox
2. working with CSO
3. working with Mist

### 📋 `Working with Netbox`

The data we need from Netbox is stored in a couple of different locations, so you'll see us query the API in a few different roles. Additionally, the data returned from Mist isn't exactly the way we need it, so you'll see us build filter plugins to massage it to our needs.

#### Netbox Retrieval and Formatting

When we query Netbox's API, we need to make sure there aren't any characters in the site's name that will be problematic. Our first action runs our variable `site_name` through the filter plugin of `format_list_of_netbox_devices` to remove pesky spaces and dashes. The output of this function is stored as `site_name_dictionary.slug`.

We pass `site_name_dictionary.slug` to the Netbox API to retrieve a list of devices, and store the output as `site_devices`. We perform an extra cleaning act by storing the object's `json.results` as a new variable of the same `site_devices` name.

Cleanup is performed with the `netbox_device_data` filter plugin, and we overwrite the variable again with the name of `site_devices`. All pretty!

> We perform the identical order of operations for site data and prefixes. We won't revisit these steps, just know they all have a differnet API endpoint, receive different sets of data, and therefore use a seperate cleanup filter plugin.

### 📋 `Working with CSO`

We have three roles (or group of functions) for CSO. The first is to authenticate, second is to create the LAN segment, and the final is to deploy the LAN.

#### Authentication

CSO is expecting that we checkout a temporary token to perform our automation authentication. To allow for variations (different users/passwords/etc.) we are going to template the JSON payload instead of hardcoded sensative information.

Templating JSON is something I personally try to avoid doing too often, as it can often be difficult with data structures. But in this case, it is more than sufficient.

We use the built-in Ansible module for templating: `template`. This template requires a source and destination, which are passed here as `cso_auth.j2` and `/var/tmp/cso_auth.json` respectively. 

We pass the `run_once` to make sure Ansible doesn't repeat this task if there is more than one device in the inventory. More of a safeguard in our example.

#### Retrieving the API token

Ansible's core module for interacting with REST APIs is used next to send our JSON payload as a body.

Things of note here: 

- Our CSO base url comes from our file `api_base_urls.yml` under the `host_vars/localhost` directory.
- we are sending an HTTP POST message to the API
- the body of our request is the json file created in the previous step
- we hardcode our expected status code of 201
- the return value of the API call is stored as a variable called `login`

The `login` object will have a lot of useless info, we only want the value of the object `x_subject_token`, so we create a new variable called `token` and set it to this value. We'll be using this token for our API call when we create the site.

#### Build the Site

Similar to the need in our previous task, we have to account for the fact that data passed to the playbook will be different each time. So we need to template the JSON file that will ultimately be pushed to CSO. This requires a little detour:

JSON templating is hard, so you will oftentimes see me template YAML instead, and then convert the YAML into JSON when we need to send the payload to a REST API. These has its own set of challenges, but it's easier to work with, and looks better if you need to debug. So YAML it is!

First task is to template the YAML file, here are where all the parameters we mentioned in the `Expectations from the playbook` section. Take a peek at the jinja2 template if you're interested in what the CSO API is expecting, or how those parameters are passed to it.

Next step is more of grooming, I remove all blank lines from the YAML file to ensure the JSON rendering smooth. The benefits of this can be debated.

Third step is where some complexity appears. We load the contents of our templated file into a new variable called `yaml_config`. The built-in plugin `from_yaml` helps Ansible know how to load the file's content (not just clear text, but an actual data structure). I would love to make this a bit easier, but unfortunately the `template` module can only create a file, and we need to reference the contents of the file as a variable, so this is why we go down this route.

Finally we push the payload to the CSO API. We use the built-in module `uri` to handle this function again (keep things simple ;)). Our token is passed here, and we run the `to_json` filter plugin to convert our YAML to JSON just before we send off the request. 

Nice and simple!

#### Communicate to team in Slack

### 📋 `Working with Mist`

We need to follow a very similar path for Mist WLAN configurations as we did for building the LAN for CSO: template as YAML, store the file's contents in memory as a variable, convert to JSON just before sending to the API.

Since the order of operations is identical, there isn't any value in revisiting here.

## ⚠️ Very Important! ⚠️

Please make sure to create your own `secrets.yml` file and store it in `group_vars/all` directory. This file hosts many variables necessary to complete the ansible playbook, without this file all of your plans for SD-WAN automation are destroyed.

The `secrets_example.yml` file from the root directory of this project will get you started, simply update the variables with the values appropriate for your environment and move it to `group_vars/all` directory, overwriting the current file there.

This should do the trick nicely

```sh
$ mv secrets_example.yml ./group_vars/all/secrets.yml
```

### Optional:
> Leverage Ansible-Vault to encrypt the `secrets.yml` file before hosting on the public internet

> `ansible-vault encrypt secrets.yml`

## Development

Want to contribute? Great!

Submit a PR and let's work on this together :D