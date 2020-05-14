from pathlib import Path

bacnet_stack_path = Path("bacnet-stack")
address_cache_path = bacnet_stack_path / "address_cache"

visiobas_slicer = {
    "bacrp": (bacnet_stack_path / "bacrp").absolute(),
    "bacrpm": (bacnet_stack_path / "bacrpm").absolute(),
    "read_timeout": 5
}

notifier = {
    "recipient_list": [{"recipient": "VisioBAS", "transitions": [False, True, False]}],
    "event_messages": ["", "Возможно точка не исправна", "", "", "Восстановленна работа"]
}

__local = {
    'host': 'http://localhost',
    'port': 8080,
    'ssl_verify': False,
    'auth': {
        'user': 'visiobas',
        'pwd': '814E284BF1B02CC2BEB58A587F5FD8DA'
    }
}

__mria = {
    'host': 'http://10.21.171.11',
    'port': 8080,
    'ssl_verify': False,
    'auth': {
        'user': 'canio',
        'pwd': '278D1DE033A395FE9A2AA9E1D07416D8'
    }
}

visiobas_server = __mria
