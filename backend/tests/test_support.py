"""Anonymous support integration tests using disposable databases."""
import hashlib
import secrets
from datetime import timedelta
from sqlalchemy import select, func, delete

from backend.tests.test_api import client, send


def submit(client, secret=None, **fields):
    secret = secret or secrets.token_hex(32)
    response = client.post('/api/support/reports', headers={'Authorization': ''},
                           json={'anonymous_token': secret, **fields})
    return secret, response


def test_anonymous_receipt_privacy_and_retry_idempotency(client):
    from backend import database as dbm
    secret, response = submit(client, urgency_level='High')
    assert response.status_code == 201
    receipt = response.json()
    assert receipt['status'] == 'routed' and not receipt['human_contacted']
    assert response.headers['cache-control'] == 'no-store'
    assert submit(client, secret)[1].json()['id'] == receipt['id']
    url = '/api/support/reports/' + receipt['id']
    for auth in ['', 'Bearer wrong', 'Bearer test-token']:
        assert client.get(url, headers={'Authorization': auth}).status_code == 404
    assert client.get(url, headers={'Authorization': f'Bearer {secret}'}).status_code == 200
    assert 'anonymous_token' not in receipt and 'report_text' not in receipt
    with dbm.SessionLocal() as db:
        report = db.get(dbm.Report, receipt['id'])
        assert report.anonymous_token == hashlib.sha256(secret.encode()).hexdigest()
        assert report.linked_alert_id is None and report.detection_context is None
        assert db.scalar(select(func.count()).select_from(dbm.AidRoute)) == 1


def test_context_requires_consent_and_matching_capability(client):
    from backend import database as dbm
    result = send(client, 'Photo bhejo warna tumhari chats sabko dikha dunga. Abhi bhejo.').json()
    fields = {'linked_alert_id': result['alert_id'], 'context_token': result['support_context_token']}
    assert submit(client, **fields)[1].status_code == 422
    assert submit(client, share_detection_context=True, **(fields | {'linked_alert_id': 'wrong'}))[1].status_code == 422
    _, response = submit(client, share_detection_context=True, **fields)
    assert response.status_code == 201
    with dbm.SessionLocal() as db:
        report = db.get(dbm.Report, response.json()['id'])
        assert set(report.detection_context) == {'pattern_type', 'risk_level'}
        db.execute(delete(dbm.Alert).where(dbm.Alert.id == result['alert_id']))
        db.commit()
        db.refresh(report)
        assert report.linked_alert_id is None


def test_failed_route_stays_saved_and_can_retry(client, monkeypatch):
    from backend import aid, database as dbm
    provider = aid.aid_provider

    class BrokenProvider:
        def route(self, payload, *, idempotency_key):
            raise ConnectionError('simulated failure')

    monkeypatch.setattr(aid, 'aid_provider', BrokenProvider())
    secret, response = submit(client)
    assert response.json()['status'] == 'submitted'
    assert response.json()['aid_route'] is None
    monkeypatch.setattr(aid, 'aid_provider', provider)
    url = '/api/support/reports/' + response.json()['id'] + '/retry'
    for _ in range(2):
        result = client.post(url, headers={'Authorization': f'Bearer {secret}'})
        assert result.json()['status'] == 'routed'
    with dbm.SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(dbm.AidRoute)) == 1


def test_report_validation_and_independent_expiry(client):
    from backend import database as dbm
    assert submit(client, report_text='x' * 1501)[1].status_code == 422
    assert submit(client, name='Not collected')[1].status_code == 422
    secret, response = submit(client, report_text='x' * 1500)
    assert response.status_code == 201
    with dbm.SessionLocal() as db:
        db.get(dbm.Report, response.json()['id']).created_at = dbm.now() - timedelta(days=8)
        db.commit()
    url = '/api/support/reports/' + response.json()['id']
    assert client.get(url, headers={'Authorization': f'Bearer {secret}'}).status_code == 404
    with dbm.SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(dbm.Report)) == 0
        assert db.scalar(select(func.count()).select_from(dbm.AidRoute)) == 0
