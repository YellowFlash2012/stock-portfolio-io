import pytest
from project import create_app
from flask import current_app

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # establish an app ctx be4 accessing the logger
        with flask_app.app_context():
            current_app.logger.info('In the test_client() fixture...')
    

        yield testing_client #where the test happens