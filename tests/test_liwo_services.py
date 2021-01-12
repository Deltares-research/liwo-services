#!/usr/bin/env python

"""Tests for `liwo_services` package."""

import pytest

from click.testing import CliRunner

import liwo_services
import liwo_services.main
import liwo_services.cli

@pytest.fixture
def app():
    yield liwo_services.main.app

@pytest.fixture
def db():
    yield liwo_services.main.db

@pytest.fixture
def client():
    app = liwo_services.main.app
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
    result = runner.invoke(liwo_services.cli.cli)
    assert result.exit_code == 0
    assert 'run' in result.output
    help_result = runner.invoke(liwo_services.cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output
