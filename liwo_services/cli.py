"""Console script for liwo_services."""
import sys
import logging

import click

import liwo_services.app

from flask.cli import FlaskGroup

logging.basicConfig(
    level=logging.INFO
)


def create_app():
    # return the created wsgi app
    return liwo_services.app.app

@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the liwo_services application application."""
    pass

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
