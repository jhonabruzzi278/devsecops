// Jenkinsfile - Pipeline de "Sistema Alumnos" (SecureDev · Evaluación Parcial 3 · OCY1102)
//
// Esta es la versión BASE: construye, prueba y despliega en producción.
// En la guía reemplazarás los marcadores  >>> [ETIQUETA]  por las etapas de seguridad.
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 40, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    // Revisa GitHub cada ~3 minutos: cada push (tuyo o un PR de Dependabot fusionado) dispara un build.
    triggers {
        pollSCM('H/3 * * * *')
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Build') {
            steps {
                script {
                    // Versión = 1.0.<nº de build>+<commit corto>: une cada despliegue con su commit (trazabilidad)
                    def sha = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    env.APP_VERSION = "1.0.${env.BUILD_NUMBER}+${sha}"
                }
                echo "Versión de este build: ${env.APP_VERSION}"
                sh 'git log -1 --format="Commit %h de %an: %s"'
                // Cada build parte limpio: sin reportes viejos y con un entorno virtual nuevo
                sh 'rm -rf .venv reports && mkdir -p reports'
                sh 'python3 -m venv .venv'
                sh '.venv/bin/pip install --quiet -r requirements.txt -r requirements-dev.txt'
                sh '.venv/bin/python -m compileall -q app.py'
            }
        }

        stage('Test') {
            steps {
                sh '.venv/bin/python -m pytest --junitxml=reports/junit.xml'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Security Review (SAST)') {
            steps {
                // Si Bandit encuentra algo Medium o High, el build queda UNSTABLE (amarillo) y sigue.
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh '''
                        bandit app.py -f json -o reports/bandit.json --exit-zero -q
                        bandit app.py -f txt  -o reports/bandit.txt  --exit-zero -q
                        cat reports/bandit.txt
                        bandit app.py -ll -q
                    '''
                }
            }
        }

        stage('Dependency Management') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh '''
                        estado=0
                        echo "== pip-audit: vulnerabilidades conocidas (CVE) en requirements.txt"
                        pip-audit -r requirements.txt -f json -o reports/pip-audit.json || true
                        pip-audit -r requirements.txt > reports/pip-audit.txt 2>&1 || estado=1
                        cat reports/pip-audit.txt
                        echo "== Dependencias desactualizadas (informativo)"
                        .venv/bin/pip list --outdated | tee reports/dependencias-desactualizadas.txt
                        echo "== Política: Dependabot debe vigilar las dependencias pip"
                        if grep -Eqs 'package-ecosystem: *"?pip"?' .github/dependabot.yml; then
                            echo "OK: .github/dependabot.yml vigila pip"
                        else
                            echo "FALTA .github/dependabot.yml con package-ecosystem pip"; estado=1
                        fi
                        exit $estado
                    '''
                }
            }
        }

        stage('Deploy Staging') {
            steps {
                sh 'bash scripts/deploy.sh staging 5001'
            }
        }

        stage('DAST - OWASP ZAP') {
            steps {
                // ZAP ataca staging (no producción). Alertas High o Medium = UNSTABLE.
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh 'python3 scripts/zap_scan.py http://jenkins:5001'
                }
            }
        }

        stage('Deploy Producción') {
            // Gate de seguridad: solo llega a producción un build sin hallazgos (SUCCESS).
            when { expression { currentBuild.currentResult == 'SUCCESS' } }
            steps {
                sh 'bash scripts/deploy.sh produccion 5000'
                script { env.PRODUCCION = env.APP_VERSION }
            }
        }
    }

    post {
        always {
            // Registro de trazabilidad: build <-> versión <-> commit <-> pruebas <-> hallazgos <-> despliegue
            withEnv(["RESULTADO=${currentBuild.currentResult}"]) {
                sh 'python3 scripts/trazabilidad.py'
            }
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
