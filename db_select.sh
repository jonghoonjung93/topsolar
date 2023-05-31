#!/bin/bash

# SQLite 데이터베이스 파일 경로
db_file="topsolar.sqlite3"

# SQLite 쿼리문
query1="SELECT * FROM power_gen_day;"
query2="SELECT * FROM power_gen_month;"

# SQLite 쿼리 실행
echo "= $query1 ======================================================"
sqlite3 "$db_file" "$query1"
echo "= $query2 ======================================================"
sqlite3 "$db_file" "$query2"
