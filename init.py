#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join, dirname, abspath
import sys
from argparse import ArgumentParser

from scr import helper as fn

dir_script = abspath(dirname(__file__))
os.chdir(dir_script)
file_env = join(dir_script, ".env")

def main():
    """
    initialize container
    """
    if not fn.input_yn("initialize container? (y/*) :"):
        print("[info] initialize canceled.")
        sys.exit()

    params = fn.getenv(file_env)
    host = fn.local_ip()
    if not args.url is None:
        host = args.url

    # コンテナ削除
    cmd="docker-compose down"
    if fn.input_yn("initialize volumes? (y/*) :"):
        cmd="docker-compose down -v"
    for line in fn.cmd_lines(_cmd=cmd):
        sys.stdout.write(line)

    # conf置き換え
    fn.update_file({"SERVER_NAME": host},
            join(dir_script, 'org', 'pleasanter.conf'),
            '___',
            join(dir_script, 'pleasanter', 'pleasanter.conf'))

    # イメージリビルド
    container_base = "pls-base"
    cmd=f"docker-compose up -d"
    if fn.input_yn("rebuild image? (y/*) :"):

        for line in fn.cmd_lines(_cmd=f"docker rmi pleasanter_{params['DISTRIBUTION']}"):
            sys.stdout.write(line)
        for line in fn.cmd_lines(_cmd="docker-compose build", _encode='utf-8'):
            sys.stdout.write(line)

    # コンテナ作成
    if fn.input_yn("make container? (y/*) :"):
        for line in fn.cmd_lines(_cmd="docker-compose up -d", _encode='utf-8'):
            sys.stdout.write(line)
    else:
        print("[info] container make canceled.")
        sys.exit()

    # Rds.json置き換え
    rds_org = join(dir_script, 'org', 'Rds.json')
    rds_dst = join(dir_script, 'pleasanter', 'Rds.json')
    fn.update_file(params, rds_org, '___', rds_dst)
    # Rds.json転送
    cmd = f'docker cp {rds_dst} {container_base}:/web/pleasanter/Implem.Pleasanter/App_Data/Parameters'
    for line in fn.cmd_lines(_cmd=cmd, _encode='utf-8'):
        sys.stdout.write(line)

    docker_cmd = f"docker exec -it {container_base}"

    # pleasanterデータベース構築
    cmd = f'{docker_cmd} dotnet /web/pleasanter/Implem.CodeDefiner/Implem.CodeDefiner.NetCore.dll _rds'
    for line in fn.cmd_lines(_cmd=cmd, _encode='utf-8'):
        sys.stdout.write(line)

    # pleasanterサービス起動
    cmds = [
            f'{docker_cmd} bash -c "systemctl daemon-reload"',
            f'{docker_cmd} bash -c "systemctl enable pleasanter"',
            f'{docker_cmd} bash -c "systemctl start pleasanter"',
            ]
    for line in fn.cmd_lines(_cmd=cmds, _encode='utf-8', _split=False):
        sys.stdout.write(line)

    # nginxサービス起動
    cmds = [
            f'{docker_cmd} bash -c "systemctl enable nginx"',
            f'{docker_cmd} bash -c "systemctl start nginx"',
            ]
    for line in fn.cmd_lines(_cmd=cmds, _encode='utf-8', _split=False):
        sys.stdout.write(line)

    print(f"""
[info] pleasanter started. access to follow url.
http://{host}:{params['PLS_PORT']}/users/login
""")


if __name__ == "__main__":
    parser = ArgumentParser(description='init container.')
    parser.add_argument('--url', '-u', help="(option) force hosturl.", type=str)
    args = parser.parse_args()

    print("[info] initialize start.")
    main()
    print("[info] initialize end.")
