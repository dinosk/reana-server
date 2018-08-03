# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
"""REANA-Server utils."""

import secrets
from uuid import UUID

import fs
from flask import current_app as app
from reana_db.database import Session
from reana_db.models import User

from reana_server.config import ADMIN_USER_ID


def is_uuid_v4(uuid_or_name):
    """Check if given string is a valid UUIDv4."""
    # Based on https://gist.github.com/ShawnMilo/7777304
    try:
        uuid = UUID(uuid_or_name, version=4)
    except Exception:
        return False

    return uuid.hex == uuid_or_name.replace('-', '')


def create_user_workspace(user_workspace_path):
    """Create user workspace directory."""
    reana_fs = fs.open_fs(app.config['SHARED_VOLUME_PATH'])
    if not reana_fs.exists(user_workspace_path):
        reana_fs.makedirs(user_workspace_path)


def get_user_from_token(access_token):
    """Validate that the token provided is valid."""
    user = Session.query(User).filter_by(access_token=access_token).\
        one_or_none()
    if not user:
        raise ValueError('Token not valid.')
    return str(user.id_)


def _get_users(_id, email, user_access_token):
    """Return all users matching search criteria."""
    search_criteria = dict()
    if _id:
        search_criteria['id_'] = _id
    if email:
        search_criteria['email'] = email
    if user_access_token:
        search_criteria['access_token'] = user_access_token
    users = Session.query(User).filter_by(**search_criteria).all()
    return users


def _create_user(email, user_access_token, admin_access_token):
    """Create user with provided credentials."""
    admin = Session.query(User).filter_by(id_=ADMIN_USER_ID).one_or_none()
    if admin_access_token != admin.access_token:
        raise ValueError('Admin access token invalid.')
    if not user_access_token:
        user_access_token = secrets.token_urlsafe(16)
    user_parameters = dict(access_token=user_access_token)
    user_parameters['email'] = email
    user = User(**user_parameters)
    Session.add(user)
    Session.commit()
    return user
