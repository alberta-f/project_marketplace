import pytest


@pytest.fixture
async def test_user(client):
    data = {
        'email': 'testuser@example.com',
        'password': 'password123',
        'username': 'tester'
    }

    response = await client.post('user/register', json=data)
    assert response.status_code == 201
    return data

def test(test_user):
    print(test_user['email'])
