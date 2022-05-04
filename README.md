# Python Cognito Proxy

# System Requirements
* Docker
* Docker Compose

# Building
```
USER_UID=`id -u` USER_GID=`id -g` docker-compose build
```

# Starting
```
USER_UID=`id -u` USER_GID=`id -g` docker-compose up
```

# Accessing the app container
```
USER_UID=`id -u` USER_GID=`id -g` docker-compose run pcp bash
```

# Updating packages
```
USER_UID=`id -u` USER_GID=`id -g` docker-compose run pcp bash
cd /pcp-app
/pcp-env/bin/pip install -r requirements.txt 
```
    
# Building Production Image
```shell
docker build -t pcp:latest -f containerize/Dockerfile-production .
``` 


# Sending Request For Testing
```python
import requests
# res = requests.post('http://localhost:6661/cognito', json={"email": "psampath@gomedigo.io", "orgid": "test"})

# Get digest of signed message
res = requests.post("http://localhost:6661/generate-hmac-signature", json={"email": "psampath@gomedigo.io", "orgid": "testorgid"})

# Get token
res = requests.post('http://localhost:6661/cognito', json={"email": "psampath@gomedigo.io", "orgid": "testorgid", "signed_email_orgid": "1cee122da0b4be246658024dc57f1959176585b59a261a024e91a3aa2130269b"})
```