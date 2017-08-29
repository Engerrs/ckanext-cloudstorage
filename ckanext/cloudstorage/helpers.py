#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ckanext.cloudstorage.storage import ResourceCloudStorage
from ckan import model
import json
from ckan.common import c


def use_secure_urls(res):
    return all([
        ResourceCloudStorage.use_secure_urls.fget(None),
        # Currently implemented just AWS version
        'S3' in ResourceCloudStorage.driver_name.fget(None)
    ])


def get_cloud_config_storage(package_id):
    data = model.get_system_info('cloud_configuration')
    if data:
        data = json.loads(data)
        containers = json.loads(data['buckets'])
        r = model.Package.get(package_id)
        org = model.Group.get(r.owner_org)
        if data['organizations_storage'] == 'Yes':
            org_settings = model.get_system_info('org_config_' + org.id)
            if org_settings:
                org_settings = json.loads(org_settings)
                if org_settings['users_select_storage'] == 'Yes':
                    dataset_settings = model.get_system_info('dataset_config_' + r.id)
                    if dataset_settings:
                        dataset_settings = json.loads(dataset_settings)
                        container = containers[dataset_settings['storage']]
                        c.c_bucket_name = dataset_settings['storage']
                        c.c_driver = container['driver']
                        c.c_driver_options = container['driver_options']
                        return data
                    else:
                        container = containers[org_settings['storage']]
                        c.c_bucket_name = org_settings['storage']
                        c.c_driver = container['driver']
                        c.c_driver_options = container['driver_options']
                        return data
                else:
                    container = containers[org_settings['storage']]
                    c.c_bucket_name = org_settings['storage']
                    c.c_driver = container['driver']
                    c.c_driver_options = container['driver_options']
                    return data
            else:
                for container in containers:
                    if 'default' in containers[container] and containers[container]['default'] == 'Yes':
                        settings = containers[container]
                        c.c_bucket_name = container
                        c.c_driver = settings['driver']
                        c.c_driver_options = settings['driver_options']
                        return data
        else:
            for container in containers:
                if 'default' in containers[container] and containers[container]['default'] == 'Yes':
                    settings = containers[container]
                    c.c_bucket_name = container
                    c.c_driver = settings['driver']
                    c.c_driver_options = settings['driver_options']
                    return data
    else:
        data = ''
        return data


def org_change_cloudstorage():
    settings = model.get_system_info('cloud_configuration')
    if settings:
        settings = json.loads(settings)
    else:
        return False

    if settings['organizations_storage'] == 'Yes' and settings['storage'] != 'Filestorage':
        return True
    else:
        return False


def user_change_cloudstorage(package):
    settings = model.get_system_info('cloud_configuration')
    org_settings = model.get_system_info('org_config_' + package['organization']['id'])
    if settings:
        settings = json.loads(settings)
    else:
        return False

    if org_settings:
        org_settings = json.loads(org_settings)
    else:
        return False

    if settings['storage'] != 'Filestorage' and settings['users_select_storage'] == 'Yes' and org_settings['users_select_storage'] == 'Yes':
        return True
    else:
        return False
