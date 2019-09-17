# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

import os
from . import app_qpylib
from . import asset_qpylib
from . import json_qpylib
from . import log_qpylib
from . import offense_qpylib
from . import rest_qpylib

def is_sdk():
    ''' Returns True if code is executing via the SDK rather than
        in a live app deployment. Depends on the QRADAR_APPFW_SDK
        environment variable.
    '''
    return os.getenv('QRADAR_APPFW_SDK', 'no').lower() == 'true'

# ==== Logging ====
    
def log(message, level='INFO'):
    ''' Logs a message at the given level, which defaults to INFO.
        Level values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        Raises RuntimeError if logging was not previously initialised
        by a call to qpylib.create_log().
    '''
    log_qpylib.log(message, level)

def create_log():
    ''' Initialises logging with INFO as the threshold log level.
        Must be called before any call to qpylib.log().
    '''
    log_qpylib.create_log()

def set_log_level(level):
    ''' Sets the threshold log level.
        Level values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    '''
    log_qpylib.set_log_level(level)

# ==== App details ====

def get_app_id():
    ''' Returns the "app_id" value from the app manifest,
        or 0 if app_id is not in the manifest.
    '''
    return app_qpylib.get_app_id()

def get_app_name():
    ''' Returns the "name" value from the app manifest.
        Raises KeyError if "name" is not in the manifest.
    '''
    return app_qpylib.get_app_name()

def get_manifest_json():
    ''' Returns the content of the app manifest as a Python object. '''
    return app_qpylib.get_manifest_json()

def get_manifest_field_value(key, default_value=None):
    ''' Returns the value of "key" from the app manifest.
        If "key" is not in the manifest and default_value
        was supplied, default_value is returned.
        Raises KeyError if "key" is not in the manifest and
        no default_value was supplied.
    '''
    return app_qpylib.get_manifest_field_value(key, default_value)

def get_store_path(relative_path=''):
    ''' Returns the app store path, joined with relative_path. '''
    return app_qpylib.get_store_path(relative_path)

def get_root_path(relative_path=''):
    ''' Returns the app root path, joined with relative_path. '''
    return app_qpylib.get_root_path(relative_path)

def get_app_base_url():
    """ Returns the QRadar app proxy prefix. """
    return app_qpylib.get_app_base_url()

def q_url_for(endpoint, **values):
    """ Returns the QRadar app proxy prefix joined to the Flask endpoint url. """
    return get_app_base_url() + app_qpylib.get_endpoint_url(endpoint, **values)

def get_console_address():
    ''' Returns the QRadar console IP address.
        Raises KeyError if environment variable QRADAR_CONSOLE_IP is not set.
    '''
    return app_qpylib.get_console_ip()

def get_console_fqdn():
    ''' Returns the QRadar console fully-qualified domain name.
        Raises KeyError if environment variable QRADAR_CONSOLE_FQDN is not set.
    '''
    return app_qpylib.get_console_fqdn()

# ==== REST ====

def REST(rest_action, request_url, headers=None, data=None, params=None,
         json_body=None, version=None, verify=None, timeout=60):
    ''' Invokes a rest_action request to request_url using the Python requests module.
        Returns a requests.Response object.
        Raises ValueError if rest_action is not one of GET, PUT, POST, DELETE.
    '''
    if is_sdk():
        rest_func = rest_qpylib.sdk_rest
    else:
        rest_func = rest_qpylib.live_rest
    return rest_func(rest_action, request_url, headers=headers,
                     data=data, params=params, json_body=json_body,
                     version=version, verify=verify, timeout=timeout)

# ==== JSON ====

def to_json_dict(python_obj, classkey=None):
    """ Converts a Python object into a dict usable with the REST function.
        Recursively converts fields which are also Python objects.
    """
    return json_qpylib.to_json_dict(python_obj, classkey)

def register_jsonld_endpoints():
    ''' Registers JSON-LD endpoints from the app manifest. '''
    json_qpylib.register_jsonld_endpoints()

def register_jsonld_type(context):
    ''' Registers a JSON-LD endpoint from the given context. '''
    json_qpylib.register_jsonld_type_from_context(context)

def get_offense_rendering(offense_id, render_type):
    ''' Returns an offense, rendered according to render_type.
        render_type is HTML or JSONLD.
    '''
    return offense_qpylib.get_offense_rendering(offense_id, render_type)

def get_asset_rendering(asset_id, render_type):
    ''' Returns an asset, rendered according to render_type.
        render_type is HTML or JSONLD.
    '''
    return asset_qpylib.get_asset_rendering(asset_id, render_type)

def render_json_ld_type(jld_type, data, jld_id=None):
    ''' Returns a JSON-LD type value rendered as a JSON-formatted string. '''
    return json_qpylib.render_json_ld_type(jld_type, data, jld_id)
