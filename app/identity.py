import re

HEX_ADDRESS = re.compile(r"\b0x[0-9a-fA-F]+\b")
UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def normalize_name(name: str) -> str:
    name = UUID.sub("<uuid>", name)
    name = HEX_ADDRESS.sub("0x?", name)
    return name.strip()


def make_test_id(classname:str, name: str) -> str:
    return f"{classname}::{normalize_name(name)}"