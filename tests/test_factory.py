from wine_scraper import create_app

def test_config():
    """
    If config not passed, there should be a default configuration, otherwise 
    configuration should be overwritten.
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

