# covid19-engineering

# Experimentation
Look at the notebook

# SageMaker Training
This repo includes the dockerfile and code necessary to create a training image for this model 

## Core Components
Dockerfile - defines image creation steps 
`ml/code/train.py` - builds model and pushes .pkl to correct directory
`ml/code/predict.py` - (Not implemented) Is used to handle model predictions
`ml/input/config/hyperparameters.json`- default hyperparameters. Can be overridden in SM training job
Directory Structure in general

sagemaker-training library - provides entrypoint for the training image, and maps sagemaker functionality to the documented directory structure, and provides librarys that can be used within the training/predict scripts
https://github.com/aws/sagemaker-training-toolkit


## Building the Training Image
`docker build -f Dockerfile.train -t finesse/covid-naive-train:latest .`
`docker tag finesse/covid-naive-train:latest 125249736415.dkr.ecr.us-east-1.amazonaws.com/finesse/covid-naive-train:latest`

## Storing the Training Image
### Setup Temporary Local credentials
(skip if you already have a finesse profile set up with long lived credentials)
```
sed '/^\[default\]$/,$d' ~/.aws/credentials > ~/.aws/credentials.bak && mv ~/.aws/credentials.bak ~/.aws/credentials
aws sts assume-role --role-arn arn:aws:iam::125249736415:role/OrganizationAccountAccessRole --role-session-name devl --profile pariveda \
    | jq -r '.Credentials |
        "[default]",
        "aws_secret_access_key = \(.SecretAccessKey)",
        "aws_session_token = \(.SessionToken)",
        "aws_access_key_id = \(.AccessKeyId)"' \
    >> ~/.aws/credentials
```
### Autenticate to ECR
`aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 125249736415.dkr.ecr.us-east-1.amazonaws.com/finesse/covid-naive-train`
Note: This command requires the AWS CLI v2

### Push to ECR
`docker push 125249736415.dkr.ecr.us-east-1.amazonaws.com/finesse/covid-naive-train:latest`

## Running training sessions
### Using estimator API
run from jupyter notebook using estimator API

### Using Console
Kick off training job using console wizard

## Analysing training results
Need to work thorugh this. Looks like logs are outputted to cloudwatch. we can create regexes to identify metrics to record

# SageMaker Prediction
Not working on this yet. We can either build the functionality into a new image, or build a shared image that can handle both training/predicting

# Next Steps
- adapt this training process to work with other team's model
- deduplicate logic in train.py and notebook (consider running notebook w/ args to train model)
- create prediction image
- figure out metric recording
- update step functions pipeline to kick off training job
- POC versioning (S3 versioning, training job naming convention, other..)
- POC hyper parameter tuning
- Stretch: create cloudFormation template for algorithm
- Extreme stretch: create codepipeline to build/publish image & deploy CF resources
