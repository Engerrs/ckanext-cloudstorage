# ckanext-cloudstorage

Implements support for using S3, Azure, or any of 30+ providers supported by
[libcloud][] to [CKAN][].

# Setup

After installing `ckanext-cloudstorage`, add it to your list of plugins in
your `.ini`:

    ckan.plugins = stats cloudstorage

If you haven't already, setup [CKAN file storage][ckanstorage] or the file
upload button will not appear.

Sysadmins can choose where resources will be uploaded, FileStorage or CloudStorage.

If CloudStorage is set, you must provide additional info needed for the uploading process:
1.Driver
2.Container_name
3.Driver_options

The info for `AWS S3` should be provided in JSON format, for example:

    {
    "CONTAINER_NAME": {"default": "Yes", "driver": "DRIVER", "driver_options": {"key" : "KEY", "secret": "SECRET_KEY"}},
    "CONTAINER_NAME_2": {"driver": "DRIVER_2", "driver_options": {"key" : "KEY", "secret": "SECRET_KEY"}}
    }

You can provide more then one CONTAINER_NAME seperated by comma, with different keys and drivers. The `default` parameter is needed to select the container that will be used.

Both the name of the driver and the name of the container/bucket are case-sensitive

You can find a list of driver names [here][storage] (see the `Provider
Constant` column.)

Each driver takes its own setup options. See the [libcloud][] documentation.
These options are passed in using `driver_options`, which is a Python dict.
For most drivers, this is all you need:

    "driver_options": {"key": "<your public key>", "secret": "<your secret key>"}

Sysadmins can provide an ability to choose between Containers for Organizations(users with admin role) and Users with editor role in organizations, by set `Organization select storage` and `Users select storage` to `Yes`.

Endpoints for configuration:
  For Sysadmins `/ckan-admin/cloud_configurations`. Tab for page appears on `/ckan-admin` page. Accessible only for sysadmins.
  For Admins in Organization `/organization/cloud_configurations/ORG_NAME`. Tab for page appears on `/organization/edit/ORG_NAME` page. Accessible only for Organization admins if the `Organization select storage` is set to `Yes` in sysadmins page.
  For Users with editor role in Organization `/dataset/cloud_configurations/DATASET_NAME`. Tab for page appears on `/dataset/edit/DATASET_NAME` page. Accessible only for Organization editors and admins if the `Users select storage` is set to `Yes` on both sysadmins and organization configuration pages.

# Support

Most libcloud-based providers should work out of the box, but only those listed
below have been tested:

| Provider | Uploads | Downloads | Secure URLs (private resources) |
| --- | --- | --- | --- |
| AWS S3   | YES | YES | YES (if `boto` is installed) |
| Rackspace | YES | YES | No |

# What are "Secure URLs"?

"Secure URLs" are a method of preventing access to private resources. By
default, anyone that figures out the URL to your resource on your storage
provider can download it. Secure URLs allow you to disable public access and
instead let ckanext-cloudstorage generate temporary, one-use URLs to download
the resource. This means that the normal CKAN-provided access restrictions can
apply to resources with no further effort on your part, but still get all the
benefits of your CDN/blob storage.

    ckanext.cloudstorage.use_secure_urls = 1

This option also enables multipart uploads, but you need to create database tables
first. Run next command from extension folder:
    `paster cloudstorage initdb -c /etc/ckan/default/production.ini `

With that feature you can use `cloudstorage_clean_multipart` action, which is available
only for sysadmins. After executing, all unfinished multipart uploads, older than 7 days,
will be aborted. You can configure this lifetime, example:

     ckanext.cloudstorage.max_multipart_lifetime  = 7

# Migrating From FileStorage

If you already have resources that have been uploaded and saved using CKAN's
built-in FileStorage, cloudstorage provides an easy migration command.
Simply setup cloudstorage as explained above, enable the plugin, and run the
migrate command. Provide the path to your resources on-disk (the
`ckan.storage_path` setting in your CKAN `.ini` + `/resources`), and
cloudstorage will take care of the rest. Ex:

    paster cloudstorage migrate <path to files> -c ../ckan/development.ini

# Notes

1. You should disable public listing on the cloud service provider you're
   using, if supported.
2. Currently, only resources are supported. This means that things like group
   and organization images still use CKAN's local file storage.

# FAQ

- *DataViews aren't showing my data!* - did you setup CORS rules properly on
  your hosting service? ckanext-cloudstorage can try to fix them for you automatically,
  run:

        paster cloudstorage fix-cors <list of your domains> -c=<CKAN config>

- *Help! I can't seem to get it working!* - send me a mail! tk@tkte.ch

[libcloud]: https://libcloud.apache.org/
[ckan]: http://ckan.org/
[storage]: https://libcloud.readthedocs.io/en/latest/storage/supported_providers.html
[ckanstorage]: http://docs.ckan.org/en/latest/maintaining/filestore.html#setup-file-uploads
