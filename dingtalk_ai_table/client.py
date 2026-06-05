import json
import os
import subprocess
from typing import Any, Dict, List


MCPORTER_CONFIG_ENV = 'MCPORTER_CONFIG'
PROJECT_MCPORTER_CONFIG = os.path.join('config', 'mcporter.json')
MCP_SERVER_NAME = 'dingtalk-ai-table'


def get_mcporter_config_path() -> str:
    """
    获取 mcporter 配置文件路径。

    优先级：
    1. MCPORTER_CONFIG 环境变量
    2. {cwd}/config/mcporter.json
    """
    config_path = os.environ.get(MCPORTER_CONFIG_ENV)
    if config_path:
        return config_path

    config_path = os.path.join(os.getcwd(), PROJECT_MCPORTER_CONFIG)
    if os.path.isfile(config_path):
        return config_path

    raise RuntimeError(
        '错误：未找到 mcporter 配置文件，请设置 MCPORTER_CONFIG，'
        '或在当前工作目录创建 config/mcporter.json'
    )


def build_mcporter_env() -> Dict[str, str]:
    env = os.environ.copy()
    env[MCPORTER_CONFIG_ENV] = get_mcporter_config_path()
    return env


def build_mcporter_call(args: List[str]) -> List[str]:
    return ['mcporter', 'call', MCP_SERVER_NAME] + args


def run_mcporter(args: List[str], timeout: int = 60) -> Any:
    if not args:
        raise ValueError('错误：空命令')

    cmd = build_mcporter_call(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=build_mcporter_env(),
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f'错误：命令执行超时（{timeout} 秒）')
    except FileNotFoundError:
        raise RuntimeError('错误：未找到 mcporter 命令，请确认已安装')

    if result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip() or 'mcporter 调用失败'
        raise RuntimeError(f'错误：{error_text}')

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        preview = result.stdout[:200]
        raise RuntimeError(f'无法解析响应：{preview}...\nJSON 解析错误：{exc}')
