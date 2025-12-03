pipeline {
    agent any
    
    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        S3_BUCKET = 'my-lambda-artifacts-unique-12345'  // Same as terraform.tfvars
        LAMBDA_ZIP = 'lambda_function.zip'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Package Lambda') {
            steps {
                sh '''
                    cd ${WORKSPACE}
                    zip -r ${LAMBDA_ZIP} lambda_function.py
                '''
            }
        }
        
        stage('Upload to S3') {
            steps {
                sh '''
                    aws s3 cp ${LAMBDA_ZIP} s3://${S3_BUCKET}/${LAMBDA_ZIP}
                '''
            }
        }
        
        stage('Terraform Init') {
            steps {
                dir('terraform') {
                    sh 'terraform init'
                }
            }
        }
        
        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    sh 'terraform plan -out=tfplan'
                }
            }
        }
        
        stage('Terraform Apply') {
            steps {
                dir('terraform') {
                    sh 'terraform apply -auto-approve tfplan'
                }
            }
        }
        
        stage('Get API Endpoint') {
            steps {
                dir('terraform') {
                    script {
                        env.API_ENDPOINT = sh(
                            script: 'terraform output -raw api_endpoint',
                            returnStdout: true
                        ).trim()
                        echo "API Endpoint: ${env.API_ENDPOINT}"
                    }
                }
            }
        }
        
        stage('Test API') {
            steps {
                sh '''
                    # Wait for API to be ready
                    sleep 10
                    
                    # Test GET (list items)
                    echo "Testing GET /items..."
                    curl -X GET ${API_ENDPOINT}/items
                    
                    # Test POST (create item)
                    echo "\nTesting POST /items..."
                    curl -X POST ${API_ENDPOINT}/items \
                        -H "Content-Type: application/json" \
                        -d '{"id":"1","name":"Test Item","price":100}'
                    
                    # Test GET single item
                    echo "\nTesting GET /items/1..."
                    curl -X GET ${API_ENDPOINT}/items/1
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
