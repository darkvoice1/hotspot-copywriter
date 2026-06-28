from app.db.init_db import init_db


def test_init_db_returns_expected_tables() -> None:
    """验证数据库初始化后返回预期表名。"""
    table_names = init_db()

    assert table_names == ["collector_runs", "raw_hotspots", "standard_hotspots"]
