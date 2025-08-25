import sys, types

# bikin modul palsu biar python-telegram-bot lama tetap jalan
module_code = """def what(file, h=None):
    return None
"""
fake_imghdr = types.ModuleType("imghdr")
exec(module_code, fake_imghdr.__dict__)
sys.modules["imghdr"] = fake_imghdr
