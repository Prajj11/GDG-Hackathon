import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend import auth
from backend.database import Base, Account

@pytest.fixture
def client(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    monkeypatch.setattr(auth, 'SessionLocal', factory)
    monkeypatch.setattr(auth, 'PASSWORD_HASH', '')
    monkeypatch.delenv('DG_HOSTED', raising=False)
    with factory() as db:
        db.add(Account(username='testguardian', role='guardian', password_hash=auth.PASSWORDS.hash('a-long-test-password'), full_name='Test'))
        db.commit()
    app = FastAPI()
    app.include_router(auth.router)
    yield TestClient(app)
    engine.dispose()

def test_unknown_account_rejected(client):
    assert client.post('/api/auth/login', json={'username': 'unknown', 'password': 'anything'}).status_code == 401

def test_demo_password_is_not_a_bypass(client):
    assert client.post('/api/auth/login', json={'username': 'testguardian', 'password': 'demo123'}).status_code == 401
    assert client.post('/api/auth/login', json={'username': 'testguardian', 'password': 'a-long-test-password'}).status_code == 200

def test_hosted_registration_allowed_for_explicit_account_creation(client, monkeypatch):
    monkeypatch.setenv('DG_HOSTED', 'true')
    assert client.post('/api/auth/register', json={'username': 'newuser', 'password': 'a-long-test-password', 'role': 'ngo'}).status_code == 200

def test_caseworker_dependency_rejects_guardian(client):
    from fastapi import HTTPException
    token = client.post('/api/auth/login', json={'username': 'testguardian', 'password': 'a-long-test-password'}).json()['access_token']
    with pytest.raises(HTTPException):
        auth.authorize_ngo('Bearer ' + token)
