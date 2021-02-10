def test_revoke_access_token(client, db, admin_headers):
    resp = client.delete('/api/v1/auth/revoke_access', headers=admin_headers)
    assert resp.status_code == 200

    resp = client.get('/api/v1/users', headers=admin_headers)
    assert resp.status_code == 401


def test_revoke_refresh_token(client, admin_refresh_headers):
    resp = client.delete('/api/v1/auth/revoke_refresh', headers=admin_refresh_headers)
    assert resp.status_code == 200

    resp = client.post('/api/v1/auth/refresh', headers=admin_refresh_headers)
    assert resp.status_code == 401


def test_revoke_refresh_without_headers(client):
    resp = client.delete('/api/v1/auth/revoke_refresh')
    assert resp.status_code == 401
