from pathlib import Path

bacnet_stack_path = Path("test_visiobas")
bacrmp_app_path = bacnet_stack_path / "bacrpm.cmd"
address_cache_path = bacnet_stack_path / "resource" / "address_cache"

visiobas_server = {
    'host': 'http://localhost',
    'port': 8080,
    'ssl_verify': False,
    'auth': {
        'user': 's.gubarev',
        'pwd': '22a4d9b04fe95c9893b41e2fde83a427'
    }
}
