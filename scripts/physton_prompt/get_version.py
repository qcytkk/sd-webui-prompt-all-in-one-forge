import os
import re
import subprocess

# 手工维护的版本号文件（位于插件根目录）。存在时优先作为显示版本，
# 不存在时回退到 git commit —— 这样用 zip 下载（无 .git）安装也能显示版本。
VERSION_FILE = 'version.txt'


def get_file_version():
    extension_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../'
    extension_dir = os.path.normpath(extension_dir)
    path = os.path.join(extension_dir, VERSION_FILE)
    try:
        with open(path, 'r', encoding='utf8') as f:
            version = f.read().strip()
        if version:
            return version
    except Exception:
        pass
    return ''


def get_git_commit_version():
    # 仅读取本地 .git 的版本号；本项目已不跟踪任何远程仓库，不会产生网络请求
    extension_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../'
    extension_dir = os.path.normpath(extension_dir)
    git_path = os.path.join(extension_dir, '.git')
    if os.path.exists(git_path):
        try:
            git = os.environ.get('GIT', "git")
            if not git:
                git = "git"
            cmd = [git, 'rev-parse', 'HEAD']
            commit_version = subprocess.check_output(cmd, cwd=extension_dir).decode('utf-8').strip()
            if re.match(r'^[0-9a-f]{40}$', commit_version):
                return commit_version
        except Exception as e:
            pass

        try:
            ref_path = os.path.join(git_path, 'refs', 'heads', 'main')
            with open(ref_path, 'r') as f:
                commit_version = f.read().strip()
                if re.match(r'^[0-9a-f]{40}$', commit_version):
                    return commit_version
        except Exception as e:
            pass

    return ''


def get_version():
    """显示用版本号：优先 version.txt，其次 git commit，都没有则为空。"""
    return get_file_version() or get_git_commit_version()


def get_git_remote_versions(page=1, per_page=100, filter_update_readme=False):
    # 已移除对 GitHub / Gitee 上游仓库的网络请求：不再对接任何远程仓库
    return []


def get_latest_version():
    # 无远程版本可比较，直接返回本地版本
    return get_version()
