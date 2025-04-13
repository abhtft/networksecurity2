# EC2 Deployment Instructions

## Prerequisites
1. AWS Account with EC2 access
2. AWS CLI configured with appropriate credentials
3. SSH key pair for EC2 access

## Steps to Deploy

1. **Launch EC2 Instance**
   - Launch an EC2 instance (recommended: t2.medium or larger)
   - Use Ubuntu 20.04 LTS or later
   - Configure security group to allow inbound traffic on port 8000
   - Attach an IAM role with S3 access or configure AWS credentials

2. **Set Environment Variables**
   Before running the deployment script, set these environment variables:
   ```bash
   export MLFLOW_TRACKING_URI="your_mlflow_tracking_uri"
   export MLFLOW_TRACKING_USERNAME="your_mlflow_username"
   export MLFLOW_TRACKING_PASSWORD="your_mlflow_password"
   export AWS_ACCESS_KEY_ID="your_aws_access_key"
   export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
   export AWS_REGION="your_aws_region"
   ```

3. **Deploy Application**
   ```bash
   # Copy files to EC2
   scp -r ./* ubuntu@your-ec2-ip:/app/networksecurity/
   
   # SSH into EC2
   ssh ubuntu@your-ec2-ip
   
   # Make deploy script executable
   chmod +x deploy.sh
   
   # Run deployment script
   ./deploy.sh
   ```

4. **Verify Deployment**
   - Check if the application is running:
     ```bash
     ps aux | grep uvicorn
     ```
   - Check logs:
     ```bash
     tail -f app.log
     ```
   - Test the API:
     ```bash
     curl http://localhost:8000/health
     ```

5. **Access the Application**
   - The application will be available at: `http://your-ec2-ip:8000`
   - API documentation at: `http://your-ec2-ip:8000/docs`

## Monitoring
- Check application logs: `tail -f /app/networksecurity/app.log`
- Monitor system resources: `htop`
- Check MLflow tracking: Access your MLflow tracking server

## Troubleshooting
1. If the application fails to start:
   - Check logs: `cat app.log`
   - Verify environment variables: `cat .env`
   - Check port availability: `netstat -tuln | grep 8000`

2. If MLflow tracking fails:
   - Verify MLflow credentials
   - Check network connectivity to MLflow server
   - Verify MLflow server is running

3. If S3 access fails:
   - Verify AWS credentials
   - Check IAM permissions
   - Verify S3 bucket exists and is accessible 