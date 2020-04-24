This is the location that Sagemaker will use to drop dta files for training.
These files are configured via the `/opt/ml/input/config/inputdataconfig.json` file. 

In our case, we're reading data from github directly, which means we don't require sageMaker to fetch data for us. Likewise, if we choose to consume training data from Athena this may not be necessary. However the tool is available, and we may consider to use it at a later date