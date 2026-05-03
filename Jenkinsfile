pipeline {
    agent any

    environment {
        APP_NAME = 'predictive-maintenance-api'
        AWS_REGION = credentials('aws-region')
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        ECR_REPOSITORY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DEPLOY_HOST = credentials('deploy-host')
        DEPLOY_USER = credentials('deploy-user')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${APP_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker run --rm ${APP_NAME}:${IMAGE_TAG} pytest'
            }
        }

        stage('Push to Registry') {
            steps {
                sh '''
                    aws ecr describe-repositories --repository-names ${APP_NAME} --region ${AWS_REGION} || \
                    aws ecr create-repository --repository-name ${APP_NAME} --region ${AWS_REGION}

                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

                    docker tag ${APP_NAME}:${IMAGE_TAG} ${ECR_REPOSITORY}:${IMAGE_TAG}
                    docker tag ${APP_NAME}:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
                    docker push ${ECR_REPOSITORY}:${IMAGE_TAG}
                    docker push ${ECR_REPOSITORY}:latest
                '''
            }
        }

        stage('Deploy to Server') {
            steps {
                sshagent(credentials: ['deploy-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} "
                            aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com &&
                            docker pull ${ECR_REPOSITORY}:latest &&
                            docker stop ${APP_NAME} || true &&
                            docker rm ${APP_NAME} || true &&
                            docker run -d --name ${APP_NAME} --restart unless-stopped -p 8000:8000 ${ECR_REPOSITORY}:latest
                        "
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f'
        }
    }
}

