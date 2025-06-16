import gzip
import base64
import json

from oas_command_handle import OasisCommandDispatcher
from oas import OASISGame
from oas import datetime


def compress_data(data_obj):
    """
    将 Python 对象压缩为 base64 编码的字符串。
    通常用于压缩 JSON 数据结构。
    """
    json_str = json.dumps(data_obj, ensure_ascii=False, separators=(',', ':'))
    binary = gzip.compress(json_str.encode('utf-8'))
    b64_str = base64.b64encode(binary).decode('utf-8')
    return b64_str

def decompress_data(b64_str):
    """
    解压 base64 编码的压缩字符串，返回 Python 对象。
    """
    binary = base64.b64decode(b64_str.encode('utf-8'))
    json_str = gzip.decompress(binary).decode('utf-8')
    return json.loads(json_str)


def main():
    # 初始化默认数据
    default_user_data = {
        "oasis_coins": 100,
        "transfer_history": [],
        "wing_suit_stats": {
            "total_jumps": 0,
            "total_score": 0,
            "achievements": [],
            "current_map": None,
            "current_height": 3000,
            "death_count": 0
        },
        "gamble_stats": {"total_wins": 0, "total_losses": 0, "daily_wins": 0},
        "lottery_tickets": [],  # 直接在此初始化彩票数据
        "inventory": {},  # 背包字段
        "equipped_items": {},  # 装备字段
    }

    default_global_data = {
        "leaderboard": {"daily": [], "monthly": [], "all_time": []},
        "daily_reset": datetime.now().isoformat(),
        "monthly_reset": datetime.now().isoformat(),
        "drop_items": []
    }

    # 读取所有输入行
    import sys
    input_lines = sys.stdin.read().splitlines()

    # 第一行是数据输入
    json_input = input_lines[0].strip() if len(input_lines) > 0 else "{}"
    data_input = json.loads(json_input) if json_input else {}

    # 解析基础参数
    user_id = data_input.get("userID", 0)
    nickname = data_input.get("nickname", "神秘旅者")

    # 加载存储数据
    try:
        global_data_raw = data_input.get("global", "")
        user_data_raw = data_input.get("storage", "")

        # 先尝试解压，如果失败则退回原始 JSON
        try:
            global_data = decompress_data(global_data_raw) if global_data_raw else default_global_data.copy()
        except Exception:
            global_data = json.loads(global_data_raw) if global_data_raw else default_global_data.copy()

        try:
            user_data = decompress_data(user_data_raw) if user_data_raw else default_user_data.copy()
        except Exception:
            user_data = json.loads(user_data_raw) if user_data_raw else default_user_data.copy()

    except Exception as e:
        print("⚠️ 全部解析失败，使用默认数据：", e)
        global_data = default_global_data.copy()
        user_data = default_user_data.copy()

    # 获取命令输入
    command = input_lines[1].strip() if len(input_lines) > 1 else "help"

    # 初始化游戏实例
    game = OASISGame(user_id, nickname, user_data, global_data)
    dispatcher = OasisCommandDispatcher(user_id, nickname, user_data, global_data)
    # 处理命令
    result = dispatcher.handle_command(command)
    # 更新排行榜
    game.update_leaderboard()

    # 确保绿洲币不为负数
    if game.user_data["oasis_coins"] < 0:
        game.user_data["oasis_coins"] = 0

    # 构建输出数据
    data_output = {
        "content": result,
        "storage": compress_data(game.user_data),
        "global": compress_data(game.global_data)
    }

    print(json.dumps(data_output, ensure_ascii=False, separators=(',', ':')))
