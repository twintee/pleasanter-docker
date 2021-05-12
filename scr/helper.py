#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import join, dirname, isfile, isdir, abspath, exists
import sys
import json
import time
import shutil
from datetime import datetime as dt
import string
import random
import subprocess
import socket

def input_yn(_txt):
    _input = input(_txt).lower()
    if _input in ["y", "yes"]:
        return True
    return False

def getenv(_path):
    """
    update env param
    """
    if not isfile(_path):
        print(f"[info] not exist env file. {_path}")
        return {}

    # ファイル行読みしながらテキスト分析
    with open(_path, 'r', encoding="utf8") as f:
        ret = {}
        while True:
            line = f.readline()
            if line:
                spl = line.replace('\n', '').split("=", 2)
                ret[spl[0]] = spl[1]
            else:
                break
        return ret

def update_file(_params, _org, _fix, _dst=None):
    """
    text update by dict items

    Parameters
    -----
    _params : dict
        replace text dictionary
    _org : str
        original file path.
    _fix : str
        replace key fix str
    _dst : str
        output path
    """
    target = _org
    if not _dst is None:
        shutil.copyfile(_org, _dst)
        target = _dst
    # ファイル行読みしながらテキスト置き換え
    txt = ""
    with open(_org, 'r', encoding="utf8") as f:
        txt = f.read()
        for key, val in _params.items():
            txt = str.replace(txt, f"{_fix}{key}{_fix}", val)
    # ファイル名保存
    with open(target, mode="w", encoding="utf8", newline="\n") as f:
        f.write(txt)

def elapse_timer(_ref_frame, _pre="", _suf=""):
    """
    処理時間計測用。基準時間からcallされた時間までの差分時間を表示。

    Parameters
    ----------
    - ref_frame : float
        差分の基準時間
    - pref : str
        表示テキストのプレフィックス
    - suff : str
        表示テキストのサフィックス

    Returns
    -------
    - get_frame : float
        差分計測用に取得した時間
    """
    get_frame = time.time()
    elapsed_frame = get_frame - _ref_frame
    print(f"{_pre}{elapsed_frame}{_suf}")
    return get_frame

def check_path(_cls: str, _ref: str, _abort=False):
    """
    パスの存在確認

    Parameters
    -----
    _cls : str
        参照元。
    _ref : str
        確認するパス
    _abort : bool
        存在しない場合処理中断するか。

    Returns
    -----
    - result:bool
    """
    if not exists(_ref):
        print(f'[error] {_cls}: not exist file. [{_ref}]')
        if _abort:
            sys.exit()
        return False
    return True

def local_ip():
    """
    socketを使ってローカルIPを取得

    Returns
    ----------
    get_ip : str
        取得したIPアドレス
    """
    get_ip = [
        (s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
        ][0][1]
    return get_ip

def cmd_lines(_cmd, _cwd="", _encode='cp932', _wait_enter=False, _split=True):
    """
    execute command and stream text

    Parameters
    -----
    _cmd : list or str
        commands list
    _cwd : str
        current work dir.
    _encode : str
        default value cp932 (set utf-8 fix errors)
    """
    if isinstance(_cmd, list):
        for ref in _cmd:
            print(f"\n[info] command executed. [{ref}]")
            if _wait_enter:
                input("enter to execute cmd. ([ctrl + c] to cancel script)")
            cmd = ref
            if _split:
                cmd = ref.split()
            if _cwd == "":
                proc = subprocess.Popen(cmd
                                        , stdout=subprocess.PIPE
                                        , stderr=subprocess.STDOUT
                                        , shell=True)
            else:
                proc = subprocess.Popen(cmd
                                        , cwd=_cwd
                                        , stdout=subprocess.PIPE
                                        , stderr=subprocess.STDOUT
                                        , shell=True)
            while True:
                line = proc.stdout.readline()
                if line:
                    yield line.decode(_encode)
                if not line and proc.poll() is not None:
                    break
    else:
        print(f"\n[info] command executed. [{_cmd}]")
        if _wait_enter:
            input("enter to execute cmd. ([ctrl + c] to cancel script)")
        cmd = _cmd
        if _split:
            cmd = _cmd.split()
        if _cwd == "":
            proc = subprocess.Popen(cmd
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.STDOUT)
        else:
            proc = subprocess.Popen(cmd
                                    , cwd=_cwd
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline()
            if line:
                yield line.decode(_encode)
            if not line and proc.poll() is not None:
                break


def find_text(_ref, _find):
    """
    check word in text file

    Parameters
    -----
    _ref: str
        target path
    _find: str
        search word
    """
    check_path(sys._getframe().f_code.co_name, _ref)
    with open(_ref) as flines:
        for row, text in enumerate(flines, start=1):
            text = text.rstrip()
            if _find in text:
                return True
    return False

def ymd_to_timestamp(ymd, is_ms=False):
    """
    yyyymmddhhiiss convert to timestamp

    Parameters
    -----
    _ymd : str
        target date str
    _is_ms : str
        comvert to ms style
    """
    ret = dt.strptime(ymd, '%Y/%m/%d %H:%M:%S').timestamp()
    if is_ms:
        ret = f"{int(ret)}000"
    return int(ret)

