#!/usr/bin/env python

"""Tests for `liwo_services` package."""

import pytest

from click.testing import CliRunner

from liwo_services import liwo_services
from liwo_services import cli
import liwo_services.app

@pytest.fixture
def app():
    yield liwo_services.app.app

@pytest.fixture
def db():
    yield liwo_services.app.db

@pytest.fixture
def client():
    app = liwo_services.app.app
    with app.test_client() as client:
        with app.app_context():
            yield client



def test_root(client):
    """Test the root url"""
    result = client.get('/')
    assert result.status_code == 200

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert 'run' in result.output
    help_result = runner.invoke(cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output
