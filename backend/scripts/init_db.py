"""数据库初始化脚本
用法：python scripts/init_db.py
功能：读取 .env → 连接 MySQL → 执行 4 个 part SQL 文件 → 验证 15 张表 + 种子数据
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from dotenv import load_dotenv

load_dotenv(BACKEND_ROOT / ".env")

import pymysql

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "450881"),
    "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
    "autocommit": False,
}

DB_NAME = os.getenv("MYSQL_DB", "campus_forum")
SCRIPTS_DIR = BACKEND_ROOT / "scripts"

EXPECTED_TABLES = [
    "pf_schools", "pf_users", "pf_anonymous_id_mapping", "pf_boards",
    "pf_posts", "pf_comments", "pf_likes", "pf_favorites", "pf_follows",
    "pf_reports", "pf_notifications", "pf_user_sessions",
    "pf_anonymous_letters", "pf_sensitive_words", "pf_audit_logs",
]


def split_sql_statements(sql_content: str) -> list[str]:
    """按分号拆分 SQL 文件为单条语句（跳过纯注释行）"""
    statements: list[str] = []
    current: list[str] = []
    for line in sql_content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt and stmt != ";":
                stmt = stmt.rstrip(";").strip()
                if stmt:
                    statements.append(stmt)
            current = []
    if current:
        stmt = "\n".join(current).strip()
        if stmt:
            statements.append(stmt)
    return statements


def execute_sql_file(cursor, sql_file: Path) -> int:
    """执行 SQL 文件并返回语句数"""
    print(f"   ├─ 执行: {sql_file.name}")
    content = sql_file.read_text(encoding="utf-8")
    statements = split_sql_statements(content)

    count = 0
    for stmt in statements:
        upper = stmt.upper().strip()
        if upper.startswith("SOURCE "):
            continue
        if upper.startswith("USE "):
            cursor.execute(stmt)
            count += 1
            continue
        try:
            cursor.execute(stmt)
            count += 1
        except pymysql.err.OperationalError as e:
            if "SOURCE" in stmt.upper() or "1064" in str(e):
                continue
            raise
    return count


def main() -> int:
    print()
    print("=" * 60)
    print("  校园树洞 - 数据库初始化")
    print("=" * 60)
    print()
    print(f"   Host:     {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   User:     {DB_CONFIG['user']}")
    print(f"   Database: {DB_NAME}")
    print()

    print("连接 MySQL...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
    except pymysql.err.OperationalError as e:
        print(f"连接失败: {e}")
        print("   请检查 MySQL 是否启动，账号密码是否正确")
        return 1
    print("   连接成功")
    print()

    try:
        with conn.cursor() as cursor:
            print("创建数据库（如不存在）...")
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
            print(f"   OK 数据库 {DB_NAME} 就绪")
            print()

            print("执行建表脚本...")
            for i in range(1, 5):
                sql_file = SCRIPTS_DIR / f"init_db_part{i}.sql"
                if not sql_file.exists():
                    print(f"   文件不存在: {sql_file}")
                    return 1
                count = execute_sql_file(cursor, sql_file)
                print(f"   │  └─ {count} 条语句执行")
            conn.commit()
            print("   建表完成")
            print()

            print("验证数据库表...")
            cursor.execute(f"USE `{DB_NAME}`")
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   当前表: {len(tables)} 张")
            for t in tables:
                mark = "✓" if t in EXPECTED_TABLES else "?"
                print(f"   │  {mark} {t}")

            missing = set(EXPECTED_TABLES) - set(tables)
            if missing:
                print(f"   缺少表: {missing}")
                return 1
            print("   全部 15 张表已创建")
            print()

            print("验证种子数据...")
            cursor.execute("SELECT COUNT(*) FROM pf_schools")
            school_count = cursor.fetchone()[0]
            print(f"   │  学校数: {school_count}")

            cursor.execute("SELECT COUNT(*) FROM pf_boards")
            board_count = cursor.fetchone()[0]
            print(f"   │  板块数: {board_count}")

            cursor.execute("SELECT COUNT(*) FROM pf_users")
            user_count = cursor.fetchone()[0]
            print(f"   │  用户数: {user_count}")

            cursor.execute("SELECT COUNT(*) FROM pf_anonymous_id_mapping")
            anon_count = cursor.fetchone()[0]
            print(f"   │  匿名马甲: {anon_count}")

            cursor.execute("SELECT COUNT(*) FROM pf_sensitive_words")
            word_count = cursor.fetchone()[0]
            print(f"   │  敏感词: {word_count}")
            print()

            print("=" * 60)
            print(f"  OK {len(tables)} tables created, {school_count} school, "
                  f"{board_count} boards, {user_count} admin+audit users")
            print("=" * 60)
            print()
            print("数据库初始化完成！")
            print()
            print("下一步:")
            print("   1. 启动后端: python run.py")
            print("   2. 测试 API: curl http://localhost:5000/api/health")
            print()

            return 0
    except Exception as e:
        print(f"执行出错: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
