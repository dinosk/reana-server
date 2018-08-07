#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017 CERN.
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
# You should have received a copy of the GNU General Public License
# along with REANA; if not, see <http://www.gnu.org/licenses>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

"""OpenAPI specification file generator script."""

import json
import os

import click
from apispec import APISpec
from flask import current_app
from flask.cli import with_appcontext
from swagger_spec_validator.validator20 import validate_json

# Import your marshmallow schemas here
# from example_package.schemas import Example_schema,

# Software title. E.g. just name of the module exposing the API.
__title__ = "REANA Server"

# Short description of the API. Supports GitHub Flavored Markdown.
__api_description__ = "Submit workflows to be run on REANA Cloud"

# Version of the API provides, not version of the OpenAPI specification.
__api_version__ = "0.1"

# Filepath where the OpenAPI specification file should be written to.
__output_path__ = "temp_openapi.json"

# Security scheme definitions.
__security_definitions__ = {
                            "JWT": {
                                "description": "",
                                "type": "apiKey",
                                "name": "Authorization",
                                "in": "header"
                            }
                        }


@click.command()
@with_appcontext
def build_openapi_spec():
    """Creates an OpenAPI definition of Flask application,
    check conformity of generated definition against OpenAPI 2.0 specification
    and writes it into a file."""

    package = __title__
    desc = __api_description__
    ver = __api_version__
    security_definitions = __security_definitions__
    

    # Create OpenAPI specification object
    spec = APISpec(
        title=package,
        version=ver,
        securityDefinitons=security_definitions,
        info=dict(
            description=desc
        ),
        plugins=(
            'apispec.ext.flask',
            'apispec.ext.marshmallow'
        )
    )

    # Add marshmallow schemas to the specification here
    # spec.definition('Example', schema=Example_schema)

    # Collect OpenAPI docstrings from Flask endpoints
    for key in current_app.view_functions:
        if key != 'static' and key != 'get_openapi_spec':
            spec.add_path(view=current_app.view_functions[key])

    spec_json = json.dumps(spec.to_dict(), indent=2,
                           separators=(',', ': '), sort_keys=True)

    # Output spec to JSON file
    with click.open_file(__output_path__, mode='w+',
                         encoding=None, errors='strict',
                         lazy=False, atomic=False) as output_file:

        output_file.write(spec_json)

        click.echo(
            click.style('OpenAPI specification written to {}'.format(
                output_file.name), fg='green'))

    # Check that generated spec passes validation. Done after writing to file
    # in order to give user easy way to access the possible erroneous spec.
    with open(os.path.join(os.getcwd(), __output_path__)) as output_file:

        validate_json(json.load(output_file), 'schemas/v2.0/schema.json')

        click.echo(
            click.style('OpenAPI specification validated successfully',
                        fg='green'))

    return spec.to_dict()


if __name__ == '__main__':
    build_openapi_spec()
