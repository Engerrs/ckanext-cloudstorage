#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from pylons import c
from pylons.i18n import _

from ckan import logic, model
from ckan.lib import base, uploader
import ckan.lib.helpers as h
from ckan.common import request
import json
from ckan.controllers.package import PackageController
from ckanext.cloudstorage import helpers

abort = base.abort
check_access = logic.check_access
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized


class StorageController(base.BaseController):
    def resource_download(self, id, resource_id, filename=None):
        settings = model.get_system_info('cloud_configuration')
        if settings:
            settings = json.loads(settings)
            if settings['storage'] == 'Cloudstorage':
                context = {
                    'model': model,
                    'session': model.Session,
                    'user': c.user or c.author,
                    'auth_user_obj': c.userobj
                }

                try:
                    resource = logic.get_action('resource_show')(
                        context,
                        {
                            'id': resource_id
                        }
                    )
                except logic.NotFound:
                    base.abort(404, _('Resource not found'))
                except logic.NotAuthorized:
                    base.abort(401, _('Unauthorized to read resource {0}'.format(id)))

                # This isn't a file upload, so either redirect to the source
                # (if available) or error out.
                if resource.get('url_type') != 'upload':
                    url = resource.get('url')
                    if not url:
                        base.abort(404, _('No download is available'))
                    base.redirect(url)

                if filename is None:
                    # No filename was provided so we'll try to get one from the url.
                    filename = os.path.basename(resource['url'])

                upload = uploader.get_resource_uploader(resource)
                uploaded_url = upload.get_url_from_filename(resource['id'], filename)

                # The uploaded file is missing for some reason, such as the
                # provider being down.
                if uploaded_url is None:
                    base.abort(404, _('No download is available'))

                base.redirect(uploaded_url)
            else:
                pkg_cnt = PackageController()
                pkg_cnt.resource_download(id, resource_id, filename)
        else:
            pkg_cnt = PackageController()
            pkg_cnt.resource_download(id, resource_id, filename)


class CloudOptionsController(base.BaseController):

    def admin_configuration(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        try:
            logic.check_access('sysadmin', context, {})
        except logic.NotAuthorized:
            base.abort(401, _('Need to be system administrator to administer'))
        if request.method == 'POST':
            data_dict = {}
            data = request.params
            for item in data:
                data_dict[item] = data.get(item)

            del data_dict['save']

            data_dict = json.dumps(data_dict)
            model.set_system_info('cloud_configuration', str(data_dict))

        info = model.get_system_info('cloud_configuration')
        if info:
            c.admin_data = json.loads(info)
        else:
            c.admin_data = ''
        return base.render('admin/admin_configuration.html')

    def organization_configuration(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        group = model.Group.get(id)
        options = []

        if request.method == 'POST':
            data_dict = {}
            data = request.params
            for item in data:
                data_dict[item] = data.get(item)
            del data_dict['save']
            org_id = data_dict.get('id')
            data_dict = json.dumps(data_dict)
            model.set_system_info('org_config_' + org_id, str(data_dict))

        if group is None:
            abort(404, _('Organization not found'))
        if group.type not in ['organization']:
            abort(404, _('Incorrect group type'))

        try:
            data_dict = {'id': id}
            check_access('group_edit_permissions', context, data_dict)

            data_dict['include_datasets'] = False
            c.group_dict = logic.get_action('organization_show')(
                context, data_dict)
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(
                403,
                _('Not authorized to edit cloud configurations of %s') % (
                    id))

        if not helpers.org_change_cloudstorage():
            abort(401, _('Cant edit this page'))

        info = model.get_system_info('org_config_' + group.id)

        if info:
            c.org_config_data = json.loads(info)
        else:
            c.org_config_data = ''

        admin_config = model.get_system_info('cloud_configuration')

        admin_config = json.loads(admin_config)

        for key in admin_config:
            if key == 'buckets' and admin_config[key]:
                admin_config[key] = json.loads(admin_config[key])
                for bucket in admin_config[key]:
                    options.append({'value': bucket, 'text': bucket})

        return base.render(
            'organization/org_configuration.html',
            extra_vars={'group_type': group.type, 'buckets': options})

    def dataset_configuration(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        options = []

        try:
            check_access('package_update', context, {'id': id})
            c.pkg_dict = logic.get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('User not authorized to edit this package'))

        if not helpers.user_change_cloudstorage(c.pkg_dict):
            abort(401, _('Cant edit this page'))

        if request.method == 'POST':
            data_dict = {}
            data = request.params
            for item in data:
                data_dict[item] = data.get(item)
            del data_dict['save']

            pkg_id = data_dict.get('id')
            data_dict = json.dumps(data_dict)
            model.set_system_info('dataset_config_' + pkg_id, str(data_dict))

        info = model.get_system_info('dataset_config_' + c.pkg_dict['id'])

        if info:
            c.dataset_config_data = json.loads(info)
        else:
            c.dataset_config_data = ''

        admin_config = model.get_system_info('cloud_configuration')

        admin_config = json.loads(admin_config)

        for key in admin_config:
            if key == 'buckets' and admin_config[key]:
                admin_config[key] = json.loads(admin_config[key])
                for bucket in admin_config[key]:
                    options.append({'value': bucket, 'text': bucket})

        return base.render(
            'package/dataset_configuration.html',
            extra_vars={'buckets': options})
