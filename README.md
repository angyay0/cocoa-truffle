# cocoa-truffle
Simple API for solving hanoi tower problems

This works using two algorithms for two approaches within the same endpoint
- Classic (2n and 2n-1): This will sove using an iterative instead of doing by recursive mechanism to save cpu resources and handle more resquests.
- Frame-Stewart (2n-1): This will solve using the most consistent algorithm fo N Poles and N Disks, is using an Oracle to understand the moves required per iteration calling the method in recursive mode at movements.

## API
This API contains a single endpoint to resolve hanoi problem

### ENDPONT
This is a simple with 4 params
- Disks number
- Source pole, from where it would be moved
- Destination pole, where the disc would end
- Auxiliar pole, to support movements

``` shell
   POST <BASE_URL>/api/hanoi TYPE application/json
   BODY 
   {
      size: 3,
      src: 1,
      dst: 3,
      aux: 2
   }
```
CURL:
```shell
   curl -X POST http://127.0.0.1:8000/api/hanoi -H 'Content-Type: application/json' -d '{"size":3,"k":3}'
```

## How to test
To have clean setup, please create an environment to handle the requirements
```shell
   python3 -m venv env
```

Activate with one of the following according to the OS
```shell
   source env/bin/activate #Linux
   .\env\Scripts\activate.bat #windows cmd
   .\env\Scripts\Activate.ps1 #windows powershell
```

Then install deps
```shell
   pip install --no-cache-dir -r requirements.txt
```

First run the app in local
```shell
   python3 app.py
```

If you want to run the tests do as follows
```shell
   python3 tests.py
   python3 tests_k_algorithm.py
```

## Deploy
This would be automatically deployed through a **CICD Pipeline to Digital Ocean**.

But the docker image build can be used to other clouds and we can extend the instances for request burst.

### Build Docker Image
The docker image can be done and tests automatically executed by running the deploy-docker-local.sh script.But here are the steps separately.

```shell
   # define image name and max moves for not a super huge payload
   export IMAGE_NAME=my-api
   export MAX_N_ENV=14 # Default as same in the code
   # build
   docker build -t "${IMAGE_NAME}:latest" .
   # run
   docker run -d --name "${IMAGE_NAME}" -p "${PORT}:8000" \
   -e PORT=8000 \
   -e MAX_N="${MAX_N_ENV}" \
   "${IMAGE_NAME}:latest"
```