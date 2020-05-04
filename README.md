__Python virtual environment__
<pre>  
python -m venv visiodesk-gateway/venv
</pre>
python environment should be activated
<pre>
visiodesk-gateway/venv/Scripts/activate.bat
</pre>
using pip freeze command to output current dependency list and it can be saved into txt file and used later for install all necessary dependencies
<pre>
pip freeze > dependencies.txt
</pre>
<pre>
pip install -r dependencies.txt
</pre>


__Create address cache by CLI__  
execute create_address_cache.py with optional --help to get full cli utility help    
<pre>
python ./create_address_cache.py --help
</pre>
example of usage (creating address_cache file)  
<pre>
python ./create_address_cache.py --devices 200,300
</pre>


__Visiobas Gateway Server (VGS)__  
default protocol: __JSON-RPC 2.0__

Visiobas Gateway Server should store list of all objects working with.  
Each device object has own unique identifier, due to it VGS get all necessary information about protocols and others data  
  
__API header__  
***
Due to JSON-RPC 2.0 format any messages request and respond has to contain follow properties:
<pre>
{  
    "jsonrpc":"2.0",  
    "id": [number]  
}
</pre>
__API Messages__
***
  
+ __Upload request device list__

Request
<pre>  
{  
    "method":"upload_request_device_list",  
    "params": [{
        TODO describe request device list object
    }]  
}
</pre>
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
<pre>
{  
    "method": "scan_bacnet_network",
    "device_id": [number]  
}
</pre>
Response
<pre>
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
</pre>

+ __Reset set point__

Request
<pre>
{  
    "method": "reset_set_point",  
    "params": {  
        "object_id": [number],  
    }  
}
</pre>
_object_id_ - unique object id totally identify certain object  
Response   
<pre>
{
    "result": {
        "success": [boolean]
    }
}
</pre>

+ __Write set point__  