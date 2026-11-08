from app.identity import make_test_id, normalize_name


def test_plain_name_is_unchanged():
    assert normalize_name("test_login_ok") == "test_login_ok"


def test_memory_address_is_replaced():
    name = "test_save[<Item object at 0x7f3a1c2b>]"
    assert normalize_name(name) == "test_save[<Item object at 0x?>]"


def test_same_test_gets_same_id_across_runs():
    run1 = make_test_id("tests.test_db", "test_save[<Item object at 0x7f3a1c2b>]")
    run2 = make_test_id("tests.test_db", "test_save[<Item object at 0x55d0e4f1>]")
    assert run1 == run2


def test_uuid_is_replaced():
    name = "test_fetch[3f2504e0-4f89-41d3-9a0c-0305e82c3301]"
    assert normalize_name(name) =="test_fetch[<uuid>]"


def test_numbers_like_10x5_are_not_touched():
    assert normalize_name("test_multiply[10x5]") == "test_multiply[10x5]"


def test_different_tests_keep_different_ids():
    first = make_test_id("tests.test_a", "test_one")
    second = make_test_id("tests.test_a", "test_two")
    assert first != second