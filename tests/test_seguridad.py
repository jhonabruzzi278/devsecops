"""Pruebas de regresión de seguridad: fallan si vuelve alguna vulnerabilidad corregida."""
import re

import pytest

import app as modulo_app


@pytest.fixture
def client():
    modulo_app.app.config["TESTING"] = True
    modulo_app._fallos_por_ip.clear()
    with modulo_app.app.test_client() as c:
        yield c


def _token(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/").get_data(as_text=True)).group(1)


def test_vuln01_xss_escapado(client):
    r = client.get("/hello?name=<script>alert(1)</script>")
    assert "<script>" not in r.get_data(as_text=True)


def test_vuln02_sqli_no_devuelve_datos_internos(client):
    r = client.get("/alumnos/buscar?nombre=zzz' UNION SELECT 0, name, sql, 0 FROM sqlite_master --")
    assert r.status_code == 200
    assert r.get_json() == []


def test_vuln03_04_sin_secretos_ni_md5_en_el_codigo():
    codigo = open(modulo_app.__file__, encoding="utf-8").read()
    assert "md5" not in codigo.lower()
    assert "clave-super-secreta" not in codigo


def test_vuln06_cabeceras_de_seguridad(client):
    h = client.get("/").headers
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"]
    assert h["X-Frame-Options"] == "DENY"
    assert h["X-Content-Type-Options"] == "nosniff"


def test_vuln07_login_sin_token_csrf_es_rechazado(client):
    assert client.post("/login", data={"usuario": "admin", "clave": "x"}).status_code == 400


def test_vuln08_fuerza_bruta_bloquea_la_ip(client):
    token = _token(client)
    codigos = [client.post("/login", data={"usuario": "admin", "clave": f"c{i}", "csrf_token": token}).status_code
               for i in range(7)]
    assert codigos[:5] == [401] * 5
    assert codigos[5:] == [429, 429]
