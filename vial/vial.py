#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import time
from wsgiref.handlers import format_date_time
import pprint

import flask
import pendulum

from __init__ import __version__ as API_VERSION

NAVIGATION_ITEMS = [
#    ('/#', 'Root'),
#    ('/doc', 'Documentation'),
]


def generate_expires_header(expires=False):
    """
    Generate HTTP expiration header.

    Args:
        expires: expiration in seconds or False for *imediately / no caching*

    Returns:
        dict: key/value pairs defining HTTP expiration information
    """
    headers = {}

    if expires is False:
        headers[
            'Cache-Control'] = 'no-store, no-cache, must-revalidate, ' \
                               'post-check=0, pre-check=0, max-age=0'
        headers['Expires'] = '-1'
    else:
        now = datetime.datetime.now()
        expires_time = now + datetime.timedelta(seconds=expires)
        headers['Cache-Control'] = 'public'
        headers['Expires'] = format_date_time(
            time.mktime(expires_time.timetuple()))

    return headers


class AppResponse(dict):
    """
    Container class for chalice app responses.
    """

    def __init__(self, *args, **kwargs):
        self.drop_dev = kwargs.get("drop_dev")

        try:
            del kwargs['drop_dev']
        except Exception:
            pass

        dict.__init__(self, *args, **kwargs)

        if '_dev' not in self:
            self['_dev'] = dict()

        try:
            self['version'] = API_VERSION
        except NameError:
            self['version'] = '0.0.42'
        self['_now'] = pendulum.now(tz='UTC').strftime('%Y-%m-%d %H:%M:%S')

        if 'navigation' not in self.keys():
            nav_items = list(self.navigation)
            if nav_items:
                self['navigation'] = nav_items

    @property
    def navigation(self):
        for data in NAVIGATION_ITEMS:
            try:
                (i_url, i_label, whitelist_key) = data
            except ValueError:
                whitelist_key = None
                (i_url, i_label) = data

            if whitelist_key and whitelist_key not in self.get("whitelist", []):
                continue
            yield i_url, i_label

    def flask_obj(self, status_code=200, drop_dev=None, with_version=True,
                  expires=None, headers=None):
        """
        Generate a :py:class:`flask.Response` object for current application
        response object.

        Args:
            status_code (int): HTTP status code, default 200
            drop_dev (bool): Drop development information
            with_version (bool): include version information
            expires: expiration specification
            headers (dict): headers

        Returns:
            flask.Response: HTTP response object
        """
        del_keys = []

        if drop_dev is None:
            drop_dev = self.drop_dev

        if drop_dev:
            del_keys.append('_dev')

        if with_version is False:
            del_keys.append('version')

        for del_key in del_keys:
            try:
                del self[del_key]
            except KeyError:
                pass

        if headers is None:
            headers = dict()

        headers["Content-Type"] = "application/json"

        if expires is not None:
            headers.update(generate_expires_header(expires))

        try:
            body = json.dumps(self, indent=2, sort_keys=True)
        except TypeError:
            body = pprint.pformat(self)
            headers["Content-Type"] = "text/plain"

        return flask.Response(
            status=status_code,
            headers=headers,
            response=body
        )
