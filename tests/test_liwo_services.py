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

def test_filter_variants_v2(client):
    """Test variants properties filter endpoint"""
    result = client.get('/v2/filter_variants')
    assert result.status_code == 200
    assert b"Overschrijdingsfrequentie" in result.data

@pytest.mark.db
def test_login(client):
    """Test the login url"""
    result = client.post('/liwo.ws/Authentication.asmx/Login', {})
    assert result.status_code == 200

@pytest.mark.db
def test_scenarios_per_breach(client):
    """Test the scenarios_per_breach url"""
    body = {'layername': "waterdiepte", "breachid": 1}
    result = client.post('/liwo.ws/Tools/FloodImage.asmx/GetScenariosPerBreachGeneric', json=body)
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
