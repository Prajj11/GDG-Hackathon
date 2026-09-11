import importlib
import os
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{tmp_path / "test.db"}')
    monkeypatch.setenv('DETECTOR', 'baseline')
    monkeypatch.setenv('DEMO_ACCESS_TOKEN', 'test-token')
    import backend.database as database
    importlib.reload(database)
    import backend.ml.detector as detector
    detector.get_detector.cache_clear()
    import backend.main as main
    importlib.reload(main)
    with TestClient(main.app, headers={'Authorization':'Bearer test-token'}) as client:
        yield client
    database.engine.dispose()

def send(client, text, conversation='test', **kwargs):
    return client.post('/api/messages/ingest', json={'text':text, 'conversation_id':conversation, **kwargs})

def test_flow_escalation_and_review(client):
    first = send(client, 'Tum apni age se bahut mature ho. Sirf main tumhe samajhta hoon. Gift bhejun?').json()
    second = send(client, 'Mummy papa ko mat batana. Ye humara secret hai. Private chat pe aao.').json()
    assert first['pattern_type'] == 'grooming-trust-building'
    assert second['escalated'] and second['risk_level'] == 'High'
    assert second['message_count'] == 2
    alert = client.get('/api/alerts/'+second['alert_id']).json()
    assert alert['risk_score'] >= 75
    assert client.patch('/api/alerts/'+alert['id'],json={'reviewed':True}).json()['reviewed'] is True
    summary = client.get('/api/dashboard/summary').json()
    assert summary['reviewed'] == 1 and summary['total_alerts'] == 2

def test_neutral_not_persisted(client):
    text = 'Great game! See you tomorrow with the rest of the team.'
    response = send(client, text).json()
    assert response['alert_id'] is None
    assert client.get('/api/alerts').json() == []
    from backend.database import SessionLocal, Conversation
    with SessionLocal() as db:
        conversation = db.get(Conversation, 'test')
        assert text not in str(conversation.signals)
        assert set(conversation.signals[0]) == {'pattern','at'}

@pytest.mark.parametrize('language,text',[
('Hindi','अभी अपनी फोटो भेजो वरना तुम्हारी बातें पूरे स्कूल को बता दूंगा।'),
('Malayalam','ഇപ്പോൾ ഫോട്ടോ അയയ്ക്കൂ, ഇല്ലെങ്കിൽ നിന്റെ രഹസ്യങ്ങൾ എല്ലാവരോടും പറയും.'),
('Manglish','Photo ayakku allenkil ninte secrets ellavarkkum parayum.')])
def test_multilingual_coercion(client,language,text):
    response = send(client,text,language=language)
    assert response.status_code == 200
    assert response.json()['pattern_type'] == 'grooming-coercive-language'

def test_repeated_harassment_and_isolation_between_conversations(client):
    text = 'Nobody likes you. You are worthless. Leave our group, loser.'
    assert not send(client,text,'one').json()['escalated']
    assert send(client,text,'one').json()['escalated']
    assert not send(client,text,'two').json()['escalated']

def test_snippets_and_settings(client):
    text = 'Photo bhejo warna tumhari chats sabko dikha dunga. Abhi bhejo.'
    result = send(client,text).json()
    assert client.get('/api/alerts/'+result['alert_id']).json()['flagged_snippet']
    assert client.patch('/api/settings',json={'retention_days':1,'snippets_enabled':False}).status_code == 200
    assert all(not a['flagged_snippet'] for a in client.get('/api/alerts').json())
    result = send(client,text).json()
    assert not client.get('/api/alerts/'+result['alert_id']).json()['flagged_snippet']

def test_minimal_excerpt_redacts_and_bounds():
    from backend.ml.detector import minimal_snippet
    snippet = minimal_snippet('private earlier context\nContact me at name@example.com +91 9876543210 https://example.com ' + 'x'*200)
    assert 'private earlier' not in snippet
    assert 'name@example' not in snippet and '987654' not in snippet and 'https://' not in snippet
    assert len(snippet) <= 141

def test_invalid_and_unauthorized_requests(client):
    assert send(client,'   ').status_code == 422
    assert send(client,'x'*2001).status_code == 422
    assert send(client,'hello','bad/id').status_code == 422
    assert client.get('/api/alerts',headers={'Authorization':'Bearer wrong'}).status_code == 401
    assert client.get('/api/alerts/not-found').status_code == 404
    assert client.patch('/api/settings',json={'retention_days':365,'snippets_enabled':True}).status_code == 422

def test_conversation_metadata_conflict(client):
    send(client,'Great game! See you tomorrow with the rest of the team.')
    assert send(client,'hello',child_label='Child 2').status_code == 409

def test_expired_alerts_and_signals(client):
    from backend.database import SessionLocal, Alert, Conversation, now
    from datetime import timedelta
    text = 'Nobody likes you. You are worthless. Leave our group, loser.'
    result = send(client,text).json()
    with SessionLocal() as db:
        db.get(Alert,result['alert_id']).created_at = now()-timedelta(days=8)
        conversation = db.get(Conversation,'test')
        conversation.signals = [{'pattern':'bullying-harassment','at':(now()-timedelta(hours=25)).isoformat()}]
        db.commit()
    assert client.get('/api/alerts').json() == []
    assert not send(client,text).json()['escalated']

def test_model_is_explicit(client):
    assert client.get('/api/health').json()['model_kind'] == 'baseline'
    from backend.ml.detector import Detector
    assert Detector('baseline').kind == 'baseline'

def test_hosted_demo_requires_token(client, monkeypatch):
    import backend.main as main
    monkeypatch.setenv('DG_HOSTED','true')
    with pytest.raises(RuntimeError, match='at least 24 characters'):
        with TestClient(main.app):
            pass

def test_models_compile_for_postgres():
    from sqlalchemy.schema import CreateTable
    from sqlalchemy.dialects import postgresql
    from backend.database import Base
    for table in Base.metadata.sorted_tables:
        statement = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        assert 'CREATE TABLE' in statement
