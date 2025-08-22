# cocoa-truffle
Simple API for solving hanoi tower problems

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

If you want to run the tests do as follows
```shell
   python3 tests.py
```

If you want to run the app in local, pls run
```shell
   python3 app.py
```

## Deploy
This would be automatically deployed through a CICD Pipeline to Digital Ocean.

But the docker image build can be used to other clouds and we can extend the instances for request burst.