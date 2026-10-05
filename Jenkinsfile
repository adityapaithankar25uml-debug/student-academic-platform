pipeline {
    agent any

    environment {
        PYTHON = '/home/aditya12/.pyenv/versions/3.11.17/bin/python3.11'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment') {
            steps {
                sh '''
                    $PYTHON -m venv .jenkins-venv
                    . .jenkins-venv/bin/activate
                    python --version
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .jenkins-venv/bin/activate
                    flake8 app database tests run.py
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .jenkins-venv/bin/activate
                    pytest -v
                '''
            }
        }
    }

    post {
        always {
            echo 'CI pipeline completed.'
        }

        success {
            echo 'All checks passed successfully.'
        }

        failure {
            echo 'CI pipeline failed. Check the stage logs above.'
        }
    }
}
