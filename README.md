# Sistema Alumnos · SecureDev

API y portal web (Flask) de la **Evaluación Parcial 3 de OCY1102 – Ciberseguridad en desarrollo**.
Sobre este código, **que es vulnerable a propósito**, construyes un pipeline seguro en Jenkins:
pruebas, análisis estático, dependencias, OWASP ZAP, despliegue protegido, monitoreo en Grafana y trazabilidad.

> Sigue la **GUIA_EXAMEN_EV3.html**. Este repositorio es solo el punto de partida.

## Rutas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Portada con enlaces y formularios |
| GET | `/hello?name=Ana` | Saludo |
| GET | `/alumnos` · `/alumnos/<id>` | Listado y detalle de alumnos |
| GET | `/alumnos/buscar?nombre=Ana` | Búsqueda por nombre |
| POST | `/login` | Acceso del administrador (formulario) |
| GET | `/health` · `/version` | Estado y versión desplegada |
| GET | `/metrics` | Métricas para Prometheus (no cambies sus nombres) |

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `app.py` | Aplicación (contiene vulnerabilidades que debes encontrar y corregir) |
| `tests/` | Pruebas funcionales (pytest). Deben seguir pasando después de corregir |
| `requirements.txt` | Dependencias de ejecución (antiguas a propósito) |
| `requirements-dev.txt` | Dependencias solo de pruebas |
| `Jenkinsfile` | Pipeline base: Build → Test → Deploy Producción. La guía indica qué agregar |
| `scripts/deploy.sh` | Despliega en `staging` (5001) o `produccion` (5000) y hace prueba de humo |
| `scripts/zap_scan.py` | Escaneo DAST con OWASP ZAP (spider, pasivo y activo) |
| `scripts/trazabilidad.py` | Registro build ↔ versión ↔ commit ↔ hallazgos ↔ despliegue |
| `scripts/revisar_local.sh` | Pruebas + Bandit + pip-audit en el contenedor taller, antes del push |
| `scripts/simular_ataque.py` | Ataque de prueba para ver incidentes en Grafana (solo en este laboratorio) |
| `docs/REGISTRO_SEGURIDAD.md` | Tu registro de revisiones, vulnerabilidades, incidentes y dependencias |

## Convención de commits (trazabilidad)

Cada corrección va en su propio commit y empieza con el identificador del hallazgo:
`VULN-02: consulta parametrizada en /alumnos/buscar`. Así cada build del registro de
trazabilidad se puede seguir hasta el hallazgo que corrigió.
