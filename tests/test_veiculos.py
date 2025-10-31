import pytest
from unittest.mock import patch


def auth_header():
    # Valor dummy; a verificação real será mockada nos testes
    return {"Authorization": "Bearer test-token"}


def test_login_success(client):
    with patch("servidor.authenticate", return_value=({"token": "abc"}, 200)):
        resp = client.post("/login", json={"username": "u", "password": "p"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["token"] == "abc"


def test_api_requires_auth(client):
    resp = client.get("/api/veiculos")
    assert resp.status_code == 401


def test_get_veiculos_ok(client):
    fake_list = [{"_id": "1", "modelo": "Yaris"}]
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.get_all", return_value=fake_list):
        resp = client.get("/api/veiculos", headers=auth_header())
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert data[0]["modelo"] == "Yaris"


def test_get_veiculo_by_id_found(client):
    item = {"_id": "1", "modelo": "Yaris"}
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.get_by_id", return_value=item):
        resp = client.get("/api/veiculos/1", headers=auth_header())
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["modelo"] == "Yaris"


def test_get_veiculo_by_id_not_found(client):
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.get_by_id", return_value=None):
        resp = client.get("/api/veiculos/nao_existe", headers=auth_header())
        assert resp.status_code == 404


def test_create_veiculo_ok(client):
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.insert_veiculo", return_value=({"message": "ok"}, 201)):
        resp = client.post("/api/veiculos", json={"modelo": "Novo"}, headers=auth_header())
        assert resp.status_code == 201


def test_update_veiculo_ok(client):
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.update_veiculo", return_value=({"message": "atualizado"}, 200)):
        resp = client.put("/api/veiculos/1", json={"modelo": "Editado"}, headers=auth_header())
        assert resp.status_code == 200


def test_delete_veiculo_ok(client):
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.remove_veiculo", return_value=({"message": "removido"}, 200)):
        resp = client.delete("/api/veiculos/1", headers=auth_header())
        assert resp.status_code == 200


def test_recomendacao_ok(client):
    with patch("servidor.verify_token", return_value=({"valid": True}, 200)), \
         patch("servidor.recomendacao_veiculo", return_value=({"recomendacao": "OK"}, 200)):
        resp = client.post("/api/recomendacao", json={"texto": "quero um suv"}, headers=auth_header())
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get("recomendacao") == "OK"


def test_recomendacao_requires_auth(client):
    resp = client.post("/api/recomendacao", json={"texto": "quero um suv"})
    assert resp.status_code == 401


def test_login_accessible_without_auth(client):
    with patch("servidor.authenticate", return_value=({"error": "Credenciais inválidas"}, 401)):
        resp = client.post("/login", json={"username": "u", "password": "p"})
        # Mesmo com erro, deve ser acessível (não 401 por falta de token)
        assert resp.status_code == 401
        assert "error" in resp.get_json()


