

async def test_register(client):
    data = {
        'email': 'testuser@example.com',
        'password': 'password123',
        'username': 'tester'
    }

    response = await client.post('/user/register', data=data)
    assert response.status_code == 201
    return data
