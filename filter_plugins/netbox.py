import json
import yaml


# ##################################################################
# ### format the return of GET dcim/devices/?slug={{ site_name }}
# ###   into an object that can be easily called by the jinja2
# ###   template the json used to create a device's config in Mist
# ##################################################################
def format_site_name(value):
    '''
    example payload:
      site_name: 
        original: The Woodlands
        lower: the woodlands
        slug: the-woodlands
        space_replaced: The-Woodlands
    '''
    site_name = dict()
    site_name["original"] = value
    site_name["lower"] = value.lower()
    site_name["slug"] = site_name["lower"].replace(" ", "-")
    site_name["space_replaced"] = value.replace(" ", "-")

    return site_name


# ##################################################################
# ### format the return of GET dcim/devices/?slug={{ site_name }}
# ###   into an object that can be easily called by the jinja2
# ###   template the json used to create a device's config in Mist
# ##################################################################
def format_list_of_netbox_devices(value):
    '''
    example payload:
      - config_context: {}
        device_role:
          slug: switch-l2
        device_type:
          slug: ex
        display_name: Magnolia-sw1
        name: Magnolia-sw1
        platform:
          slug: ex2300-c-12p
        serial: HW0216520055
        site:
          id: 17
          slug: magnolia
        status:
          value: active
        tags:
        - switch
        tenant:
          slug: redtail
    '''
    site = {}
    cpe = {}
    switch = {}
    for each in value:
        if each["device_role"]["slug"] == 'sdwan-cpe':
          cpe["config_context"] = each["config_context"]
          cpe["device_role"] = each["device_role"]["slug"]
          cpe["device_type"] = each["device_type"]["slug"]
          cpe["name"] = each["display_name"]
          cpe["platform"] = each["platform"]["slug"]
          cpe["serial"] = each["serial"]
          cpe["site"] = each["site"]["slug"]
          cpe["site_id"] = each["site"]["id"]
          cpe["site_url"] = each["site"]["url"]
          cpe["status"] = each["status"]["value"]
          cpe["tags"] = each["tags"]
          if each["tenant"] is not None:
            cpe["tenant"] = each["tenant"]["slug"]
          else:
            cpe["tenant"] = "not_found"

        site['cpe'] = cpe
        site['switch'] = switch
    
    return site
        
# ##################################################################
# ### format the return of GET dcim/interfaces/?device={{ item.name }}
# ###   into an object that can be easily called by the jinja2
# ###   template the json used to create a device's config in Mist
# ##################################################################
def format_list_of_netbox_interfaces(value):
    '''
    example payload:
      - item:
          config_context: {}
          device_role:
            slug: sdwan-cpe
          id: 15
          name: TheWoodlands-fw1
          serial: EE1718AF0085
          site:
            id: 24
            slug: thewoodlands
          status:
            value: active
          tags:
            - sdwan
            - spoke
        json:
          results:
            - description: '[ ge-1/0/1 ] MPLS'
              enabled: true
              id: 81
              mode:
                value: access
              name: WAN_1
              tagged_vlans: []
              tags: []
              untagged_vlan: null
    '''
    devices = []
    for each in value:
        # ##################################################################
        # ### create an empty dictionary called device and start 
        # ###   stuffing it with the output of each device's 
        # ###   characteristics. 
        # ##################################################################
        device = {}
        device["config_context"] = each["item"]["config_context"]
        device["id"] = each["item"]["id"]
        device["name"] = each["item"]["display_name"]
        device["role"] = each["item"]["device_role"]["slug"]
        device["tags"] = each["item"]["tags"]
        device["site"] = {}
        device["site"]["id"] = each["item"]["site"]["id"]
        device["site"]["name"] = each["item"]["site"]["slug"]
        device["site"]["status"] = each["item"]["status"]["value"]
        # ##################################################################
        # ### create an empty list called device["interfaces"]. start a loop 
        # ###   over each of the interfaces and start stuffing them in the
        # ###   interfaces list.
        # ##################################################################
        device["interfaces"] = []
        for interface in each["json"]["results"]:
          iface = {}
          iface["description"] = interface["description"]
          iface["enabled"] = interface["enabled"]
          iface["mode"] = interface["mode"]["value"]
          iface["name"] = interface["name"]
          iface["tagged_vlans"] = interface["tagged_vlans"]
          iface["tags"] = interface["tags"]
          iface["untagged_vlan"] = interface["untagged_vlan"]
          device["interfaces"].append(iface)

        devices.append(device)

    return devices


# ##################################################################
# ### format the return of GET dcim/devices/?slug={{ site_name }}
# ###   into an object that can be easily called by the jinja2
# ###   template the json used to create a device's config in Mist
# ##################################################################
def format_netbox_site_data(value):
    '''
      msg:
        asn: null
        city: The Woodlands
        contact_email: cremsburg@juniper.net
        contact_name: Calvin Remsburg
        contact_phone: '2813308004'
        country: United States
        description: 4775 W Panther Creek Dr
        facility: Retail Gas @ Panther Creek
        latitude: '30.167339'
        longitude: '-95.504849'
        name: TheWoodlands
        physical_address: 4775 W Panther Creek Dr, The Woodlands, Texas, 77381
        region: united-states
        slug: thewoodlands
        state: Texas
        street_address: 4775 W Panther Creek Dr
        tenant: redtail
        time_zone: America/Chicago
    '''
    site = {}
    for each in value:
        site["name"] = each["name"]
        site["slug"] = each["slug"]
        site["region"] = each["region"]["slug"]
        site["country"] = each["region"]["name"]
        site["tenant"] = each["tenant"]["slug"]
        site["facility"] = each["facility"]
        site["asn"] = each["asn"]
        site["time_zone"] = each["time_zone"]
        site["description"] = each["description"]
        site["physical_address"] = each["physical_address"]
        # ### split up the physical address by comma
        # ###   this will be used to derive the following:
        # ###   - street_address
        # ###   - city
        # ###   - state
        # ###   - zip_code
        address = each["physical_address"].split(',')
        site["street_address"] = address[0]
        site["city"] = str(address[1]).strip()
        site["state"] = str(address[2]).strip()
        site["zip_code"] = str(address[3]).strip()
        site["latitude"] = each["latitude"]
        site["longitude"] = each["longitude"]
        site["contact_name"] = each["contact_name"]
        site["contact_phone"] = each["contact_phone"]
        site["contact_email"] = each["contact_email"]

    return site


def format_netbox_site_prefixes(value):
    '''
      msg:
      - created: '2020-09-14'
        custom_fields: {}
        description: IoT Network Prefix
        family:
          label: IPv4
          value: 4
        id: 75
        is_pool: true
        last_updated: '2020-09-15T20:23:58.068126Z'
        prefix: 10.1.43.0/24
        role: null
        site:
          id: 27
          name: Sugar Land
          slug: sugar-land
          url: https://netbox-v285.centralus.cloudapp.azure.com/api/dcim/sites/27/
        status:
          id: 1
          label: Active
          value: active
        tags:
        - iot
        tenant:
          id: 3
          name: Redtail
          slug: redtail
          url: https://netbox-v285.centralus.cloudapp.azure.com/api/tenancy/tenants/3/
        vlan:
          display_name: 13 (IoT)
          id: 75
          name: IoT
          url: https://netbox-v285.centralus.cloudapp.azure.com/api/ipam/vlans/75/
          vid: 13
        vrf:
          id: 2
          name: IoT
          rd: '100:3'
          url: https://netbox-v285.centralus.cloudapp.azure.com/api/ipam/vrfs/2/
    '''
    site_prefixes = []
    for each in value:
        prefix = dict()
        prefix["description"] = each["description"]
        prefix["id"] = each["id"]
        prefix["prefix"] = each["prefix"]
        # ### time to dig in and make some new variables
        # ###   using the prefix variable. dhcp and gatway
        # ###   will be derived here, gateway going on to
        # ###   be used shortly to query for interface.
        stripped_last_octet = prefix["prefix"].split('0/')
        stripped_last_octet = str(stripped_last_octet[0]).strip()
        # ### set the default gateway
        prefix["gateway"] = stripped_last_octet + '1'
        # ### set the dhcp attributes
        prefix["dhcp"] = dict()
        prefix["dhcp"]["low"] = stripped_last_octet + '10'
        prefix["dhcp"]["high"] = stripped_last_octet + '250'
        # ### set the site attributes
        prefix["site"] = dict()
        prefix["site"]["id"] = each["site"]["id"]
        prefix["site"]["slug"] = each["site"]["slug"]
        prefix["tags"] = each["tags"]
        # ### set the tenant attributes
        prefix["tenant"] = dict()
        prefix["tenant"]["id"] = each["tenant"]["id"]
        prefix["tenant"]["slug"] = each["tenant"]["slug"]
        # ### set the vlan attributes
        prefix["vlan"] = dict()
        prefix["vlan"]["id"] = each["vlan"]["id"]
        prefix["vlan"]["name"] = each["vlan"]["name"]
        prefix["vlan"]["vid"] = each["vlan"]["vid"]
        # ### set the vrf attributes
        prefix["vrf"] = dict()
        prefix["vrf"]["id"] = each["vrf"]["id"]
        prefix["vrf"]["name"] = each["vrf"]["name"]
        prefix["vrf"]["rd"] = each["vrf"]["rd"]

        site_prefixes.append(prefix)

    return site_prefixes


def format_netbox_interfaces_and_prefixes(value):
    '''
      - item:
          description: Network Management Prefix
          dhcp:
            high: 10.1.40.250
            low: 10.1.40.10
          gateway: 10.1.40.1
          id: 72
          prefix: 10.1.40.0/24
          site:
            id: 27
            slug: sugar-land
          tags:
          - network
          tenant:
            id: 3
            slug: redtail
          vlan:
            id: 72
            name: Network
            vid: 10
          vrf:
            id: 5
            name: Default
            rd: '1:1'
        json:
          count: 1
          next: null
          previous: null
          results:
          - address: 10.1.40.1/24
            created: '2020-09-15'
            custom_fields: {}
            description: Network Management Gateway
            dns_name: ''
            family:
              label: IPv4
              value: 4
            id: 113
            interface:
              device:
                display_name: SugarLand-fw1
                id: 27
                name: SugarLand-fw1
                url: https://netbox-v285.centralus.cloudapp.azure.com/api/dcim/devices/27/
              id: 86
              name: ge-0/0/2
              url: https://netbox-v285.centralus.cloudapp.azure.com/api/dcim/interfaces/86/
              virtual_machine: null
            last_updated: '2020-09-15T20:18:52.486680Z'
            nat_inside: null
            nat_outside: null
            role: null
            status:
              id: 1
              label: Active
              value: active
            tags:
            - network
            tenant:
              id: 3
              name: Redtail
              slug: redtail
              url: https://netbox-v285.centralus.cloudapp.azure.com/api/tenancy/tenants/3/
            vrf:
              id: 5
              name: Default
              rd: '1:1'
              url: https://netbox-v285.centralus.cloudapp.azure.com/api/ipam/vrfs/5/
    '''
    interface_configurations = []
    for each in value:
        interface = dict()
        # ### build interface parameters
        interface["iface"] = each["json"]["results"][0]
        # ### build prefix parameters
        interface["prefix"] = each["item"]

        interface_configurations.append(interface)

    return interface_configurations

class FilterModule(object):
    ''' 
    20200912: @packetferret
    Netbox Jinja2 filter plugins
    '''

    def filters(self):
        return {
            # jinja2 overrides
            'format_list_of_netbox_devices': format_list_of_netbox_devices,
            'format_list_of_netbox_interfaces': format_list_of_netbox_interfaces,
            'format_site_name': format_site_name,
            'format_netbox_site_data': format_netbox_site_data,
            'format_netbox_site_prefixes': format_netbox_site_prefixes,
            'format_netbox_interfaces_and_prefixes': format_netbox_interfaces_and_prefixes,
        }