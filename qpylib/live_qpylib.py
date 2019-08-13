# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

from .abstract_qpylib import AbstractQpylib
from flask import request, has_request_context
import os
from socket import gethostbyname, gethostname

class LiveQpylib(AbstractQpylib):
    APP_CERT_LOCATION = '/opt/app-root/etc/pki/tls/certs/ca-bundle.crt'
    QRADAR_CONSOLE_FQDN = 'QRADAR_CONSOLE_FQDN'
    QRADAR_CSRF = 'QRadarCSRF'
    SEC_HEADER = 'SEC'
    SEC_ADMIN_TOKEN = 'SEC_ADMIN_TOKEN'

    # ==== App details ====

    def get_app_base_url(self):
        """
        Gets the full url that will proxy an app request to its plugin servlet.
        If any of the information required for building the proxy is missing
        then an empty string is returned.
        """
        app_id = self._get_manifest_field_value('app_id', '')

        if app_id == '':
            self.log("get_app_base_url: app_id not found in manifest", 'error')
            return ''
            
        url_suffix = "/console/plugins/{0}/app_proxy".format(app_id)
        proxy_path = ''

        try:
            x_console_host = self._get_host_header()
            proxy_path = "https://{0}{1}".format(x_console_host, url_suffix)
            
        except: # pylint: disable=W0702
            console_ip = self._get_manifest_field_value('console_ip', '')
            if console_ip == '':
                self.log("get_app_base_url: console_ip not found in manifest", 'error')
            else:
                proxy_path = "https://{0}{1}".format(console_ip, url_suffix)

        self.log("get_app_base_url: proxy_path={0}".format(proxy_path), 'debug')
        return proxy_path

    def _get_host_header(self):
        return request.headers.get('X-Console-Host')

    # ==== REST ====

    def REST(self, rest_type, request_url, headers=None, data=None,
             params=None, json_body=None, version=None, verify=None,
             timeout=60):

        rest_headers = self._add_headers(headers, version)

        if os.getenv(self.QRADAR_CONSOLE_FQDN):
            console_address = os.getenv(self.QRADAR_CONSOLE_FQDN)
        else:
            console_address = self.get_console_address()

        full_url = "https://{0}/{1}".format(console_address, request_url)

        if os.path.isfile('/store/consolecert.pem'):
            # if /store/consolecert.pem exists then we need to pass it 
            # to be able to communicate with console
            verify = '/store/consolecert.pem'
        else:
            # If the verify value isn't a string - i.e. True, False or None
            # retrieve the cert file location to try and ensure all REST requests use SSL.
            if not isinstance(verify, str):
                verify = self._get_cert_filepath()

        self.log("REST type=" + rest_type +
                 " url=" + full_url +
                 " headers=" + str(rest_headers) +
                 " data=" + str(data) +
                 " params=" + str(params) +
                 " json_body=" + str(json_body) +
                 " verify=" + str(verify) +
                 " version=" + str(version), 'debug')

        return self._chooseREST(rest_type)(full_url, headers=rest_headers, data=data,
                                           params=params, json=json_body,
                                           timeout=timeout, verify=verify)

    def _get_cert_filepath(self):
        if '/etc/qradar_pki' in open('/proc/mounts').read():
            self.log('Using ca bundle cert from file: {0}'.format(str(self.APP_CERT_LOCATION)), level='debug')
            cert_filepath = self.APP_CERT_LOCATION
        else:
            self.log('/etc/qradar_pki is not mounted in the container. verify will be turned off', level='debug')
            cert_filepath = False
        return cert_filepath

    def _add_headers(self, headers, version=None):
        if headers is None:
            headers = {}

        if version is not None:
            headers['Version'] = version

        if headers.get('Host') is None:
            headers['Host'] = gethostbyname(gethostname())

        if has_request_context():
            if self.QRADAR_CSRF in request.cookies.keys():
                headers[self.QRADAR_CSRF] = request.cookies.get(self.QRADAR_CSRF)
            if self.SEC_HEADER in request.cookies.keys() \
                and self.SEC_HEADER not in headers.keys():
                headers[self.SEC_HEADER] = request.cookies.get(self.SEC_HEADER)

        if os.getenv(self.SEC_ADMIN_TOKEN):
            headers[self.SEC_HEADER] = os.getenv(self.SEC_ADMIN_TOKEN)

        return headers
