from pathlib import Path

bacnet_stack_path = Path("/W/element/npp/visiodesk-gateway/test_visiobas")
address_cache_path = bacnet_stack_path / "resource" / "address_cache"

visiobas_slicer = {
    "bacrp": bacnet_stack_path / "bacrp",
    "bacrpm": bacnet_stack_path / "bacrpm"
}

visiobas_server = {
    'host': 'http://localhost',
    'port': 8080,
    'ssl_verify': False,
    'auth': {
        'user': 'visiobas',
        'pwd': '814E284BF1B02CC2BEB58A587F5FD8DA'
    }
}
