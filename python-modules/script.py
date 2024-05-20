import asyncio
import json
import os
from homeassistant_api import Client

async def turn_off_devices_in_zone():
    # Home Assistant API URL and Token
    hass_url = os.environ['HASS_URL']
    hass_token = os.environ['HASS_TOKEN']

    # Create a Home Assistant API client
    client = Client(hass_url, hass_token)

    # Load options from config
    with open('/data/options.json') as f:
        config = json.load(f)

    include_zones = config.get('include_zones', [])
    include_domains = config.get('include_domains', ['all'])
    dependencies = config.get('dependencies', {})
    exclude_identifiers = config.get('exclude_identifiers', [])
    exclude_entities = config.get('exclude_entities', [])
    max_retries = config.get('max_retries', 30)
    retry_interval = config.get('retry_interval', 10)

    if 'all' in include_domains:
        domains = ['light', 'switch', 'media_player']
    else:
        domains = include_domains

    entity_registry = await client.async_get_entity_registry()
    device_registry = await client.async_get_device_registry()
    area_registry = await client.async_get_area_registry()

    entities = []
    for domain in domains:
        domain_entities = client.states.async_entity_ids(domain)
        if domain_entities:
            entities.extend(domain_entities)

    devices_in_zone = []
    for entity_id in entities:
        if entity_id in exclude_entities:
            continue

        entity_entry = entity_registry.entities.get(entity_id)
        if not entity_entry:
            continue

        device_entry = device_registry.devices.get(entity_entry.device_id)
        if device_entry:
            # Check if the device has any identifiers in the blacklist
            if any(identifier[0] in exclude_identifiers for identifier in device_entry.identifiers):
                continue

            area_id = device_entry.area_id
        else:
            area_id = entity_entry.area_id

        if area_id:
            area_entry = area_registry.areas.get(area_id)
            if area_entry and area_entry.name in include_zones:
                devices_in_zone.append(entity_id)

    if not devices_in_zone:
        print(f"No devices found in zones '{include_zones}'.")
        return

    attempts = 0
    while devices_in_zone and attempts < max_retries:
        remaining_devices = []

        for device in devices_in_zone:
            if client.states.get(device).state == 'on':
                device_dependencies = dependencies.get(device, [])
                can_turn_off = True

                for dep in device_dependencies:
                    dep_entity_id = dep['entity_id']
                    if client.states.get(dep_entity_id).state == 'on':
                        can_turn_off = False
                        break

                if not can_turn_off:
                    remaining_devices.append(device)
                    continue

                try:
                    await client.services.async_call(device.split('.')[0], 'turn_off', {'entity_id': device})
                except Exception as e:
                    remaining_devices.append(device)
                    continue

                # Handle delay for dependent devices
                if device in dependencies:
                    for dep in dependencies[device]:
                        delay = dep.get('delay', 0)
                        if delay > 0:
                            await asyncio.sleep(delay)
            else:
                pass

        devices_in_zone = remaining_devices
        if devices_in_zone:
            await asyncio.sleep(retry_interval)
        attempts += 1

    if devices_in_zone:
        print(f"Some devices could not be turned off after {max_retries} attempts: {devices_in_zone}")
    else:
        print(f"All devices in zones '{include_zones}' have been turned off.")

if __name__ == "__main__":
    asyncio.run(turn_off_devices_in_zone())