def test_app_factory_creates_app(client):
    response = client.get('/')
    assert response.status_code == 200
