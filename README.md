## Install python
https://www.python.org/downloads/    


## Python virtual environment
for Ubuntu users need to install python virtual env module  
used python3 instead of python because of using python of version 3  
```console
apt-get install python3-venv
```
</pre>
change director into visiodesk-gateway folder    
and create virtual env with name __venv__
```console
python3 -m venv venv
```
python environment should be activated (Windows)  
execute follow bat file
```console
visiodesk-gateway/venv/Scripts/activate.bat
```
python environment should be activated (Ubuntu)  
execute follow command
```console
cd /opt/visiodesk-gateway
source venv/bin/activate
```
after it terminal before input cursor should display __(venv)__  
add env variable (Windows) set PYTHONPATH=<visiodesk-gateway dir>  
add env variable (Ubuntu) export PYTHONPATH=<visiodesk-gateway dir>  
example set PYTHONPATH=C:\W\element\npp\visiodesk-gateway  
this is necessary for correct resolve modules search   
using pip freeze command to output current dependency list and it can be saved into txt file and used later for install all necessary dependencies
```console
pip freeze > requirements.txt
```
```console
pip install -r requirements.txt
```


## Create address cache by CLI
execute create_address_cache.py with optional --help to get full cli utility help    
<pre>
python ./create_address_cache.py --help
</pre>
example of usage (creating address_cache file)  
<pre>
python ./create_address_cache.py --devices 200,300
</pre>

## Bacnet stack emulation
available for windows uses (stored under __test_visiobas/__)  
copy __test_visiobas/bacrp.exe into vacbet-stack folder (depend on config/visiobas.py configuration)
prepare **address_cache** file with list of devices for data collect    
example of address_cache file stored here **test_visiobas/address_cache**

## Start data collector by CLI
./bacnet-stack folder should store bacnet apps for perform reading and writing bacnet properties  
execute data_collector.py with optional --help to get full cli help  
*data collector* use *address_cache* file for it own purpose  
only devices listed in address_cache used for collection  
configuration stored into config.visiobas.py module  
--single_thread 1 (using single thread instead of multi thread reads)    
```console
cd /opt/visiodesk-gateway
python ./data_collector.py
```

__Visiobas Gateway Server (VGS)__  
default protocol: __JSON-RPC 2.0__

Visiobas Gateway Server should store list of all objects working with.  
Each device object has own unique identifier, due to it VGS get all necessary information about protocols and others data  
  
__API header__  
***
Due to JSON-RPC 2.0 format any messages request and respond has to contain follow properties:
```json
{  
    "jsonrpc":"2.0",  
    "id": [number]  
}
```
__API Messages__
***
  
+ __Upload request device list__

Request
```json
{  
    "method":"upload_request_device_list",  
    "params": [{
        TODO describe request device list object
    }]  
}
```
Response  
<pre>
{
    "result": {
        TODO describe format of request device list
    }
}
</pre>

+ __Scan BACnet network__

Request
```json
{  
    "method": "scan_bacnet_network",
    "device_id": [number]  
}
```
Response
```json
{
    "result": {
        "data": [
            {
                "27": [string] description,
                "72": [number] object identifier,
                "74": [string] object reference,
                "351": [string] device identifier
            }
        ],
        "success": [boolean]
    }
}
```
+ __Reset set point__

Request
```json
{  
    "method": "reset_set_point",  
    "params": {  
        "object_id": [number],  
    }  
}
```
_object_id_ - unique object id totally identify certain object  
Response   
```json

{
    "result": {
        "success": [boolean]
    }
}
```

+ __Write set point__  

# Docker

To build docker use

```console
docker-compose build
```
