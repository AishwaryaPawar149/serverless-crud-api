pipeline {
    agent any
    
    environment {
        PATH = "/usr/local/bin:${env.PATH}"  // Ensure Terraform is found
        AWS_DEFAULT_REGION = 'ap-south-1'
        S3_BUCKET = 'aishwarya-lambda-artifacts-2024'  // Make sure this bucket exists
        LAMBDA_ZIP = 'lambda_function.zip'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                    sudo apt update
                    sudo apt install -y zip curl unzip
                '''
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
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials', 
                        usernameVariable: 'AWS_ACCESS_KEY_ID', 
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    sh '''
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        aws s3 cp ${LAMBDA_ZIP} s3://${S3_BUCKET}/${LAMBDA_ZIP}
                    '''
                }
            }
        }
        
        stage('Terraform Init') {
            steps {
                dir('terraform') {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'aws-credentials', 
                            usernameVariable: 'AWS_ACCESS_KEY_ID', 
                            passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                        )
                    ]) {
                        sh '''
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            terraform init
                        '''
                    }
                }
            }
        }
        
        stage('Terraform Plan') {
            steps {
                dir('terraform') {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'aws-credentials', 
                            usernameVariable: 'AWS_ACCESS_KEY_ID', 
                            passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                        )
                    ]) {
                        sh '''
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            terraform plan -out=tfplan
                        '''
                    }
                }
            }
        }
        
        stage('Terraform Apply') {
            steps {
                dir('terraform') {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'aws-credentials', 
                            usernameVariable: 'AWS_ACCESS_KEY_ID', 
                            passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                        )
                    ]) {
                        sh '''
                            export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                            export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                            terraform apply -auto-approve tfplan
                        '''
                    }
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
                        echo "=========================================="
                        echo "API Endpoint: ${env.API_ENDPOINT}"
                        echo "=========================================="
                    }
                }
            }
        }
        
        stage('Test API') {
            steps {
                sh '''
                    echo "Waiting for API to be ready..."
                    sleep 15
                    
                    echo "\n========== Testing GET /items (List all) =========="
                    curl -s -X GET ${API_ENDPOINT}/items || echo "Failed"
                    
                    echo "\n\n========== Testing POST /items (Create item) =========="
                    curl -s -X POST ${API_ENDPOINT}/items \
                        -H "Content-Type: application/json" \
                        -d '{"id":"1","name":"Test Item","price":100}' || echo "Failed"
                    
                    echo "\n\n========== Testing GET /items/1 (Get single item) =========="
                    curl -s -X GET ${API_ENDPOINT}/items/1 || echo "Failed"
                    
                    echo "\n\n========== Testing PUT /items/1 (Update item) =========="
                    curl -s -X PUT ${API_ENDPOINT}/items/1 \
                        -H "Content-Type: application/json" \
                        -d '{"id":"1","name":"Updated Item","price":200}' || echo "Failed"
                    
                    echo "\n\n========== Testing DELETE /items/1 (Delete item) =========="
                    curl -s -X DELETE ${API_ENDPOINT}/items/1 || echo "Failed"
                    
                    echo "\n\n========== API Testing Complete =========="
                '''
            }
        }
    }
    
    post {
        success {
            echo '==========================================' 
            echo 'Deployment Successful! ✅'
            echo 'API Endpoint: Check the "Get API Endpoint" stage'
            echo '=========================================='
        }
        failure {
            echo '==========================================' 
            echo 'Deployment Failed! ❌'
            echo 'Check the console output for errors'
            echo '=========================================='
        }
        always {
            cleanWs()
        }
    }
}
