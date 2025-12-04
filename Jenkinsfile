pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        S3_BUCKET = 'aishwarya-lambda-artifacts-2024'
        LAMBDA_ZIP = 'lambda_function.zip'
        TF_PATH = '/usr/local/bin'
        PATH = "$PATH:${TF_PATH}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'master', url: 'https://github.com/AishwaryaPawar149/serverless-crud-api.git'
            }
        }

        stage('Package Lambda') {
            steps {
                sh """
                    zip -r ${LAMBDA_ZIP} lambda_function.py
                """
            }
        }

        stage('Upload to S3') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'aws-credentials', 
                    usernameVariable: 'AWS_ACCESS_KEY_ID', 
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    sh """
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        aws s3 cp ${LAMBDA_ZIP} s3://${S3_BUCKET}/${LAMBDA_ZIP}
                    """
                }
            }
        }

        stage('Terraform Init') {
            steps {
                dir('terraform') {
                    withCredentials([usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )]) {
                        sh """
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            terraform init -input=false
                        """
                    }
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    withCredentials([usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )]) {
                        sh """
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            terraform plan -out=tfplan
                        """
                    }
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                dir('terraform') {
                    withCredentials([usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )]) {
                        sh """
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            terraform apply -auto-approve tfplan
                        """
                    }
                }
            }
        }

        stage('Retrieve API Endpoint') {
            steps {
                dir('terraform') {
                    script {
                        env.API_ENDPOINT = sh(
                            script: "terraform output -raw api_endpoint",
                            returnStdout: true
                        ).trim()

                        echo "=============================================="
                        echo "API Gateway URL: ${env.API_ENDPOINT}"
                        echo "=============================================="
                    }
                }
            }
        }

        stage('Test API') {
            steps {
                script {
                    echo "⏳ Waiting for API to warm up..."
                    sleep 20

                    sh """
                        echo "\n====== TESTING API ======\n"

                        echo "GET all items:"
                        curl -s -X GET ${API_ENDPOINT}/items || echo "GET failed"

                        echo "\nPOST item:"
                        curl -s -X POST ${API_ENDPOINT}/items -H "Content-Type: application/json" -d '{"id":"1","name":"Phone","price":500}' || echo "POST failed"

                        echo "\nGET created item:"
                        curl -s -X GET ${API_ENDPOINT}/items/1 || echo "GET failed"

                        echo "\nPUT update item:"
                        curl -s -X PUT ${API_ENDPOINT}/items/1 -H "Content-Type: application/json" -d '{"id":"1","name":"Updated Phone","price":750}' || echo "PUT failed"

                        echo "\nDELETE item:"
                        curl -s -X DELETE ${API_ENDPOINT}/items/1 || echo "DELETE failed"

                        echo "\n==========================="
                        echo "API Test Completed"
                        echo "===========================\n"
                    """
                }
            }
        }
    }

    post {
        success {
            echo "🚀 Deployment Successful!"
            echo "API Live At: ${API_ENDPOINT}"
        }
        failure {
            echo "❌ Deployment Failed — Check console logs"
        }
        always {
            cleanWs()
        }
    }
}
