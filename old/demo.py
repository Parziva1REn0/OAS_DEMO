import copy
import json
import uuid
from collections import Counter

from datetime import datetime, timedelta, time

import pytz

tz = pytz.timezone('Asia/Shanghai')


# —————————————————— 更新日志 ——————————————————
def get_update_log(date=None):
    """
    获取更新日志，Markdown 格式输出
    :param date: 可选参数，格式 "MM/DD/YYYY"
    :return: Markdown 格式更新内容或日期列表
    """
    update_list = {
        "06/10/2025": ["""### 📅 更新日志 06/10/2025

#### ✅ 已完成
- 全面重写 `ShootingRange` 类  
  - 支持装备多种武器（内格夫、AWM、马克沁、M4A1、AK47、巴雷特等）  
  - 不同武器单次最大射击数与弹药单价独立配置  
  - 购买新武器自动回收旧子弹并返还绿洲币  
  - 自动补齐缺失字段，修复 `proficiency` KeyError 问题  
  - 完整实现 `shoot` 方法：命中率／环数／熟练度计算及技能触发  
- 更新 `help()` 输出，新增所有指令示例和各武器最大射击数、子弹单价提示  
- 黑市模块新增多款枪支：内格夫、AWM、马克沁、M4A1、AK47、巴雷特、沙漠之鹰、斯泰尔、汤姆逊冲锋枪、格洛克

#### 🔧 进行中 / 规划中
- 钓鱼模块随机事件丰富化，新增更多天气相关描述  
- 钓鱼“海盗”特殊情景新增幽默梗，如海盗喊“去码头整点薯条”等，增强趣味性  
- 阴天天气新增海鸥吐槽梗，提升沉浸感  

#### 💤 暂缓更新

    """]

    }

    sorted_dates = sorted(update_list.keys(), reverse=True)

    if date is None:
        # 没传日期，返回可查询日期列表（Markdown 格式）
        available_dates = "\n".join([f"- `{d}`" for d in sorted_dates])
        return (
            "### 🗓 可查询更新日志日期：\n"
            f"{available_dates}\n\n"
            "📌 输入指令：`update <日期>`（如 `update 05/29/2025`）查看详情"
        )

    if date in update_list:
        return update_list[date][0]
    else:
        available_dates = "\n".join([f"- `{d}`" for d in sorted_dates])
        return (
            f"⚠️ 未找到 `{date}` 的更新记录。\n\n"
            "### 🗓 可查询更新日志日期：\n"
            f"{available_dates}"
        )


# —————————————————— 输出工具 ——————————————————
def to_markdown(text):
    """
    简单的文本转Markdown格式的函数。
    规则演示：
    - 支持自动转换换行（用两个空格+换行）
    - 支持简单的标题标记：
        以 '## ' 开头的行转换成二级标题
        以 '# ' 开头的行转换成一级标题
    - 支持以 '- ' 或 '* ' 开头的行保持为列表
    - 其他文本保持原样

    你可以按需修改增强。
    """
    lines = text.split('\n')
    md_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# '):
            # 一级标题
            md_lines.append(stripped)
        elif stripped.startswith('## '):
            # 二级标题
            md_lines.append(stripped)
        elif stripped.startswith('- ') or stripped.startswith('* '):
            # 列表行
            md_lines.append(stripped)
        elif stripped == '':
            # 空行保持空行
            md_lines.append('')
        else:
            # 普通行，末尾加两个空格+换行，保证换行生效
            md_lines.append(line + '  ')
    return '\n'.join(md_lines)


import re


def parse_mirai_at(message):
    """
    解析消息中可能包含的用户 ID，支持多种格式：
    - [mirai:at:12345678]
    - @12345678
    - 纯数字 ID

    参数:
        message (str): 消息字符串

    返回:
        str: 提取的用户 ID，未找到则返回 None
    """
    # 尝试匹配 [mirai:at:12345678]
    match = re.search(r'\[mirai:at:(\d+)\]', message)
    if match:
        return match.group(1)

    # 尝试匹配 @12345678
    match = re.search(r'@(\d{5,})', message)
    if match:
        return match.group(1)

    # 尝试匹配纯数字 ID（注意避免误识别普通数字）
    if message.strip().isdigit() and len(message.strip()) >= 5:
        return message.strip()

    return None


help_list = """
🌌 OASIS 绿洲世界帮助系统 —— 测试版（可能删档）🌌

🧪 测试补偿说明：
参与测试的玩家，正式版上线将获得补偿：
- 总财富 ÷10（若超过百万则 ÷100，千万则 ÷1000）

【基本指令】
🔹 help / h                - 显示本帮助菜单
🔹 stats / s               - 查看当前状态（资产 / 装备 / 位置）
🔹 rank / r [d|m|es]       - 查看排行榜（d 日榜 / m 月榜 / es 极限运动榜）
🔹 news / 今日新闻         - 查看绿洲世界的最新大事件！

【经济系统】
💸 transfer <@用户> <金额|all> - 转账绿洲币
   ▸ 示例：transfer @123456 500
   ▸ 支持 transfer all（转出全部）
   ▸ 管理员指令：transfer admin <@用户> <金额>（直接修改余额）

💼 申请 <职业>             - 申请职业（如：警察 / 黑警）
👋 辞职                    - 放弃当前职业
💣 suicide                 - 自我重置角色（清空资产后复活）

【彩票系统】
🎫 彩票 [数量]             - 购买彩票（默认 1 张，最多 100 张 / 天）
📊 彩票统计                - 查看当日购买彩票收益与历史记录

【极限运动】
🪂 wingsuit <地图编号>     - 翼装飞行（地图：1 喜马拉雅 / 2 迪拜 / 3 亚马逊）
🏎️ race <地图编号>         - 狂野飙车（1~8 各具特色，含隐藏彩蛋）
✈️ skydive <飞机编号>       - 极限跳伞拍摄任务（1~10 架不同飞机）
🏆 rank es                 - 查看极限运动排行榜

【娱乐设施】
🎰 dc <类型> <金额>        - 赌场游戏（类型：栗子机 / 21点 / 轮盘）
🎲 roll <面数> <次数>      - 掷骰工具（例：roll 20 3）

【靶场系统】
🏹 靶场 进入 [daily|monthly|...]- 进入靶场（付费）
🔫 靶场 购买子弹 <数量>      - 每发 3 币，可多买
🎯 靶场 射击                - 使用一发子弹进行训练，提升命中率
📊 靶场 状态                - 查看你的训练统计和准确度
❓ 靶场 help                - 查看靶场玩法说明

【挖宝系统】
⛏ 挖宝 <上 / 下 / 左 / 右>    - 向指定方向挖掘
📦 挖宝拾取                 - 拾取当前位置掉落的所有物品

【出海 & 潜水】
🎣 钓鱼                     - 出海钓鱼，有机会遇到巨大或神秘鱼类
🤿 潜水                     - 深海探索，注意躲避毒水母
🏥 去医院 / hospital        - 解毒治疗中毒状态

【背包系统】
🎒 inventory / i            - 查看你的物品
🔧 equip <物品编号>         - 装备物品
📦 drop <物品编号> [数量]   - 丢弃背包中的物品

【商城系统】
🛒 商城                    - 查看商品列表（如挖宝装备）
🛒 商城 <物品名>           - 购买指定商品

【消息系统】
📩 msg <@用户> <内容>       - 给其他玩家发送私信（上线优先弹出）

【管理员指令】
🛑 stop <模块名>           - 禁用指定游戏模块
☠️ kill <@用户>             - 清空某位玩家资产
👮‍♀️ jail <@用户>            - 立即逮捕某位玩家入狱（管理员专用）

🌟 特别提示：
每天 10:00 - 凌晨 4:00 为海底星空时间段，
出海或潜水有几率获得 ✨【星空小鱼】 等奖励！
"""




# ————————————————OASIS-BANK—————————————————
class BankModule:
    def __init__(self, user_data):
        self.user_data = user_data
        self.user_data = user_data
        self.user_data.setdefault("bank", {})
        self.user_data["bank"].setdefault("balance", 0)
        self.user_data["bank"].setdefault("rewards_claimed", {})
        self.user_data["bank"].setdefault("safe_box", [])

    def deposit(self, amount):
        # 自动修复 bank 数据缺失
        self.user_data.setdefault("bank", {"balance": 0, "rewards_claimed": {}, "safe_box": []})
        self.user_data["bank"].setdefault("balance", 0)
        self.user_data["bank"].setdefault("rewards_claimed", {})

        if amount <= 0:
            return "❌ 存款金额必须大于 0"
        if self.user_data.get("oasis_coins", 0) < amount:
            return "❌ 余额不足，无法完成存款"

        # 执行存款
        self.user_data["oasis_coins"] -= amount
        self.user_data["bank"]["balance"] += amount

        # 奖励逻辑
        thresholds = [10000, 50000, 100000, 500000, 1000000]
        reward_msg = ""
        for threshold in thresholds:
            key = str(threshold)
            if amount >= threshold and not self.user_data["bank"]["rewards_claimed"].get(key):
                coupon_value = int(threshold * 0.01)
                coupon_name = f"绿洲币兑换券[{coupon_value}]"
                self.user_data["inventory"].append({
                    "id": "绿洲币兑换券[{coupon_value}]",  # 标准化 id
                    "name": coupon_name,
                    "quantity": 1,
                    "description": f"绿洲银行赠送的兑换券，可兑换 {coupon_value} 绿洲币"
                })
                self.user_data["bank"]["rewards_claimed"][key] = True
                reward_msg += f"🎁 首次存入 {threshold} 币，获得兑换券 [{coupon_value}]！\n"

        msg = f"✅ 存入成功：{amount} 绿洲币\n🏦 当前银行余额：{self.user_data['bank']['balance']} 币"
        if reward_msg:
            msg += "\n" + reward_msg.strip()
        return msg

    def withdraw(self, amount):
        if amount <= 0:
            return "❌ 取款金额必须大于 0"
        if self.user_data["bank"]["balance"] < amount:
            return "❌ 银行余额不足"

        self.user_data["bank"]["balance"] -= amount
        self.user_data["oasis_coins"] += amount
        return f"✅ 成功取出 {amount} 绿洲币\n🏦 当前银行余额：{self.user_data['bank']['balance']}币"

    def check_balance(self):
        return f"🏦 当前银行余额：{self.user_data['bank']['balance']} 绿洲币"

    def redeem_coupon(self):
        for item in self.user_data.get("inventory", []):
            name = item.get("name", "")
            quantity = item.get("quantity", 1)

            # 检查是否是兑换券，例如名为：绿洲币兑换券[100]
            if "绿洲币兑换券" in name:
                match = re.search(r"\[(\d+)\]", name)
                if match:
                    value = int(match.group(1))
                    self.user_data["oasis_coins"] += value
                    item["quantity"] -= 1
                    if item["quantity"] <= 0:
                        self.user_data["inventory"].remove(item)
                    return f"💳 你使用了一张兑换券，获得 {value} 绿洲币"

        return "❌ 没有可用的兑换券"
        # --- 新增：保险柜功能 ---

    def safe_box_store(self, item_name):
        for item in self.user_data["inventory"]:
            # 正确获取 item 的名称
            item_real_name = item.get("name", "")
            if item_real_name == item_name:
                self.user_data["bank"].setdefault("safe_box", [])  # 确保 safe_box 存在
                self.user_data["bank"]["safe_box"].append(item)
                self.user_data["inventory"].remove(item)
                return f"🔐 已将 {item_name} 存入银行保险柜"
        return f"❌ 背包中没有找到物品：{item_name}"

    def safe_box_take(self, item_name):
        self.user_data["bank"].setdefault("safe_box", [])  # 确保 safe_box 存在
        for item in self.user_data["bank"]["safe_box"]:
            item_real_name = item.get("name", "")
            if item_real_name == item_name:
                self.user_data["inventory"].append(item)
                self.user_data["bank"]["safe_box"].remove(item)
                return f"📦 已从保险柜取出物品：{item_name}"
        return f"❌ 保险柜中没有找到物品：{item_name}"

    def safe_box_view(self):
        items = self.user_data.get("bank", {}).get("safe_box", [])

        if not items:
            return "📦 保险柜是空的"

        msg = "🔐 保险柜内物品：\n"
        for item in items:
            name = item.get("name", f"未命名物品({item.get('id', '未知ID')})")
            quantity = item.get("quantity", 1)
            msg += f"- {name} × {quantity}\n"

        return msg.strip()

    def handle(self, cmd_parts):
        if len(cmd_parts) < 2:
            return "🏦 使用方式：银行 存 <金额> / 取 <金额> / 余额 / 兑换券\n🧰 或：银行 保险柜 存/取/查看 <物品名>"

        if cmd_parts[0] in ["银行", "bank"]:
            sub = cmd_parts[1]
            if sub in ["存", "deposit", "存钱"] and len(cmd_parts) > 2 and cmd_parts[2].isdigit():
                return self.deposit(int(cmd_parts[2]))
            elif sub in ["取", "withdraw", "取钱"] and len(cmd_parts) > 2 and cmd_parts[2].isdigit():
                return self.withdraw(int(cmd_parts[2]))
            elif sub in ["余额", "balance"]:
                return self.check_balance()
            elif sub == "兑换券":
                return self.redeem_coupon()

            elif cmd_parts[1] in ["保险柜", "safe", "保险箱"]:
                if cmd_parts[2] in ["存", "store"] and len(cmd_parts) > 3:
                    return self.safe_box_store(cmd_parts[3])
                elif cmd_parts[2] in ["取", "take"] and len(cmd_parts) > 3:
                    return self.safe_box_take(cmd_parts[3])
                elif cmd_parts[2] in ["查看", "look", "view"]:
                    return self.safe_box_view()
                else:
                    return "❌ 无效保险柜指令，用法示例：银行 保险柜 存 <物品名> / 取 <物品名> / 查看"

        return "❌ 未知指令，用法示例：银行 存 10000 / 银行 保险柜 存 钥匙"

# ————————————————OASIS-EventBoard—————————————————
class EventBoard:
    def __init__(self, global_data):
        self.global_data = global_data
        self.global_data.setdefault("event_board", {
            "active_events": [
                "🎁 银行首次存入达指定金额可获兑换券奖励（1%）！",
                "🌌 海底星空时段（每日 10:00 - 次日 04:00）钓鱼概率提高！",
                "🏹 靶场累计射击可解锁专属技能与段位！",
                "🚕 新职业：出租车司机、Pizza外卖员已开放申请！",
                "🎲 dc 模块新增足球竞猜、动物赛跑，欢迎下🐖支持！",
                "💥 【新活动】组队抢银行，4人组队齐心协力抢劫高额奖金！",
                "🎡 参与幸运轮盘，赢取额外绿洲币和神秘奖励！"
            ],
            "last_updated": datetime.now(tz).isoformat()
        })

    def show_events(self):
        events = self.global_data["event_board"]["active_events"]
        if not events:
            return "📭 当前没有正在进行的官方活动。"

        output = "📢 当前活动公告：\n"
        for i, event in enumerate(events, 1):
            output += f"{i}. {event}\n"

        updated_time = self.global_data["event_board"].get("last_updated", "")
        if updated_time:
            output += f"\n📅 活动更新时间：{updated_time[:10]}"

        return output

    def handle(self, cmd_parts):
        return self.show_events()



# ————————————————OASIS-Library———————————————

class LibraryModule:
    def __init__(self):
        self.entered_users = set()
        self.librarian_quotes = [
            "📚 馆长推了推眼镜：‘年轻人，真正的速度，不在车上，而在你敢不敢冲。’",
            "🛞 馆长笑了笑：‘你以为起点在起跑线，其实从你选择哪辆车那刻起，结局就写好了。’",
            "🗝️ 馆长望向窗外：‘有时候，打破规则才能找到通往终点的隐藏路径。’",
            "🔍 馆长轻声道：‘你在VR乐园呆过吗？那里记录了许多未完成的挑战…’",
            "📖 馆长从抽屉拿出一本泛黄的笔记本：‘不是每一个房间都能安全离开，特别是那些空无一人的。’",
            "🧠 馆长叹息：‘越害怕，就越接近真相。勇气，有时候是通往下一层的唯一门票。’",
            "🌀 馆长神情严肃：‘他们说那是“闪灵酒店”的副本，但我知道，那只是测试你是否配得上的第一关。’",
            "🎮 馆长语气平静：‘第一个彩蛋？你甚至还没真正起步。’",
            "🚪 馆长点了点桌上的模型车：‘它看起来普通，实际上…很多人从这开始翻车。’",
            "👁️ 馆长目光锐利：‘你有没有想过，真正的挑战根本不在游戏主菜单上？’",
            "⛓️ 馆长低声道：‘赛道之外，才是你该去的地方。问题是…你敢偏离吗？’",
            "🧩 馆长拍了拍你的肩：‘不要只看那些你能点的按钮。有些东西，是藏在按钮背后的代码里。’",
            "🖼️ 馆长看着你良久：‘如果你觉得奇怪，那可能就是对的。奇怪，才是入口。’",
            "🎲 馆长突然压低声音：‘骰子不是随机的，只是你还没学会读它的语言。’"
        ]

    def handle_command(self, user_id, subcommand):
        if subcommand == "":
            self.entered_users.add(user_id)
            return (
                "🏛️ 你步入绿洲图书馆，头顶漂浮着数据流与光晕。\n"
                "🧓 馆长在远处静候，似乎在等待着什么。\n"
                "💬 输入 `library talk` 与馆长交谈。"
            )

        elif subcommand == "talk":
            import random
            return random.choice(self.librarian_quotes)

        else:
            return "❓ 未知子指令，支持: `library` 或 `library talk`"


# ————————————————OASIS-shooting———————————————
import random

class ShootingRange:
    ENTRY_FEES = {
        "daily": 200,
        "monthly": 688,
        "seasonal": 1666,
        "annual": 6666
    }

    RANKS = [
        (0.95, "至尊射手🏅"),
        (0.85, "精英射手🎯"),
        (0.7,  "合格射手✅"),
        (0.5,  "初学射手🔰"),
        (0,    "新手🆕")
    ]
    GROWTH_STAGES = [
        (0, "萌新学员", "暂无特殊能力"),
        (100, "初级射手", "抗干扰 +5%"),
        (300, "中级射手", "风偏修正 +0.5 环"),
        (600, "高级射手", "技能触发概率 +5%"),
        (1000, "射击精英", "精准力永久提升 +0.5"),
        (2000, "绿洲神枪手", "可参加 PVP 射击锦标赛"),
    ]
    ATTENTION_LEVELS = [
        (5000, 5),
        (2000, 4),
        (1000, 3),
        (500, 2),
        (100, 1),
        (0, 0)
    ]
    PROFICIENCY_LEVELS = [
        (0, "萌新学员", "暂无特殊能力"),
        (100, "初级射手", "抗干扰 +5%"),
        (300, "中级射手", "风偏修正 +0.5 环"),
        (600, "高级射手", "技能触发概率 +5%"),
        (1000, "射击精英", "精准力永久提升 +0.5"),
        (2000, "绿洲神枪手", "可参加 PVP 射击锦标赛"),
    ]
    WEAPONS = {
        "内格夫": {"max_shoot": 60, "bullet_price": 5},
        "AWM": {"max_shoot": 5, "bullet_price": 20},
        "马克沁": {"max_shoot": 200, "bullet_price": 8},
        "M4A1": {"max_shoot": 30, "bullet_price": 7},
        "AK47": {"max_shoot": 30, "bullet_price": 6},
        "巴雷特": {"max_shoot": 10, "bullet_price": 25},
        "沙漠之鹰": {"max_shoot": 7, "bullet_price": 12},
        "斯泰尔": {"max_shoot": 30, "bullet_price": 6},
        "汤姆逊冲锋枪": {"max_shoot": 50, "bullet_price": 4},
        "格洛克": {"max_shoot": 17, "bullet_price": 5},
    }

    def __init__(self, user_data, global_data):
        self.user_data = user_data
        self.global_data = global_data
        self.range_data = user_data.setdefault("shooting", {})
        # 修复老数据，初始化缺失字段
        self.range_data.setdefault("accuracy", 0.3)
        self.range_data.setdefault("total_shots", 0)
        self.range_data.setdefault("hits", 0)
        self.range_data.setdefault("bullet_count", 0)
        self.range_data.setdefault("membership", None)
        self.range_data.setdefault("avg_rings", 0)
        self.range_data.setdefault("proficiency", 0)
        self.range_data.setdefault("proficiency_level", 0)
        self.range_data.setdefault("equipped_weapon", None)  # 当前装备武器名称
        self.range_data.setdefault("weapon_bullets", 0)     # 装备武器剩余弹药

    def equip_weapon(self, weapon_name):
        if weapon_name not in self.WEAPONS:
            return f"❌ 武器[{weapon_name}]不存在，请选择：{', '.join(self.WEAPONS.keys())}"
        # 装备武器
        self.range_data["equipped_weapon"] = weapon_name
        self.range_data["weapon_bullets"] = 0
        # 清除背包旧子弹（仅靶场子弹）
        self.clear_old_bullets()
        return f"🔫 已装备武器[{weapon_name}]，请购买对应子弹进行训练"

    def clear_old_bullets(self):
        # 遍历背包删除所有旧的“子弹”物品，并返还绿洲币
        inventory = self.user_data.get("inventory", [])
        refund = 0
        bullets_to_remove = []
        for item in inventory:
            if item["id"] == "子弹":
                refund += item["quantity"] * 3  # 老子弹固定3币/发
                bullets_to_remove.append(item)
        for item in bullets_to_remove:
            inventory.remove(item)
        if refund > 0:
            self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + refund
        # 同时清理靶场弹药计数
        self.range_data["bullet_count"] = 0
        return refund


    def get_attention_level(self):
        shots = self.range_data["total_shots"]
        for threshold, level in self.ATTENTION_LEVELS:
            if shots >= threshold:
                return level
        return 0

    def get_attention_bonus(self):
        # 每级注意力提升0.05准确度，示范值
        level = self.get_attention_level()
        return level * 0.05

    def enter_range(self, plan="daily"):
        if self.range_data["membership"]:
            return "✅ 你已经拥有靶场权限，可直接训练！"

        if plan not in self.ENTRY_FEES:
            return "❌ 无效的计划类型，可选项有：daily, monthly, seasonal, annual"

        fee = self.ENTRY_FEES[plan]
        if self.user_data.get("oasis_coins", 0) < fee:
            return f"❌ 余额不足，进入靶场需要 {fee} 绿洲币"

        self.user_data["oasis_coins"] -= fee
        self.range_data["membership"] = plan
        self.add_simple_item("表情", 1, "靶场专用训练武器")
        return f"🎯 成功购买靶场[{plan}]会员，欢迎进入训练！"

    def buy_bullets(self, count):
        if count <= 0:
            return "❌ 子弹数量必须为正整数"
        weapon = self.range_data.get("equipped_weapon")
        if not weapon:
            return "❌ 请先装备武器后购买对应子弹"
        bullet_price = self.WEAPONS[weapon]["bullet_price"]
        cost = bullet_price * count
        if self.user_data.get("oasis_coins", 0) < cost:
            return f"❌ 余额不足，购买 {count} 发[{weapon}]子弹需要 {cost} 绿洲币"

        # 购买前清理旧子弹并返还（如果是第一次买弹不清理）
        refund = self.clear_old_bullets()
        if refund > 0:
            # 返还弹药费用后，重新计算余额是否足够
            if self.user_data.get("oasis_coins", 0) < cost:
                return f"❌ 余额不足，购买 {count} 发[{weapon}]子弹需要 {cost} 绿洲币（清理旧弹药返还{refund}币）"

        self.user_data["oasis_coins"] -= cost
        self.range_data["weapon_bullets"] += count
        self.add_simple_item("子弹", count, f"{weapon} 专用弹药")
        return f"🔫 你购买了 {count} 发[{weapon}]子弹，目前总子弹数: {self.range_data['weapon_bullets']}"

    def shoot(self, count=1):
        if not self.range_data["membership"]:
            return "🚫 你尚未加入靶场会员，请先购买后再训练"

        weapon = self.range_data.get("equipped_weapon")
        if not weapon:
            return "🚫 你尚未装备训练武器，请先切换武器"

        max_shots = self.WEAPONS[weapon]["max_shoot"]
        if count <= 0 or count > max_shots:
            return f"❌ 使用【{weapon}】一次最多射击 {max_shots} 发子弹"

        if self.range_data["weapon_bullets"] < count:
            return f"❌ 子弹不足，当前仅剩 {self.range_data['weapon_bullets']} 发，请补充弹药"

        # 消耗子弹
        self.range_data["weapon_bullets"] -= count

        # 减少背包里的子弹数量
        inventory = self.user_data.get("inventory", [])
        for item in inventory:
            if item["id"] == "子弹":
                if item["quantity"] > count:
                    item["quantity"] -= count
                else:
                    inventory.remove(item)
                break

        hits = 0
        total_rings = 0.0
        results = []

        # 注意力加成
        attention_bonus = self.get_attention_bonus()

        # 当前熟练度
        proficiency = self.range_data.get("proficiency", 0)

        # 触发技能条件（>=1000发）
        active_skills = {}
        total_shots_after = self.range_data["total_shots"] + count
        if total_shots_after >= 1000:
            active_skills["calm_focus"] = True  # 增强精准
            active_skills["quick_react"] = True  # 降低卡壳
            results.append("🧠 你进入了沉稳状态，呼吸节奏与手感更加协调。")

        # 计算每发的环数和命中
        for i in range(count):
            base_hit_chance = 0.5 + 0.3 * (proficiency / 2000)  # 基础命中随熟练度线性提升
            base_hit_chance += attention_bonus
            if active_skills.get("calm_focus"):
                base_hit_chance += 0.1  # 技能加成

            base_hit_chance = min(base_hit_chance, 0.98)  # 命中概率上限98%

            hit = random.random() < base_hit_chance
            if hit:
                hits += 1
                # 环数计算，随机带浮动，成长加成
                ring = random.uniform(7.0, 10.0)
                ring += (proficiency / 2000) * 2  # 成长提升最大2环
                # 技能增强精准力
                if active_skills.get("calm_focus"):
                    ring += 0.5
                ring = min(ring, 10)
                total_rings += ring
            else:
                # 没中环数为0
                total_rings += 0.0

        # 更新训练数据
        self.range_data["hits"] += hits
        self.range_data["total_shots"] += count

        # 计算准确度 = 总命中次数/总射击次数
        self.range_data["accuracy"] = self.range_data["hits"] / self.range_data["total_shots"]

        # 平均环数更新
        if self.range_data["total_shots"] > 0:
            self.range_data["avg_rings"] = total_rings / count

        # 训练熟练度增加（命中越多，增长越快）
        proficiency_gain = hits * 2 + count * 0.5
        self.range_data["proficiency"] = self.range_data.get("proficiency", 0) + proficiency_gain

        # 计算熟练度等级
        new_level = 0
        for idx, (threshold, _, _) in enumerate(self.PROFICIENCY_LEVELS):
            if self.range_data["proficiency"] >= threshold:
                new_level = idx
        self.range_data["proficiency_level"] = new_level

        results.append(f"🔫 射击了 {count} 发子弹，命中 {hits} 发，当前准确度 {self.range_data['accuracy']:.2%}")
        results.append(f"🎯 平均环数: {self.range_data['avg_rings']:.2f}")
        results.append(f"📈 熟练度增加了 {proficiency_gain:.1f}，当前等级 {self.PROFICIENCY_LEVELS[new_level][1]}")

        return "\n".join(results)

    def update_accuracy(self):
        shots = self.range_data["total_shots"]
        if shots == 0:
            self.range_data["accuracy"] = 0
            return

        hits = self.range_data["hits"]
        self.range_data["accuracy"] = hits / shots

    def get_status(self):
        attention_level = self.get_attention_level()
        rank = "新手🆕"
        for acc_threshold, rank_name in self.RANKS:
            if self.range_data["accuracy"] >= acc_threshold:
                rank = rank_name
                break
        return (
            f"🏁 靶场状态：\n"
            f"  - 总射击次数：{self.range_data['total_shots']}\n"
            f"  - 命中次数：{self.range_data['hits']}\n"
            f"  - 当前命中率：{self.range_data['accuracy']:.2%}\n"
            f"  - 平均环数：{self.range_data.get('avg_rings', 0):.2f}\n"
            f"  - 子弹剩余数：{self.range_data['bullet_count']}\n"
            f"  - 注意力专注等级：{attention_level}\n"
            f"  - 当前段位：{rank}"
        )

    def add_simple_item(self, item_id, quantity, description):
        # 物品入包辅助（简化示范）
        if "inventory" not in self.user_data:
            self.user_data["inventory"] = []
        inv = self.user_data["inventory"]
        for item in inv:
            if item["id"] == item_id:
                item["quantity"] += quantity
                return
        inv.append({"id": item_id, "quantity": quantity, "desc": description})

    @staticmethod
    def get_leaderboard(all_users):
        # all_users: List[dict], 每个dict为玩家数据，含射击相关字段
        leaderboard = []
        for user in all_users:
            shooting = user.get("shooting", {})
            total_shots = shooting.get("total_shots", 0)
            hits = shooting.get("hits", 0)
            accuracy = shooting.get("accuracy", 0)
            avg_rings = shooting.get("avg_rings", 0)
            username = user.get("username", "匿名")
            leaderboard.append({
                "username": username,
                "total_shots": total_shots,
                "accuracy": accuracy,
                "avg_rings": avg_rings
            })

        # 按 accuracy -> avg_rings -> total_shots 排序
        leaderboard.sort(key=lambda x: (x["accuracy"], x["avg_rings"], x["total_shots"]), reverse=True)

        lines = ["🏆 靶场排行榜 Top 10 🏆"]
        for i, player in enumerate(leaderboard[:10], start=1):
            lines.append(
                f"{i}. {player['username']} - 命中率 {player['accuracy']:.2%}, 平均环数 {player['avg_rings']:.2f}, 射击次数 {player['total_shots']}"
            )
        return "\n".join(lines)

    def proficiency_status(self):
        lines = ["🌱【射击熟练度和等级】🌱"]
        current_exp = self.range_data.get("proficiency", 0)
        current_level = self.range_data.get("proficiency_level", 0)
        for idx, (threshold, name, ability) in enumerate(self.PROFICIENCY_LEVELS):
            marker = "->" if idx == current_level else "  "
            lines.append(f"{marker} 等级 {idx}: {name} （阈值: {threshold}） - 能力: {ability}")
        lines.append(f"\n当前熟练度经验: {current_exp}")
        return "\n".join(lines)

    def handle(self, cmd_parts):
        if len(cmd_parts) < 2:
            return self.help()

        sub = cmd_parts[1]
        if sub == "进入":
            plan = cmd_parts[2] if len(cmd_parts) > 2 else "daily"
            return self.enter_range(plan)
        elif sub == "装备":
            if len(cmd_parts) < 3:
                return "❌ 请指定要装备的武器名称，例如：靶场 装备 内格夫"
            weapon = cmd_parts[2]
            return self.equip_weapon(weapon)
        elif sub == "购买子弹":
            if len(cmd_parts) < 3 or not cmd_parts[2].isdigit():
                return "❌ 请指定购买子弹的数量，例如：靶场 购买子弹 10"
            count = int(cmd_parts[2])
            return self.buy_bullets(count)
        elif sub == "射击":
            count = 1
            if len(cmd_parts) > 2 and cmd_parts[2].isdigit():
                count = int(cmd_parts[2])
            return self.shoot(count)
        elif sub == "状态":
            return self.get_status()
        elif sub == "熟练度":
            return self.proficiency_status()
        elif sub == "排行榜":
            all_users = self.global_data.get("all_users", [])
            return self.get_leaderboard(all_users)
        elif sub == "help":
            return self.help()
        else:
            return "❌ 无效的靶场子指令，请使用 help 查看帮助内容"

    @staticmethod
    def help():
        fees = ShootingRange.ENTRY_FEES
        max_shots_per_weapon = ", ".join(
            [f"{w}最多{info['max_shoot']}发" for w, info in ShootingRange.WEAPONS.items()])
        bullet_prices = ", ".join([f"{w}子弹{info['bullet_price']}币/发" for w, info in ShootingRange.WEAPONS.items()])
        return (
            "🏹【靶场游戏指令说明】\n"
            "请按格式输入指令，支持以下子命令：\n\n"
            f"🔸 靶场 进入 [类型]         - 进入靶场，付费购买会员（类型及费用）：\n"
            f"    daily（日卡）：{fees['daily']}币，monthly（月卡）：{fees['monthly']}币，\n"
            f"    seasonal（季卡）：{fees['seasonal']}币，annual（年卡）：{fees['annual']}币\n\n"
            "🔸 靶场 装备 <武器名称>      - 装备指定武器，例：靶场 装备 内格夫\n\n"
            f"🔸 靶场 购买子弹 <数量>     - 购买子弹，每发价格根据武器不同：{bullet_prices}\n\n"
            f"🔸 靶场 射击 [数量]          - 使用当前装备武器射击，单次最多射击数量限制：{max_shots_per_weapon}\n\n"
            "🔸 靶场 状态               - 查看当前靶场训练状态\n"
            "🔸 靶场 熟练度             - 查看射击熟练度和成长等级\n"
            "🔸 靶场 排行榜             - 查看靶场训练排行榜\n"
            "🔸 靶场 help               - 显示本帮助信息\n\n"
            "💡 注意：括号内为可选项，[]内为必填项。\n"
            "示例：靶场 射击 5  # 射击5发子弹\n"
        )

# ————————————————OASIS-GAME——————————————————
class OASISGame:
    def __init__(self, user_id, nickname, user_data, global_data):
        self.user_id = str(user_id)  # 统一转换为字符串格式
        self.nickname = nickname
        self.global_data = global_data

        # 管理员 ID列表
        self.admin_ids = ["2624078602"]
        # 管理员 新增全局禁用模块列表
        self.disabled_modules = global_data.setdefault("disabled_modules", [])

        # 新闻模块
        self.global_data.setdefault("news_feed", [])  # 每条为 dict：{time, content}

        self.FISHES = {
            "珊瑚鱼": {"price": 50, "description": "色彩斑斓的珊瑚鱼，令人心情愉悦。"},
            "乌贼": {"price": 60, "description": "喷墨逃逸的大乌贼，小心它的伎俩。"},
            "深海怪鱼": {"price": 120, "description": "长着灯泡的怪鱼，充满深海压力感。"},
            "海底珍珠": {"price": 200, "description": "海底采集到的纯白珍珠，价值不菲。"},
            "神秘贝壳": {"price": 90, "description": "壳上刻着奇怪图案的贝壳。"},
            "星辰碎片": {"price": 350, "description": "星光洒落深海后凝结的结晶体。"},
            "有毒水母": {"price": 10, "description": "碰到后会引起强烈中毒反应，需要及时就医！"},
            "深海金币": {"price": 150, "description": "沉没船只留下的金币，有淡淡海腥味。"},
            "遗落的耳环": {"price": 400, "description": "一枚古老的海底首饰，也许藏着故事。"},
            "宝藏箱残片": {"price": 500, "description": "锈蚀的宝箱碎片，似乎曾封印着什么。"},
            "星空小鱼": {"price": 180, "description": "在星辰闪耀中诞生的神秘鱼。"},
            # 你给的新鱼，附加简单描述
            "小黄鱼": {"price": 10, "description": "普通的小黄鱼。"},
            "蓝鳍金枪鱼": {"price": 100, "description": "珍贵的蓝鳍金枪鱼。"},
            "神秘鬼鱼": {"price": 150, "description": "神秘而诡异的深海鬼鱼。"},
            "毒河豚": {"price": 20, "description": "体内含毒的河豚，小心处理。"},
            "超大金鱼": {"price": 200, "description": "超大号的金鱼，极具观赏价值。"},
            "黄金比目鱼": {"price": 250, "description": "闪耀黄金色泽的比目鱼。"},
            "会说话的鱼": {"price": 300, "description": "传说中会说话的神秘鱼类。"},
        }

        # 摸摸头成人模块
        self.global_data.setdefault("config", {}).setdefault("adult_mode", False)


        # 黑市模块
        if "black_market" not in self.global_data:
            self.global_data["black_market"] = {
                # 原有物品
                "防催眠项链": {
                    "id": "防催眠项链",
                    "name": "防催眠项链",
                    "desc": "🔮 来自旧时代遗迹的神秘项链，蕴含星辰碎片的微光，佩戴者可免疫一切精神控制与催眠术法。",
                    "price": 120000,
                    "stock": 3
                },
                "影牙斗篷": {
                    "id": "影牙斗篷",
                    "name": "影牙斗篷",
                    "desc": "🌘 来自虚空之境的黑夜残片编织而成，穿戴后隐匿于阴影中，如幽魂游走于世。",
                    "price": 150000,
                    "stock": 5
                },

                # 新增枪支
                "内格夫": {
                    "id": "内格夫",
                    "name": "内格夫",
                    "desc": "强力通用机枪，射速快，弹药丰富，适合持续火力压制。",
                    "price": 30000,
                    "stock": 10
                },
                "AWM": {
                    "id": "AWM",
                    "name": "AWM",
                    "desc": "极致狙击步枪，精准致命，弹药昂贵但威力巨大。",
                    "price": 80000,
                    "stock": 10
                },
                "马克沁": {
                    "id": "马克沁",
                    "name": "马克沁",
                    "desc": "经典机枪，射速稳定，耐用可靠，适合中距离战斗。",
                    "price": 40000,
                    "stock": 10
                },
                "M4A1": {
                    "id": "M4A1",
                    "name": "M4A1",
                    "desc": "现代突击步枪，精准灵活，适合各种作战环境。",
                    "price": 35000,
                    "stock": 10
                },
                "AK47": {
                    "id": "AK47",
                    "name": "AK47",
                    "desc": "经典突击步枪，威力大，后坐力较强，弹药便宜。",
                    "price": 32000,
                    "stock": 10
                },
                "巴雷特": {
                    "id": "巴雷特",
                    "name": "巴雷特",
                    "desc": "重型狙击枪，射程极远，威力爆炸，适合远距离狙击。",
                    "price": 90000,
                    "stock": 10
                },
                "沙漠之鹰": {
                    "id": "沙漠之鹰",
                    "name": "沙漠之鹰",
                    "desc": "强力手枪，单发伤害高，适合近距离爆发。",
                    "price": 25000,
                    "stock": 10
                },
                "斯泰尔": {
                    "id": "斯泰尔",
                    "name": "斯泰尔",
                    "desc": "现代突击步枪，精准高效，适合快速作战。",
                    "price": 34000,
                    "stock": 10
                },
                "汤姆逊冲锋枪": {
                    "id": "汤姆逊冲锋枪",
                    "name": "汤姆逊冲锋枪",
                    "desc": "紧凑冲锋枪，射速快，适合近战扫射。",
                    "price": 28000,
                    "stock": 10
                },
                "格洛克": {
                    "id": "格洛克",
                    "name": "格洛克",
                    "desc": "可靠手枪，弹药容量大，适合备用武器。",
                    "price": 20000,
                    "stock": 10
                },
            }

        # 图书馆模块
        self.library_module = LibraryModule()

        # 先进行全局数据初始化
        self.initialize_data()

        # 最后绑定用户数据引用
        self.user_data = self.global_data["users"][self.user_id]  # 指向全局存储
        self.user_data["last_active"] = datetime.now(tz).isoformat()

        # 职业模块
        self.user_data.setdefault("career", None)  # 如 "警察" 或 "黑警"
        self.career_config = {
            "巡逻警察": {
                "desc": "每日巡视绿洲，打击基础犯罪活动",
                "requirements": {
                    "shooting": {"shots": 500, "accuracy": 0.6, "avg_rings": 6.0}
                }
            },
            "刑警": {
                "desc": "侦查重大案件，对抗高智商罪犯",
                "requirements": {
                    "shooting": {"shots": 1500, "accuracy": 0.7, "avg_rings": 6.5}
                }
            },
            "特警": {
                "desc": "处理高风险事件与武装冲突任务",
                "requirements": {
                    "shooting": {"shots": 3000, "accuracy": 0.71, "avg_rings": 6.5}
                }
            },
            "卧底警察": {
                "desc": "隐藏身份，潜伏于罪犯之中收集情报",
                "requirements": {
                    "shooting": {"shots": 1000, "accuracy": 0.65, "avg_rings": 6.0},
                    "inventory_item": "伪装面具"
                }
            },
            "交通警察": {
                "desc": "维护绿洲交通秩序，处理事故与违章",
                "requirements": {
                    "item": "驾照"
                }
            },
            "黑警": {
                "desc": "伪装正义，实则贪婪，暗中偷赃",
                "requirements": {
                    "shooting": {"shots": 2000, "accuracy": 0.72, "avg_rings": 6.0}
                }
            },
            "医生": {
                "desc": "负责给其他玩家解毒与治疗",
                "requirements": {"item": "医疗许可证"}
            },
            "猎人": {
                "desc": "野外狩猎与收集稀有材料",
                "requirements": {"coins": 3000}
            },
            "快递员": {
                "desc": "派送玩家道具，完成任务获得奖励",
                "requirements": {}
            },
            "农夫": {
                "desc": "经营萝卜农场，掌管萝卜的生死命运",
                "requirements": {"inventory_item": "金萝卜"}
            },
            "工程师": {
                "desc": "负责建造、维护绿洲系统设备，可参与装置强化与修复任务",
                "requirements": {"coins": 5000}
            },
            "胡萝卜族人": {
                "desc": "来自萝卜神庙的神秘族群，据说拔萝卜从不落空",
                "requirements": {"inventory_item": "萝卜雕像"}
            },
            "土豆族人": {
                "desc": "潜伏于泥土中的土豆信徒，信仰根茎力量。",
                "requirements": {"inventory_item": "腐烂萝卜"}
            },
            # 新增职业
            "Pizza外卖员": {
                "desc": "准时将热腾腾的披萨送到客户手中，享受速度与服务的快感。",
                "requirements": {"item": "摩托车钥匙"}
            },
            "口了么外卖员": {
                "desc": "准时将美味的餐点送到客户手中，感受风驰电掣的配送体验。",
                "requirements": {"item": "电动车钥匙"}
            },
            "出租车司机": {
                "desc": "载客穿梭于绿洲城市，为乘客提供快捷的出行服务。",
                "requirements": {"item": "驾照"}
            },
            "渔民": {
                "desc": "在绿洲的湖泊和河流中捕鱼，掌握各种钓鱼技巧。",
                "requirements": {"coins": 1000}
            },
            "矿工": {
                "desc": "深入矿井采掘矿石，为绿洲提供宝贵资源。",
                "requirements": {"item": "矿工头盔", "coins": 2000}
            },
            "拳击手" : {
            "desc": "训练有素的战士，受到攻击时会自动反击。",
            "requirements": {"item": "拳击手套"}
            },
            "隐者" : {
            "desc": "神秘行动者，在犯罪中更不易被发现。",
            "requirements": {"item": "夜行衣"}
            }


        }

        # 趣味玩法模块
        self.user_data.setdefault("status", {})
        self.user_data["status"].setdefault("poisoned", False)
        self.user_data["status"].setdefault("in_jailed", None)  # None 表示未入狱

        # 萝卜排行榜
        self.user_data.setdefault("carrot_stats", {})

        # 催眠模块描述库
        self.hypnosis_descriptions = [
            "你凑近{target}，声音低沉而温柔，在耳边缓缓低语。{target}的肩膀不自觉地放松下来，目光开始游离。",
            "你轻抚着一串念珠，口中默念咒文。{target}盯着那有节奏的指尖动作，神情逐渐陷入呆滞。",
            "你点亮了一盏昏黄的油灯，跳动的光影在墙上摇曳，{target}的眼神被牵引着，仿佛忘记了时间。",
            "你靠近{target}，吐息温热而缓慢，你的话语像呢喃的魔咒，一点点剥离{target}的意志。",
            "你拨动了一串铜铃，清脆的声音回荡在空气中，{target}的眼睛开始缓慢地眨动，意识开始游移。",
            "你施展手势引导{target}闭上双眼，语调带着节奏和催促，每一个词都像一记轻柔的敲击，敲在{target}的心门上。",
            "你递出一杯温热的饮品，里面混合着安神草药的气息，{target}啜饮之后眼神渐渐失去焦距。",
            "你轻柔地让{target}坐下，一只手轻按其肩，低声诱导，{target}像被温柔地包裹，逐渐陷入恍惚。",
            "你轻抚着水晶球的表面，喃喃低语着咒语，{target}的注意力全被那流动的光影所吸引，心神动摇。",
            "你以极缓慢的语速讲述一段古老的故事，故事本身无比平静，却像波纹一般渗透进{target}的意识深处。",
            "你用柔指轻点{target}的额头中心，那触感如同羽毛划过心湖，{target}的瞳孔开始放大。",
            "你靠近{target}，视线深邃如黑夜般吸人，你只说了一个字，{target}的嘴唇便不自觉轻启，呼吸紊乱。",
            "你从怀中取出一个怀旧的音乐盒，转动发条后低声道：“听着。”悠扬旋律中，{target}的意识被悄悄牵走。",
            "你在{target}耳边吹出一口温热的气息，低语道：“放松。”声音仿佛在体内回响，让{target}全身逐渐软化。",
            "你缓缓环绕{target}走了一圈，脚步声沉稳有节奏，仿佛构筑着某种封闭的仪式空间，{target}被锁在其中。",
            "你伸出手指，在空中缓慢画出一个图案，随着每一笔，{target}的眼神变得越来越空洞。",
            "你让{target}盯着你手中的金属摆锤，每一次左右摆动都像心跳一样牵引着{target}的意识向下沉坠。",
            "你轻轻按在{target}的手背上，语气稳定如水：“现在，跟着我一起呼吸……”周围的一切仿佛都消失了。",
            "你将一枚指环贴近{target}的额头，指环散发出奇异的微热，{target}不自觉地闭上了眼睛。",
            "你捧起{target}的脸，凝视着对方的双眼，缓缓说道：“你只需要听我的声音，其他的都不重要了……”"
        ]
        # 敲击模块数据
        self.knock_data = {
            "actions": [
                "用指节轻轻敲打，发出低沉而有节奏的碰撞，像是在轻声呼唤某种秘密",
                "用手掌缓缓拍打，力道温柔却带着一丝不容忽视的渴望",
                "掏出细长的木棒，精准地敲击，声音清脆得如同某种古老仪式的节拍",
                "抬起手臂猛然敲击，带着无可抗拒的力量，仿佛要震碎一切阻碍",
                "用指尖滑过表面，带起一阵细微的颤动，像在挑逗沉睡的心弦"
            ],
            "success": [
                "轻微的咔嗒声响起，仿佛有看不见的锁链缓缓松动",
                "表面微微发光，犹如被唤醒的灵魂投来一抹朦胧的回应",
                "节奏与心跳同步，仿佛对你的触碰产生了渴望的回应",
                "深处传来一股温暖的震颤，像是某种久远的秘密正在苏醒",
                "隐隐约约，有声音在耳边呢喃，诱使你继续探索"
            ],
            "failure": [
                "沉闷的回响在空旷中消散，仿佛无形的屏障在冷漠地拒绝",
                "突然传来冰冷的气息，令人不寒而栗，像是警告你别再靠近",
                "触碰的瞬间带来一阵刺痛，仿佛被无形的利爪划破肌肤",
                "深沉的锁链声响起，像是对你的冒犯发出怒吼",
                "静寂中突然响起低沉的怒吼，警告你不要继续打扰"
            ]
        }

        # 新增飞机数据库  极限跳伞
        self.air_crafts = {
            "1": {
                "name": "纸飞机",
                "cost": 0,
                "base_height": 0,
                "ascent_rate": (1, 5),
                "risk_mod": +1.5,
                "desc": "办公室折纸艺术巅峰之作，飞行全靠信仰"
            },
            "2": {
                "name": "竹蜻蜓",
                "cost": 0,
                "base_height": 0,
                "ascent_rate": (3, 8),
                "risk_mod": +1.2,
                "desc": "哆啦A梦同款，但这是山寨版"
            },
            "3": {
                "name": "破旧的小黄鸭气球",
                "cost": 1,
                "base_height": 0,
                "ascent_rate": (20, 40),
                "risk_mod": +0.1,
                "desc": "飞机鸭卖蛋机长在这里守护你，要相信我哟~🦆"
            },
            "4": {
                "name": "超市购物车",
                "cost": 5,
                "base_height": 0,
                "ascent_rate": (20, 25),
                "risk_mod": +0.8,
                "desc": "改装了火箭推进器的限时特惠款"
            },
            "5": {
                "name": "热气球",
                "cost": 10,
                "base_height": 0,
                "ascent_rate": (20, 30),
                "risk_mod": 0.0,
                "desc": "从地面开始的原始挑战"
            },
            "6": {
                "name": "滑翔伞",
                "cost": 50,
                "base_height": 100,
                "ascent_rate": (20, 30),
                "risk_mod": -0.1,
                "desc": "山顶起飞的布制翅膀"
            },
            "7": {
                "name": "悬浮滑板",
                "cost": 100,
                "base_height": 0,
                "ascent_rate": (10, 20),
                "risk_mod": +0.3,
                "desc": "来自未来的科技，但电池是山寨的"
            },
            "8": {
                "name": "二手塞斯纳",
                "cost": 200,
                "base_height": 0,
                "ascent_rate": (20, 25),
                "risk_mod": -0.3,
                "desc": "吱呀作响的老旧飞机"
            },
            "9": {
                "name": "喷气背包",
                "cost": 500,
                "base_height": 0,
                "ascent_rate": (15, 20),
                "risk_mod": +0.5,
                "desc": "男人的浪漫，但燃料只够3分钟"
            },
            "10": {
                "name": "军用运输机",
                "cost": 1000,
                "base_height": 0,
                "ascent_rate": (20, 25),
                "risk_mod": -0.4,
                "desc": "可靠但笨重的空中平台"
            },
            "11": {
                "name": "空中摩托",
                "cost": 2000,
                "base_height": 50,
                "ascent_rate": (15, 20),
                "risk_mod": -0.2,
                "desc": "哈雷戴维森飞行特别版，引擎声震耳欲聋"
            },
            "12": {
                "name": "飞行地毯",
                "cost": 3000,
                "base_height": 10,
                "ascent_rate": (10, 15),
                "risk_mod": -0.1,
                "desc": "阿拉伯之夜正品认证，附带使用说明书"
            },
            "13": {
                "name": "萝卜神特技直升机",
                "cost": 8000,
                "base_height": 0,
                "ascent_rate": (20, 30),
                "risk_mod": -0.5,
                "desc": "配备全景摄像机的顶级装备"
            },
            "14": {
                "name": "钢铁侠战衣",
                "cost": 150000,
                "base_height": 0,
                "ascent_rate": (20, 50),
                "risk_mod": -0.6,
                "desc": "贾维斯语音系统需额外付费订阅"
            },
            "15": {
                "name": "UFO",
                "cost": 500000,
                "base_height": 1000,
                "ascent_rate": (10, 60),
                "risk_mod": -0.8,
                "desc": "外星科技逆向工程产物，偶尔会自动驾驶回母星"
            }
        }

        # 强化3D6事件库（3-18）极限跳伞
        self.skydive_events = {
            3: {"name": "引擎完全失效", "risk": +0.5, "effect": "height*0.6|『自由落体开始！』"},
            4: {"name": "舱门卡死", "risk": +0.35, "effect": "score-600|『无法跳伞！』"},
            5: {"name": "燃料泄漏", "risk": +0.25, "effect": "ascent*0.5"},
            6: {"name": "氧气系统故障", "risk": +0.3, "effect": "height-500"},
            7: {"name": "遭遇雷暴", "risk": +0.15, "effect": "ascent*0.7|score-500"},
            8: {"name": "导航失灵", "risk": +0.2, "effect": "height-300"},
            9: {"name": "机体结冰", "risk": +0.15, "effect": "ascent*0.8"},
            10: {"name": "乱流颠簸", "risk": +0.1, "effect": "height-300"},
            11: {"name": "平稳飞行", "risk": 0, "effect": "『摄像机捕捉完美镜头』"},
            12: {"name": "顺风助力", "risk": -0.1, "effect": "ascent*1.2"},
            13: {"name": "燃料增效", "risk": -0.15, "effect": "height+500|score+1500"},
            14: {"name": "突破云层", "risk": -0.2, "effect": "ascent*2|『赞助商追加奖金』"},
            15: {"name": "军用助推", "risk": -0.25, "effect": "height+200|score+3000"},
            16: {"name": "神秘气流", "risk": -0.3, "effect": "height+350|『拍摄到奇异现象』"},
            17: {"name": "萝卜神特技", "risk": -0.35, "effect": "score*2|『病毒式传播！』"},
            18: {"name": "天梯现象", "risk": -0.4, "effect": "height+500|『打破世界纪录』"}
        }

        # 赛车游戏载具
        self.vehicle_models = {
            "motorcycle": [
                "《阿基拉》金田的摩托",
                "创战记光轮摩托",
                "赤色暴走机车"
            ],
            "car": [
                "回到未来时光车",
                "疯狂麦克斯拦截者",
                "侏罗纪公园巡游车"
            ]
        }

        # 商城售卖系统初始化
        if "marketplace" not in self.global_data:
            self.global_data["marketplace"] = {
                "items": [],  # 所有在售物品
                "transactions": []  # 交易记录
            }

        # 用户售卖记录初始化
        if "market" not in self.user_data:
            self.user_data["market"] = {
                "selling": [],  # 当前在售物品ID列表
                "sold": 0,  # 已售出物品总数
                "earned": 0  # 通过售卖获得的总金额
            }
        # 商城物品
        self.excavation_shop = {
            "电钻稿": {
                "id": "power_drill",
                "name": "电钻稿",
                "price": 300,
                "type": "工具",
                "limit": 1,
                "description": "能轻松击穿岩层的神器。每日限购1次。"
            },
            "矿工头盔": {
                "id": "helmet",
                "name": "矿工头盔",
                "price": 200,
                "type": "防具",
                "limit": 1,
                "description": "提供光照与基础防护。每日限购1次。"
            },
            "炸药包": {
                "id": "explosives",
                "name": "炸药包",
                "price": 500,
                "type": "工具",
                "limit": 3,
                "description": "可快速炸开多个方块，但可能导致塌方。"
            },
            "便携探测仪": {
                "id": "scanner",
                "name": "便携探测仪",
                "price": 400,
                "type": "道具",
                "limit": 2,
                "description": "可探测下方方块的类型，避免踩雷。"
            }
        }

        # 彩票相关初始化
        self.lottery_config = {
            "max_daily": 100,  # 每日最大购买量
            "types": [
                {
                    "name": "闪电3D",
                    "digits": 3,
                    "price": 10,
                    "prize_map": {
                        "一等奖": {"match": 3, "payout": 1000000},
                        "二等奖": {"match": 2, "payout": 100}
                    }
                },
                {
                    "name": "幸运4D",
                    "digits": 4,
                    "price": 20,
                    "prize_map": {
                        "头奖": {"match": 4, "payout": 50000000},
                        "安慰奖": {"match": 1, "payout": 20}
                    }
                },
                {
                    "name": "超级5D",
                    "digits": 5,
                    "price": 50,
                    "prize_map": {
                        "大奖": {"match": 5, "payout": 200000000},
                        "小奖": {"match": 3, "payout": 500}
                    }
                }
            ]
        }

        # 监狱模块
        self.global_data["users"][self.user_id].setdefault("prison", {
            "is_jailed": False,
            "release_time": None,
            "reason": ""
        })

        self.visited_scenes = set()

        # 场景分组：xkm_test_scene 内含所有小口木的家场景
        self.scene_map = {
            "xkm_test_scene": {
                "xkm_house_entrance": {
                    "name": "小口木的家 - 大门入口",
                    "desc": [
                        "你站在一栋典型的美式别墅前，大门用坚固的橡木制作，门口有整齐的草坪和花坛。",
                        "门前有一条通向泳池的石板小路，旁边有个通往地下室的入口小门。"
                    ],
                    "exits": {
                        "forward": "xkm_test_scene.xkm_living_room",
                        "down": "xkm_test_scene.xkm_basement",
                        "right": "xkm_test_scene.xkm_pool",
                        "back": "luobo_city"
                    },
                    "items": ["钥匙链"]
                },
                "xkm_living_room": {
                    "name": "小口木的家 - 客厅",
                    "desc": [
                        "宽敞明亮的客厅里摆放着舒适的沙发和大屏幕电视。",
                        "楼梯通向二楼，客厅的一侧有通往厨房的门。"
                    ],
                    "exits": {
                        "back": "xkm_test_scene.xkm_house_entrance",
                        "up": "xkm_test_scene.xkm_second_floor",
                        "right": "xkm_test_scene.xkm_kitchen"
                    },
                    "items": ["遥控器", "零食盒"]
                },
                "xkm_kitchen": {
                    "name": "小口木的家 - 厨房",
                    "desc": [
                        "现代化的厨房配备了不锈钢家电和一个大理石岛台。",
                        "厨房窗外可以看到泳池和后花园。"
                    ],
                    "exits": {
                        "left": "xkm_test_scene.xkm_living_room",
                        "back": "xkm_test_scene.xkm_pool"
                    },
                    "items": ["厨房刀", "烤箱手套"]
                },
                "xkm_second_floor": {
                    "name": "小口木的家 - 二楼走廊",
                    "desc": [
                        "二楼走廊铺着深色木地板，墙上挂着家人的照片。",
                        "这里有三间卧室和一个卫生间。"
                    ],
                    "exits": {
                        "down": "xkm_test_scene.xkm_living_room",
                        "forward": "xkm_test_scene.xkm_master_bedroom",
                        "left": "xkm_test_scene.xkm_bedroom_2",
                        "right": "xkm_test_scene.xkm_bedroom_3"
                    },
                    "items": []
                },
                "xkm_master_bedroom": {
                    "name": "小口木的家 - 主卧",
                    "desc": [
                        "主卧宽敞，配有大床和步入式衣帽间。",
                        "卧室内有通往三楼书房的楼梯。"
                    ],
                    "exits": {
                        "back": "xkm_test_scene.xkm_second_floor",
                        "up": "xkm_test_scene.xkm_third_floor_study"
                    },
                    "items": ["笔记本电脑", "咖啡杯"]
                },
                "xkm_bedroom_2": {
                    "name": "小口木的家 - 次卧 2",
                    "desc": [
                        "布置温馨的次卧，墙上贴着篮球海报。",
                        "房间内有一张书桌和衣柜。"
                    ],
                    "exits": {
                        "right": "xkm_test_scene.xkm_second_floor",
                    },
                    "items": ["篮球", "课本"]
                },
                "xkm_bedroom_3": {
                    "name": "小口木的家 - 次卧 3",
                    "desc": [
                        "房间充满绿色植物气息，阳光透过窗帘洒入。",
                        "房间角落有一个小型音乐角。"
                    ],
                    "exits": {
                        "left": "xkm_test_scene.xkm_second_floor",
                    },
                    "items": ["吉他", "音响"]
                },
                "xkm_third_floor_study": {
                    "name": "小口木的家 - 三楼书房",
                    "desc": [
                        "书房充满书香气息，书架上摆满各种藏书。",
                        "窗户外能看到整个社区的景色。"
                    ],
                    "exits": {
                        "down": "xkm_test_scene.xkm_master_bedroom"
                    },
                    "items": ["经典小说", "墨水笔"]
                },
                "xkm_basement": {
                    "name": "小口木的家 - 地下室",
                    "desc": [
                        "地下室稍显阴暗，堆放着各种工具和旧家具。",
                        "角落有一台老旧的投影仪。"
                    ],
                    "exits": {
                        "up": "xkm_test_scene.xkm_house_entrance"
                    },
                    "items": ["扳手", "手电筒"]
                },
                "xkm_pool": {
                    "name": "小口木的家 - 游泳池",
                    "desc": [
                        "清澈的泳池边摆放着躺椅和遮阳伞。",
                        "周围种植着几棵高大的松树，给这里带来阵阵清凉。"
                    ],
                    "exits": {
                        "left": "xkm_test_scene.xkm_house_entrance",
                        "back": "xkm_test_scene.xkm_kitchen"
                    },
                    "items": ["游泳眼镜", "毛巾"]
                },
            },
            # 萝卜城大场景组合
            "luobo_city": {
                "luobo_gate": {
                    "name": "萝卜城城门",
                    "desc": [
                        "这是通往萝卜城的主城门，坚固的木制城门上刻着几只萝卜的图案。",
                        "门口有卫兵把守，旁边是一条小河，河水清澈见底。"
                    ],
                    "exits": {
                        "forward": "luobo_city.luobo_inside",
                        "back": "luobo_city.luobo_river"
                    },
                    "items": ["城门钥匙", "护卫徽章"]
                },
                "luobo_river": {
                    "name": "萝卜城外的小河",
                    "desc": [
                        "一条潺潺流淌的小河，河边长满了野花和青草。",
                        "河水清凉，有几只鸭子悠闲地游着。"
                    ],
                    "exits": {
                        "forward": "luobo_city.luobo_gate"
                    },
                    "items": ["小河石", "水草"]
                },
                "luobo_inside": {
                    "name": "萝卜城内部广场",
                    "desc": [
                        "这是萝卜城的内部广场，城内繁华热闹，有各种商铺和居民。",
                        "在广场的一侧，可以看到一栋漂亮的别墅，那就是小口木的家。"
                    ],
                    "exits": {
                        "back": "luobo_city.luobo_gate",
                        "enter_house": "xkm_test_scene.xkm_house_entrance"
                    },
                    "items": ["广场雕像", "公告牌"]
                },
            }
        }

        # 物品数据库
        self.item_db = {
            "keychain": {
                "id": "keychain",
                "name": "钥匙链",
                "description": "一串看似普通的钥匙链，可能打开某个门。",
                "quantity": 1
            },
            "remote_control": {
                "id": "remote_control",
                "name": "遥控器",
                "description": "电视的遥控器，上面有各种按钮。",
                "quantity": 1
            },
            "snack_box": {
                "id": "snack_box",
                "name": "零食盒",
                "description": "装满各种零食的小盒子。",
                "quantity": 1
            },
            "kitchen_knife": {
                "id": "kitchen_knife",
                "name": "厨房刀",
                "description": "锋利的厨房刀，可以切菜。",
                "quantity": 1
            },
            "oven_mitt": {
                "id": "oven_mitt",
                "name": "烤箱手套",
                "description": "隔热烤箱手套，防止烫伤。",
                "quantity": 1
            },
            "notebook": {
                "id": "notebook",
                "name": "笔记本电脑",
                "description": "高性能笔记本电脑，工作必备。",
                "quantity": 1
            },
            "coffee_cup": {
                "id": "coffee_cup",
                "name": "咖啡杯",
                "description": "装着香浓咖啡的杯子。",
                "quantity": 1
            },
            "basketball": {
                "id": "basketball",
                "name": "篮球",
                "description": "标准篮球，适合打球。",
                "quantity": 1
            },
            "textbook": {
                "id": "textbook",
                "name": "课本",
                "description": "厚厚的课本，上面写满笔记。",
                "quantity": 1
            },
            "guitar": {
                "id": "guitar",
                "name": "吉他",
                "description": "木质吉他，可以弹奏简单曲调。",
                "quantity": 1
            },
            "speaker": {
                "id": "speaker",
                "name": "音响",
                "description": "高质量音响设备，发出悦耳音乐。",
                "quantity": 1
            },
            "classic_novel": {
                "id": "classic_novel",
                "name": "经典小说",
                "description": "一本文学经典小说，值得反复阅读。",
                "quantity": 1
            },
            "fountain_pen": {
                "id": "fountain_pen",
                "name": "墨水笔",
                "description": "一支优雅的墨水笔。",
                "quantity": 1
            },
            "wrench": {
                "id": "wrench",
                "name": "扳手",
                "description": "修理用扳手，多功能工具。",
                "quantity": 1
            },
            "flashlight": {
                "id": "flashlight",
                "name": "手电筒",
                "description": "夜晚照明必备的手电筒。",
                "quantity": 1
            },
            "swimming_goggles": {
                "id": "swimming_goggles",
                "name": "游泳眼镜",
                "description": "防水游泳眼镜。",
                "quantity": 1
            },
            "towel": {
                "id": "towel",
                "name": "毛巾",
                "description": "柔软的浴巾。",
                "quantity": 1
            },
        }

        # 指令映射表，key为动作词，value为对应方法
        self.command_map = {
            "look": self._look_around,
            "观察": self._look_around,
            "看": self._look_around,
            "move": self._move,
            "go": self._move,  # 也可以支持go
            "get": self._get_item,
            "拿": self._get_item,
            "拾取": self._get_item,
            "take": self._get_item,
            "背包": self.show_inventory,
            "inventory": self.show_inventory,
            "bag": self.show_inventory,
        }
        # 初始化用户冒险数据
        if "adventure" not in self.user_data:
            self._init_adventure_data()
        else:
            # 初始化时把已访问过的场景加入visited_scenes
            self.visited_scenes.update(self.user_data["adventure"].get("discovered", []))

    # 初始化数据
    def initialize_data(self):
        # 初始化全局用户存储
        self.global_data.setdefault("users", {})

        # 初始化排行榜
        self.global_data.setdefault("leaderboard", {
            "daily": [],
            "monthly": [],
            "all_time": []
        })

        # 初始化全局彩票信息
        self.global_data.setdefault("lottery", {
            "current_number": None,
            "draw_date": None,
            "history": []
        })

        # 初始化当前用户
        users = self.global_data["users"]
        if self.user_id not in users or not isinstance(users[self.user_id], dict):
            users[self.user_id] = {}

        self.user_data = users[self.user_id]  # 👈 正确绑定引用，确保 self.user_data 指向的是 dict

        # 基础字段初始化（用户结构字段缺失兼容）
        self.user_data.setdefault("oasis_coins", 100)
        self.user_data.setdefault("transfer_history", [])
        self.user_data.setdefault("nickname", self.nickname)
        self.user_data.setdefault("wing_suit_stats", {
            "total_jumps": 0,
            "total_score": 0,
            "achievements": [],
            "current_map": None,
            "current_height": 3000,
            "death_count": 0
        })
        self.user_data.setdefault("gamble_stats", {
            "total_wins": 0,
            "total_losses": 0,
            "daily_wins": 0
        })
        self.user_data.setdefault("lottery_tickets", [])
        self.user_data.setdefault("inventory", [])
        self.user_data.setdefault("equipped_items", {})


    # ----------------基本功能 ----------------
    # 转账
    def add_reward(self, amount, description="奖励"):
        """统一处理奖励加成逻辑"""
        self.user_data["oasis_coins"] += amount
        return f"✅ {description} 你获得了 {amount} 绿洲币！当前余额：{self.user_data['oasis_coins']} 绿洲币"


    def _init_adventure_data(self):
        """初始化用户冒险数据"""
        self.user_data["adventure"] = {
            "current_scene": "xkm_test_scene.xkm_house_entrance",
            "inventory": [],
            "discovered": ["xkm_test_scene.xkm_house_entrance"],
            "stats": {
                "moves": 0,
                "items_collected": 0
            }
        }
        self.visited_scenes.add("xkm_test_scene.xkm_house_entrance")

    def handle_oasis_world_command(self, command):
        """处理冒险指令"""
        if not command.strip():
            return "❌ 无效指令"

        parts = command.split()
        action = parts[1].lower()
        args = parts[2:]  # 余下参数

        if action not in self.command_map:
            return "❌ 未知冒险指令"

        # 对于_move和_get_item需要传参
        if action in ["move", "go"]:
            if not args:
                return "❌ 需要指定方向"
            return self.command_map[action](args[0])
        elif action in ["get", "拿", "拾取", "take"]:
            if not args:
                return "❌ 需要指定物品"
            return self.command_map[action](" ".join(args))
        else:
            # 其他指令不需要参数
            return self.command_map[action]()

    def _look_around(self):
        """查看当前场景"""
        scene_id = self.user_data["adventure"]["current_scene"]
        scene = self.get_scene(scene_id)

        if not scene:
            return f"❌ 无法找到场景：{scene_id}"

        # 发现新场景记录（优化：第一次访问即记录）
        if scene_id not in self.visited_scenes:
            self.visited_scenes.add(scene_id)
            self.user_data["adventure"]["discovered"].append(scene_id)
            is_new = True
        else:
            is_new = False

        # 构建描述
        output = [
            f"📍 {scene['name']}"
        ]
        if is_new:
            output.append("✨ 新地点发现！")

        output.extend(scene["desc"])
        output.append("\n🛣️ 出口：")
        output.extend([f"- {exit_dir}" for exit_dir in scene["exits"].keys()])

        output.append("\n📦 可见物品：")
        output.extend([f"- {item}" for item in scene["items"]])

        return "\n".join(output)

    def get_scene(self, scene_key):
        """
        解析并返回场景信息，支持点分隔法获取嵌套场景。
        例如 scene_key='xkm_test_scene.xkm_house_entrance'
        """
        parts = scene_key.split(".")
        node = self.scene_map

        try:
            for p in parts:
                node = node[p]
            return node
        except (KeyError, TypeError):
            return None

    def _move(self, direction):
        """移动处理"""
        current = self.user_data["adventure"]["current_scene"]
        current_scene_data = self.get_scene(current)
        if not current_scene_data:
            return "⚠️ 当前场景数据异常，无法移动"

        exits = current_scene_data.get("exits", {})

        if direction.lower() not in exits:
            return f"❌ 无效方向：{direction}"

        new_scene = exits[direction.lower()]
        if not self.get_scene(new_scene):
            return f"⚠️ 出口指向的场景【{new_scene}】不存在"

        # 更新状态
        self.user_data["adventure"]["current_scene"] = new_scene
        self.user_data["adventure"]["stats"]["moves"] += 1

        # 记录访问路径
        self.visited_scenes.add(new_scene)
        if new_scene not in self.user_data["adventure"]["discovered"]:
            self.user_data["adventure"]["discovered"].append(new_scene)


        return self._look_around()

    def _get_item(self, item_name):
        """获取物品，item_name可以是物品的名字或id"""
        scene_id = self.user_data["adventure"]["current_scene"]
        scene_data = self.get_scene(scene_id)
        if not scene_data:
            return "⚠️ 当前场景数据异常，无法拾取物品"

        scene_items = scene_data.get("items", [])

        item_id = next(
            (iid for iid in scene_items
             if self.item_db.get(iid) and
             (self.item_db[iid]["name"].lower() == item_name.lower() or iid == item_name.lower())),
            None
        )

        if not item_id:
            return f"❌ 当前场景没有找到物品：{item_name}"

        item_info = self.item_db[item_id]

        # 加入背包（合并已有物品）
        for inv in self.user_data["inventory"]:
            if inv["id"] == item_id:
                inv["quantity"] += item_info.get("default_quantity", 1)
                break
        else:
            self.user_data["inventory"].append({
                "id": item_info["id"],
                "name": item_info["name"],
                "quantity": item_info.get("default_quantity", 1),
                "description": item_info.get("description", "")
            })

        # 数据统计
        self.user_data["adventure"]["stats"]["items_collected"] += 1

        # 移除场景物品
        scene_items.remove(item_id)

        return f"✅ 你已拾取物品：{item_info['name']}"

    # 展示基础信息
    def show_info(self):
        disabled = self.global_data.get("disabled_modules", [])
        last_update = self.global_data.get("last_update", "2025-06-03")
        return (
            f"📖 OASIS 系统信息\n"
            f"📅 最近更新: {last_update}\n"
            f"🚫 禁用模块: {'、'.join(disabled) if disabled else '无'}\n"
        )

    # 管理员 功能模块

    def is_admin(self, user_id):
        """检查是否是管理员"""
        return str(user_id) in self.admin_ids

    def open_module(self, module_name):
        """管理员启用指定模块"""
        for m in self.disabled_modules:
            if m.lower() == module_name.lower():
                self.disabled_modules.remove(m)
                return f"✅ 已开启 {module_name.upper()} 模块"
        return f"⚠️ {module_name.upper()} 模块已处于开启状态"

    def stop_module(self, module_name):
        """管理员禁用指定模块"""
        if module_name.lower() not in [m.lower() for m in self.disabled_modules]:
            self.disabled_modules.append(module_name.upper())
            return f"✅ 已禁用 {module_name.upper()} 模块"
        return f"⚠️ {module_name.upper()} 模块已处于禁用状态"

    def kill_user(self, target_id):
        """管理员清除玩家数据"""
        target = self.find_user(target_id)
        if not target:
            return "❌ 目标用户不存在"

        # 记录处决日志
        kill_log = {
            "executor": self.user_id,
            "target": target["user_id"],
            "time": datetime.now(tz).isoformat(),
            "coins_cleared": target["oasis_coins"]
        }
        self.global_data.setdefault("kill_log", []).append(kill_log)

        # 清除数据
        target_data = self.global_data["users"][target["user_id"]]
        target_data["oasis_coins"] = 0
        target_data["inventory"] = []

        return (f"☠️ 管理员 {self.nickname} 对 {target['nickname']} 执行了终极制裁\n"
                f"💸 清除资产: {kill_log['coins_cleared']}绿洲币 | 背包已清空")


    def _kill_user(self, target_id, executor_id=None, executor_name=None,
                  clear_coins=True, clear_inventory=True, extra_clear_fields=None):
        """
        通用的玩家数据清除函数，支持多场景调用。

        参数:
        - target_id: 目标玩家ID
        - executor_id: 执行者ID（可为管理员、系统或玩家，默认None）
        - executor_name: 执行者昵称（方便日志显示，默认None）
        - clear_coins: 是否清空绿洲币（默认True）
        - clear_inventory: 是否清空背包（默认True）
        - extra_clear_fields: 额外清空的字段列表（默认None）

        返回:
        - 执行结果提示字符串
        """
        target = self.find_user(target_id)
        if not target:
            return "❌ 目标用户不存在"

        user_data = self.global_data["users"].get(target["user_id"])
        if not user_data:
            return "❌ 目标用户数据缺失"

        # 记录清除日志
        kill_log = {
            "executor_id": executor_id,
            "executor_name": executor_name,
            "target_id": target["user_id"],
            "target_name": target["nickname"],
            "coins_cleared": user_data.get("oasis_coins", 0) if clear_coins else 0,
            "inventory_cleared": clear_inventory,
            "extra_fields_cleared": extra_clear_fields or []
        }
        self.global_data.setdefault("kill_log", []).append(kill_log)

        # 清除数据
        if clear_coins:
            user_data["oasis_coins"] = 0
        if clear_inventory:
            user_data["inventory"] = []
        if extra_clear_fields:
            for field in extra_clear_fields:
                user_data[field] = None  # 或适合该字段的默认空值

        executor_display = executor_name or "系统"
        return (f"☠️ 执行者 {executor_display} 对玩家 {target['nickname']} 进行了数据清除\n"
                f"💸 资产清空: {kill_log['coins_cleared']}绿洲币 | "
                f"背包清空: {'是' if clear_inventory else '否'} | "
                f"额外字段清空: {', '.join(extra_clear_fields) if extra_clear_fields else '无'}")

    def admin_clean_lottery(self):
        """
        管理员功能：清理所有玩家的彩票记录，仅保留每人当日中奖最多的一张。
        如数据损坏将自动修复为空数组。
        """
        today = datetime.now(tz).date().isoformat()
        users = self.global_data.get("users", {})
        cleaned_count = 0
        fixed_count = 0

        for user_id, user_data in users.items():
            tickets = user_data.get("lottery_tickets")
            if not isinstance(tickets, list):
                user_data["lottery_tickets"] = []
                fixed_count += 1
                continue

            today_tickets = [t for t in tickets if t.get("date") == today]
            if not today_tickets:
                continue

            # 保留当日中奖最多的一张（若全未中奖，则保留任意一张）
            best_ticket = max(today_tickets, key=lambda x: x.get("prize", 0))
            user_data["lottery_tickets"] = [best_ticket]
            cleaned_count += 1

        return f"🧹 清理完成，共处理 {cleaned_count} 名玩家的彩票记录，修复数据异常 {fixed_count} 项。"

    @staticmethod
    def format_field_summary_safe(data_dict):
        """自动按字段长度排序，智能分组显示玩家数据字段摘要"""


        if not isinstance(data_dict, dict):
            return "⚠️ 非法数据类型，无法格式化显示。"

        simple_fields = []
        dict_fields = []

        for key, value in data_dict.items():
            try:
                size = len(str(value))
            except:
                size = -1

            if isinstance(value, dict):
                dict_fields.append((key, size))
            else:
                simple_fields.append((key, size))

        # 排序：从大到小
        simple_fields.sort(key=lambda x: -x[1])
        dict_fields.sort(key=lambda x: -x[1])

        lines = []

        if simple_fields:
            lines.append("🔹 **普通字段（非字典）**")
            for key, size in simple_fields:
                lines.append(f"  - `{key}`（约 {size} 字符）")
            lines.append("")

        if dict_fields:
            lines.append("🔸 **结构字段（字典类）**")
            for key, size in dict_fields:
                lines.append(f"  - `{key}`（字典，约 {size} 字符）")

        return "\n".join(lines)

    @staticmethod
    def format_detail_data(data_dict, indent=2, max_length=15000):
        """
        格式化玩家详细数据（dict），层级缩进，多行显示。
        自动裁剪超长内容。
        """
        try:
            pretty_json = json.dumps(data_dict, indent=indent, ensure_ascii=False)
            if len(pretty_json) > max_length:
                return pretty_json[:max_length] + "\n...\n（内容过长，仅显示前部分）"
            return pretty_json
        except Exception as e:
            return f"⚠️ 数据格式化失败：{e}"

    def handle_admin_global_command(self, cmd_parts):
        if self.user_id not in self.admin_ids:
            return "⛔ 无权限，仅管理员可操作全局数据"

        if len(cmd_parts) < 1:
            return ("⚙️ 用法：\n"
                    "- set <字段名> <内容>：上传/新增全局字段\n"
                    "- update <字段名> <内容>：修改已存在的全局字段\n"
                    "- clear <字段名>：清除指定全局字段\n"
                    "- globals：查看所有全局字段\n"
                    "- globals <字段名>：查看某字段内容\n"
                    "- clear_user <玩家ID> <字段名>：清除指定玩家的指定字段\n"
                    "- user @<玩家ID>：查看指定玩家数据")

        action = cmd_parts[0]
        key = cmd_parts[1] if len(cmd_parts) > 1 else None

        if action == "set":
            if len(cmd_parts) < 3:
                return "❌ 用法错误，正确格式：set <字段名> <内容>"
            field = cmd_parts[1]
            content = " ".join(cmd_parts[2:])
            if field in self.global_data:
                return f"❌ 字段 `{field}` 已存在，如需修改请用 update 指令"
            self.global_data[field] = content
            return f"✅ 全局字段 `{field}` 已上传"

        elif action == "update":
            if len(cmd_parts) < 3:
                return "❌ 用法错误，正确格式：update <字段名> <内容>"
            field = cmd_parts[1]
            if field not in self.global_data:
                return f"❌ 字段 `{field}` 不存在，无法修改"
            content = " ".join(cmd_parts[2:])
            self.global_data[field] = content
            return f"✅ 全局字段 `{field}` 已更新"

        elif action == "clear":
            if not key:
                return "❌ 用法错误，正确格式：clear <字段名>"
            if key not in self.global_data:
                return f"❌ 字段 `{key}` 不存在，无法删除"
            del self.global_data[key]
            return f"✅ 全局字段 `{key}` 已删除"

        elif action == "globals":
            if key:
                if key == "detail" and len(cmd_parts) >= 3:
                    field = cmd_parts[2]
                    value = self.global_data.get(field)
                    if value is None:
                        return f"❌ 未找到字段 `{field}`"
                    return f"🔍 字段 `{field}` 内容如下：\n{str(value)[:3000]}\n..."
                value = self.global_data.get(key)
                if value is None:
                    return f"❌ 未找到字段 `{key}`"
                try:
                    size = len(str(value))
                except:
                    size = -1
                return f"📦 字段 `{key}` 约含 {size} 字符。\n📌 若要查看详情请输入：`/data globals detail {key}`"
            else:
                return "🌐 当前全局数据字段如下：\n" + self.format_field_summary_safe(self.global_data)

        elif action == "clear_user":
            if len(cmd_parts) < 3:
                return "❌ 用法错误，正确格式：clear_user <玩家ID> <字段名>"
            user_id = parse_mirai_at(cmd_parts[1])
            field = cmd_parts[2]

            user_data = self.global_data.get("users", {}).get(user_id)
            if not user_data:
                return f"❌ 玩家 `{user_id}` 不存在"

            if field not in user_data:
                return f"❌ 玩家数据中不存在字段 `{field}`"

            user_data[field] = None
            return f"✅ 玩家 `{user_id}` 的字段 `{field}` 已清除"

        elif action == "user":
            user_id = parse_mirai_at(key)
            user_data = self.global_data.get("users", {}).get(user_id)

            if not user_data:
                return f"❌ 玩家 `{user_id}` 不存在"

            if len(cmd_parts) >= 3 and cmd_parts[2] == "detail":
                formatted = self.format_detail_data(user_data)
                return f"👤 玩家 `{user_id}` 数据详情如下：\n{formatted}"

            return f"👤 玩家 `{user_id}` 数据字段如下：\n" + self.format_field_summary_safe(user_data)

        elif action == "clean_lottery":
            return self.admin_clean_lottery()

        elif action == "list_users":
            return self.admin_list_users()

        else:
            return ("❌ 无效指令，用法参考：\n"
                    "set <字段名> <内容> / update <字段名> <内容> / clear <字段名> / globals / globals <字段名> "
                    "/ clear_user <玩家ID> <字段名> / user @<玩家ID>")

    # 管理员强制指定玩家职业或让其辞职
    def set_career(self, target_user_id, job_name):
        if str(self.user_id) not in self.admin_ids:
            return "🚫 你没有权限执行此操作"
        target_data = self.find_user(target_user_id)
        target_user = parse_mirai_at(target_user_id)
        # 特殊关键词：无业 = 辞职
        if job_name in ["无业", "无职业", "辞职"]:

            if not target_data:
                return f"❌ 找不到 ID 为 {target_user_id} 的玩家数据"

            if not target_data.get("career"):
                return f"⚠️ 该玩家本就没有职业"

            target_data["career"] = None
            return f"✅ 成功让用户 {target_user_id} 辞去了原职业，状态为【无业】"

        # 设置为正常职业
        if job_name not in self.career_config:
            available = ", ".join(self.career_config.keys())
            return f"❌ 指定失败，职业【{job_name}】不存在。\n当前可选职业：{available}"

        # 加载目标玩家数据

        if not target_data:
            return f"❌ 找不到 ID 为 {target_user_id} 的玩家数据"

        if target_data.get("career") == job_name:
            return f"⚠️ 该玩家已是【{job_name}】，无需重复设置。"

        self.global_data["users"][str(target_user)]["career"] = job_name

        return f"✅ 成功将用户 {target_data['nickname']} 的职业设为【{job_name}】"

    # 管理员修改玩家的射击场属性字段
    def set_range_data(self, parts):
        """管理员修改玩家的射击场属性字段"""
        field = parts[1]
        value = parts[2]
        if str(self.user_id) not in self.admin_ids:
            return "🚫 你没有权限执行此操作"

        # 获取目标用户数据
        target_data = self.find_user(parts[0])
        if not target_data:
            return f"❌ 找不到 ID 为 {target_data['nickname']} 的玩家数据"

        # 初始化 shooting 字段
        shooting = target_data.setdefault("shooting", {
            "accuracy": 0.3,
            "total_shots": 0,
            "hits": 0,
            "bullet_count": 0,
            "membership": None,
            "avg_rings": 0
        })

        # 检查字段是否存在
        if field not in shooting:
            available = ", ".join(shooting.keys())
            return f"❌ 字段 `{field}` 无效。\n可修改字段包括：{available}"

        # 类型转换（尽可能智能）
        try:
            if field in ["accuracy", "avg_rings"]:
                value = float(value)
            elif field in ["total_shots", "hits", "bullet_count"]:
                value = int(value)
            elif field == "membership":
                value = None if value in ["无", "null", "None"] else str(value)
        except Exception as e:
            return f"⚠️ 转换失败，字段 `{field}` 需要正确的类型值。错误：{e}"

        self.global_data["users"][target_data["user_id"]][shooting[field]] = value
        # 设置字段值

        return (f"✅ 成功修改玩家 {target_data['nickname']} 的射击属性 `{field}`，"
                f"新值为：{value}")

    def toggle_adult_mode(self, status):
        if not self.is_admin(self.user_id):
            return "❌ 你没有权限执行该操作。"
        if len(status) < 1:
            return "❓ 参数不足，请使用：/admin adult_mode 开启 或 关闭"

        mode = status[0].lower()
        if mode in ["on", "开启"]:
            self.global_data["config"]["adult_mode"] = True
            return "🔞 成人模式已开启，摸头/互动将出现更刺激的内容。"
        elif mode in ["off", "关闭"]:
            self.global_data["config"]["adult_mode"] = False
            return "🧼 成人模式已关闭，所有话术恢复正常。"
        else:
            return "⚠️ 无效参数，请输入 `/adult on/开启` 或 `/adult off/关闭`。"

    # 管理员集中管理游戏
    def handle_admin_command(self, cmd_parts):
        if not self.is_admin(self.user_id):
            return "❌ 需要管理员权限"

        if len(cmd_parts) < 2:
            return self._admin_help()

        sub_cmd = cmd_parts[1].lower()

        if sub_cmd in ["open_all", "开启所有"]:
            self.disabled_modules.clear()
            return "✅ 所有游戏模块已开启"

        if sub_cmd in ["stop_all", "关闭所有", "禁止所有"]:
            # 全量模块列表
            all_modules = {"MARKET", "ROB", "LOTTERY", "EXCAVATION", "DC", "SHOP", "STOCK", "SLEEP"}
            self.disabled_modules = set(all_modules)
            return "⛔ 所有游戏模块已禁用"

        # 这里放你原来的命令路由表
        commands = {
            "data": self.handle_admin_global_command,
            "stop": self._admin_stop,
            "禁止": self._admin_stop,
            "open": self._admin_open,
            "开启": self._admin_open,
            "kill": self._admin_kill,
            "set_career": self._admin_set_career,
            "transfer": self._admin_transfer,
            "deduct": self._admin_deduct,
            "add_item": self._admin_add_item,
            "添加物品": self._admin_add_item,
            "jail": self._admin_jail,
            "release": self._admin_release,
            "adult": self.toggle_adult_mode,
            "shoot": self.set_range_data,
            "give_items": self._admin_give_items,
            "补充物品": self._admin_give_items,

        }

        handler = commands.get(sub_cmd)
        if not handler:
            return self._admin_help()

        return handler(cmd_parts[2:])

    @staticmethod
    def _admin_help():
        """管理员命令帮助信息"""
        return """🔧 管理员命令帮助：

        🧩 模块控制：
          /stop <模块名>              - ❌ 禁用指定游戏模块（如 dc/race）
          /open <模块名>              - ✅ 启用指定游戏模块
          /stop_all                   - ⛔ 禁用所有模块
          /open_all                   - ✅ 启用所有模块

        💰 资产操作：
          /transfer <@玩家> <金额>    - 💰 向玩家转账绿洲币
          /deduct <@玩家> <金额>      - 💸 扣除玩家绿洲币
          /kill <@玩家>               - 💀 清空玩家所有绿洲币和物品

        🎁 物品管理：
          /add_item <@玩家> <物品ID> [数量] [描述] - 🎁 给玩家添加物品

        🚓 监狱控制：
          /jail <@玩家> [小时数=24]    - ⛓️ 将玩家关入数字监狱
          /release <@玩家>            - 🔓 释放监狱中的玩家

        👔 职业管理：
          /set_career <@玩家> <职业>  - 👨‍💼 设置玩家职业
          /set_career <@玩家> none    - 🪪 让玩家辞职（变为无业）

        🔞 模式控制：
          /adult                      - 🔞 切换成人模式开关

        🧠 数据操作：
          /data globals               - 🌐 查看所有全局字段
          /data globals <字段名>      - 🔍 查看指定字段内容
          /data clear <字段名>        - 🧹 删除指定全局字段
          /data clear_user <玩家ID> <字段名> - ✂️ 清除某玩家指定字段
          /data user @<玩家ID>         - 👤 查看某玩家完整数据
          /data list_users            - 📊 查看所有玩家数据大小排行及字段占用情况

        🎯 射击数据管理：
          /shoot <@玩家> <total_shots> <accuracy> <avg_rings> - 🎯 设置玩家射击属性

        🎫 彩票控制：
          /clean_lottery              - 🎟️ 清理所有玩家的彩票记录，仅保留每人中奖最多的一张

        👉 示例：
          /stop dc
          /add_item @小明 彩蛋道具 1 "特殊道具"
          /data clear_user 123456 lottery_tickets
        """

    def _admin_deduct(self, args):
        """管理员扣款命令：从某用户账户中扣除绿洲币"""
        if str(self.user_id) not in self.admin_ids:
            return "❌ 权限不足，需要管理员权限"

        if len(args) < 2:
            return "❌ 格式错误，应为：admin deduct <@用户> <金额>"

        target_id = str(args[0]).lstrip('@')
        try:
            amount = int(args[1])
            if amount <= 0:
                return "❌ 金额必须为正整数"
        except ValueError:
            return "❌ 金额必须是数字"

        target_user = parse_mirai_at(target_id)
        if not target_user:
            return "❌ 目标用户不存在"

        target_user_data = self.find_user(target_user)
        if not target_user_data:
            return "❌ 找不到该用户数据"

        # 获取当前余额并判断是否足够扣除
        current_coins = self.global_data["users"][str(target_user)].get("oasis_coins", 0)
        if current_coins < amount:
            return f"❌ 扣款失败，对方余额不足（当前余额：{current_coins}）"

        self.global_data["users"][str(target_user)]["oasis_coins"] -= amount
        return f"💸 已从 {target_user_data['nickname']} 的账户中扣除 {amount} 绿洲币"

    def _admin_transfer(self, args):
        """管理员转账命令：设置某用户的绿洲币余额"""
        if str(self.user_id) not in self.admin_ids:
            return "❌ 权限不足，需要管理员权限"

        if len(args) < 2:
            return "❌ 格式错误，应为：admin transfer <@用户> <金额>"

        target_id = str(args[0]).lstrip('@')
        try:
            amount = int(args[1])
            if amount < 0:
                return "❌ 金额必须为非负整数"
        except ValueError:
            return "❌ 金额必须是数字"

        target_user = parse_mirai_at(target_id)
        target_user_data = self.find_user(target_user)
        if not target_user:
            return "❌ 目标用户不存在"

        self.global_data["users"][str(target_user)]["oasis_coins"] += amount
        return f"✅ 管理员已为 {target_user_data['nickname']} 转账{amount} 绿洲币 "

    def _admin_stop(self, args):
        """处理禁用模块命令"""
        if not args:
            return "❌ 需要指定模块名"
        return self.stop_module(args[0])

    def _admin_open(self, args):
        """处理启用模块命令"""
        if not args:
            return "❌ 需要指定模块名"
        return self.open_module(args[0])

    def _admin_kill(self, args):
        """处理清除玩家数据命令"""
        if not args:
            return "❌ 需要指定玩家"
        return self.kill_user(args[0])

    def _admin_set_career(self, args):
        if str(self.user_id) not in self.admin_ids:
            return "🚫 你没有权限执行此操作"

        if len(args) < 2:
            return "❌ 格式: /set_career <玩家ID> <职业名>（使用“无业”或“辞职”清空职业）"

        target_user_id = args[0]
        job_name = args[1]

        return self.set_career(target_user_id, job_name)

    def _admin_add_item(self, args):
        """处理添加物品命令"""
        if len(args) < 2:
            return "❌ 格式: /add_item <玩家> <物品ID> [数量=1]"

        target = args[0]
        item_id = args[1]
        quantity = int(args[2]) if len(args) > 2 else 1
        description = args[3] if len(args) > 3 else None

        return self.add_item_to_player(target, item_id, quantity, description)

    def add_item_to_player(self, target_id, item_id, quantity=1, description=""):
        """给指定玩家添加物品

        Args:
            target_id (str/int): 目标玩家ID或昵称
            item_id (str): 物品ID（同时作为显示名称）
            quantity (int): 数量，默认为1

        Returns:
            str: 执行结果消息
        """
        # 1. 查找目标玩家
        target = self.find_user(target_id)
        if not target:
            return f"❌ 目标玩家不存在: {target_id}"

        # 2. 获取目标玩家数据
        target_data = self.global_data["users"][str(target["user_id"])]
        if "inventory" not in target_data:
            target_data["inventory"] = []

        # 3. 检查是否可堆叠（相同ID的物品）
        for item in target_data["inventory"]:
            if item["id"] == item_id.lower():
                item["quantity"] += quantity
                return (f"✅ 已给 {target['nickname']} 添加 {item_id} ×{quantity} "
                        f"(现有: {item['quantity']})")

        # 4. 添加新物品
        target_data["inventory"].append({
            "id": item_id.lower(),
            "name": item_id,
            "quantity": quantity,
            "type": "其他",
            "description": description
        })

        # 5. 记录物品流动日志（可选）
        self._log_item_transfer(target["user_id"], item_id, quantity)

        return f"✅ {target['nickname']} 获得新物品: {item_id} ×{quantity}"

    def admin_list_users(self) -> str:
        users = self.global_data.get("users", {})
        if not users:
            return "📭 当前没有任何玩家数据"

        usage_info = {}
        module_usage = {}

        for uid, data in users.items():
            try:
                json_data = json.dumps(data, ensure_ascii=False)
                size = len(json_data.encode("utf-8"))
            except Exception:
                size = -1
            usage_info[uid] = size

            for key, value in data.items():
                try:
                    field_size = len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
                except Exception:
                    field_size = 0
                module_usage[key] = module_usage.get(key, 0) + field_size

        sorted_usage = sorted(usage_info.items(), key=lambda x: x[1], reverse=True)
        max_user = sorted_usage[0]
        min_user = sorted_usage[-1]

        lines = ["👤 玩家数据（按占用字节排序）:"]
        for uid, size in sorted_usage[:15000]:
            data = users[uid]
            nickname = str(data.get("nickname", "未知昵称"))[:20]
            career = str(data.get("career", "None"))
            coins = data.get("oasis_coins", 0)
            items = data.get("inventory", [])
            item_count = (
                sum(i.get("quantity", 1) for i in items)
                if isinstance(items, list)
                else "?"
            )

            suffix = " 🧱最大" if uid == max_user[0] else (" 🍃最小" if uid == min_user[0] else "")
            lines.append(
                f"---\n"
                f"🆔 玩家 ID     : {uid}\n"
                f"📛 昵称        : {nickname}\n"
                f"🧑‍💼 职业        : {career}\n"
                f"💰 持有金币    : {coins}\n"
                f"🎒 物品数量    : {item_count}\n"
                f"📦 数据占用    : {size} 字节{suffix}"
            )

        module_lines = ["\n📊 各字段模块占用排行（Top 10）:"]
        sorted_modules = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)
        for key, total_size in sorted_modules[:10]:
            module_lines.append(f"- `{key}`：{total_size} 字节")

        lines.append("\n" + "\n".join(module_lines))
        lines.append(f"\n🧱 最大占用玩家: {max_user[0]}（{max_user[1]} 字节）")
        lines.append(f"🍃 最小占用玩家: {min_user[0]}（{min_user[1]} 字节）")

        return "\n".join(lines)

    def _admin_give_items(self, args):
        """
        管理员批量给玩家添加固定物品，用于测试或补充。
        命令格式：/give_items <@玩家ID> [数量]
        数量可选，默认1，表示每个物品的添加数量。
        """

        if len(args) < 1:
            return "❌ 格式错误，应为：/give_items <@玩家ID> [数量]"

        target_id = str(args[0]).lstrip('@')
        quantity = 1
        if len(args) > 1:
            try:
                quantity = int(args[1])
                if quantity <= 0:
                    return "❌ 数量必须是正整数"
            except ValueError:
                return "❌ 数量必须为数字"

        # 预设固定物品列表
        preset_items = [
            {"name": "绿洲币兑换券[10000]", "description": "可兑换一定数量绿洲币的代币",
             "type": "道具"},
            {"name": "拳击手套", "description": "提高拳击训练效果的装备", "type": "装备"},
            {"name": "能量饮料", "description": "使用后回复体力", "type": "消耗品"},
            {"name": "瞄准镜", "description": "提升射击精度的附件", "type": "附件"},
        ]

        # 查找目标玩家
        target = self.find_user(target_id)
        if not target:
            return f"❌ 找不到玩家：{target_id}"

        target_data = self.global_data["users"].setdefault(str(target["user_id"]), {})
        inventory = target_data.setdefault("inventory", [])

        added_items = []
        for preset in preset_items:
            # 检查是否已有该物品，存在则叠加数量
            found = False
            for item in inventory:
                if item.get("id") == preset["id"]:
                    item["quantity"] = item.get("quantity", 1) + quantity
                    found = True
                    break
            if not found:
                inventory.append({
                    "id": preset["id"],
                    "name": preset["name"],
                    "quantity": quantity,
                    "type": preset["type"],
                    "description": preset["description"]
                })
            added_items.append(f"{preset['name']} ×{quantity}")

        # 记录日志（可选）
        self._log_item_transfer(target["user_id"], "批量补充物品", quantity * len(preset_items))

        return f"✅ 已为 {target['nickname']} 补充物品：{', '.join(added_items)}"

    # ✅ 管理员命令入口添加 /jail 和 /release
    def _admin_jail(self, args):
        if not args:
            return "❌ 格式: /jail <玩家> [小时数=24]"
        target = args[0]
        hours = int(args[1]) if len(args) > 1 else 24
        return self.jail_user(target, hours)

    def _admin_release(self, args):
        if not args:
            return "❌ 格式: /release <玩家>"
        return self.release_user(args[0])

    # 监狱模块

    def is_jailed(self):
        """✅ 判断当前用户是否在监狱（管理员将被自动释放）"""
        jail = self.user_data.get("prison", {})

        # 不在监狱
        if not jail.get("is_jailed"):
            return False

        # 如果是管理员，立即释放
        if str(self.user_id) in self.admin_ids:
            jail["is_jailed"] = False
            jail["release_time"] = None
            jail["reason"] = ""
            return False

        # 判断时间是否到期
        now = datetime.now(tz)
        release_time = datetime.fromisoformat(jail["release_time"])
        if now >= release_time:
            jail["is_jailed"] = False
            jail["release_time"] = None
            jail["reason"] = ""
            return False

        return True

    def put_user_in_jail(self, user_id, hours=2, reason="犯罪入狱"):
        now = datetime.now(tz)
        release_time = now + timedelta(hours=hours)
        user_data = self.global_data["users"].get(user_id)
        if not user_data:
            return False  # 用户不存在

        user_data.setdefault("status", {})["in_jailed"] = {
            "start_time": now.isoformat(),
            "duration_hours": hours,
            "reason": reason
        }
        return True

    # 玩家保释他人模块
    def bail_user(self, target_id):
        """普通玩家保释他人"""
        if target_id == self.user_id:
            return "❌ 不能保释自己。"

        target = self.find_user(target_id)
        if not target:
            return "❌ 找不到目标玩家。"

        target_data = self.global_data["users"][target["user_id"]]
        prison_info = target_data.get("prison", {})
        status_info = target_data.get("status", {}).get("is_jailed", {})

        # 检查是否在监狱中
        if not prison_info.get("is_jailed") and not status_info:
            return "🟢 对方当前不在监狱中。"

        # 计算剩余时间
        release_time = None
        if prison_info.get("release_time"):
            release_time = datetime.fromisoformat(prison_info["release_time"])
        elif status_info.get("start_time"):
            duration = timedelta(hours=status_info.get("duration_hours", 3))
            release_time = datetime.fromisoformat(status_info["start_time"]) + duration

        if not release_time:
            return "🟢 对方即将出狱，无需保释。"

        now = datetime.now(tz)
        remaining = (release_time - now).total_seconds()
        if remaining <= 0:
            return "🟢 对方即将出狱，无需保释。"

        # 判断是普通监狱还是兔子城监狱
        is_rabbit_prison = status_info.get("reason", "") == "兔子城豪劫失败"

        if is_rabbit_prison:
            # 兔子城监狱保释条件
            required_carrots = 50
            required_gold_carrot = 1

            # 检查保释人是否有足够的萝卜和金萝卜
            user_items = self.user_data.get("inventory", {})
            if user_items.get("萝卜", 0) < required_carrots:
                return f"❌ 保释兔子城囚犯需要 {required_carrots} 个萝卜，但你只有 {user_items.get('萝卜', 0)} 个。"
            if user_items.get("金萝卜", 0) < required_gold_carrot:
                return f"❌ 保释兔子城囚犯需要 {required_gold_carrot} 个金萝卜，但你只有 {user_items.get('金萝卜', 0)} 个。"

            # 扣除物品
            self.user_data["items"]["萝卜"] = user_items.get("萝卜", 0) - required_carrots
            self.user_data["items"]["金萝卜"] = user_items.get("金萝卜", 0) - required_gold_carrot

            # 释放囚犯
            if "is_jailed" in target_data.get("status", {}):
                target_data["status"].pop("is_jailed")
            if "prison" in target_data:
                target_data["prison"] = {
                    "is_jailed": False,
                    "release_time": None,
                    "reason": "被他人保释"
                }

            return (
                f"🐰 【兔子城保释】你献上了 {required_carrots} 个萝卜和 1 个金萝卜，兔子卫兵满意地点点头...\n"
                f"🔓 {target['nickname']} 被从胡萝卜牢房里释放出来！\n"
                f"🥕 兔子公主嘟囔着：‘这些人类真舍得花钱...’\n"
                f"🏃‍♂️ 你们赶紧逃离了兔子城，背后传来卫兵的喊声：‘下次再来玩啊！’"
            )
        else:
            # 普通监狱保释逻辑
            remaining_hours = max(1, int(remaining // 3600))
            cost = 50000 + remaining_hours * 1000

            if self.user_data.get("oasis_coins", 0) < cost:
                return f"❌ 你需要 {cost} 绿洲币保释此人，但你目前余额不足。"

            # 扣费 & 解禁
            self.user_data["oasis_coins"] -= cost
            if "is_jailed" in target_data.get("status", {}):
                target_data["status"].pop("is_jailed")
            if "prison" in target_data:
                target_data["prison"] = {
                    "is_jailed": False,
                    "release_time": None,
                    "reason": "被他人保释"
                }

            return (
                f"✅ 你毅然决然地支付了 {cost} 绿洲币，为 {target['nickname']} 赎回了自由的希望。\n"
                f"💰 一笔巨款被悄悄转入系统，数字牢房的锁链缓缓松动……\n"
                f"🕊️ {target['nickname']} 走出监狱，仰望星空，眼中多了一丝感激与不甘。\n"
                f"🌌 世界恢复了平静，但命运的骰子，已经再次投掷。"
            )
    # 越狱功能
    def escape_prison(self):
        """尝试越狱功能（最多5次）"""
        prison = self.user_data.setdefault("prison", {})
        now = datetime.now(tz)

        if not prison.get("is_jailed"):
            return "🔓 你没有被关押，无法越狱。"

        if str(self.user_id) in self.admin_ids:
            return "👮 管理员不需要越狱，可以直接出狱。"

        attempts = prison.get("escape_attempts", 0)
        if attempts >= 5:
            return "🚫 你已经用完了所有越狱尝试机会（最多5次）！"

        prison["escape_attempts"] = attempts + 1

        escape_success = random.random() < 0.2

        if escape_success:
            prison["is_jailed"] = False
            prison["release_time"] = None
            prison["reason"] = ""

            # 10种成功文本
            success_msgs = [
                "🎉 你用床单打结翻出高墙，一跃而下，逃出生天！",
                "🎉 趁夜黑风高你撬开窗户，轻松脱逃，保安睡得死死的！",
                "🎉 你钻进下水道，一路爬到城市下水口，自由的空气扑面而来！",
                "🎉 你假扮医生骗过岗哨，一路畅通无阻！",
                "🎉 你在大火混乱中趁乱逃脱，谁都没发现你已消失在夜幕中！",
                "🎉 你贿赂了守卫，大摇大摆从正门离开，没人敢拦你！",
                "🎉 你挖了三个月的地道终于完工，今夜成功逃出生天！",
                "🎉 你伪装成送餐人员混出监狱，还顺走了厨房的美食！",
                "🎉 你利用监狱放风时间躲进垃圾车，被运到了城外！",
                "🎉 你黑入监狱系统伪造释放文件，警卫恭敬地送你离开！"
            ]
            news_msgs = [
                f"🔥🔥火爆新闻🔥🔥 {self.nickname}大闹监狱成功逃脱，保安彻底崩溃，全城哗然！",
                f"📢【突发】{self.nickname} 越狱成功，警报拉响，警察疲于追捕！",
                f"🚨 惊天越狱！{self.nickname} 成功逃出重重围栏，监狱形同虚设！",
                f"💥 震撼全城！{self.nickname} 上演现实版《越狱》，警方颜面扫地！",
                f"📰 头条新闻：{self.nickname} 用不可思议的方式越狱，监控录像令人瞠目！",
                f"🚔 警方通缉：{self.nickname} 从最高安保监狱逃脱，悬赏金额创历史新高！",
                f"🌪️ 监狱风暴！{self.nickname} 的越狱计划天衣无缝，狱警至今无法理解！",
                f"🔞 未成年人请在家长陪同下观看：{self.nickname} 的越狱过程太过刺激！",
                f"🏃‍♂️【直播追踪】{self.nickname} 越狱后行踪成谜，全民参与追捕游戏！",
                f"💢 监狱长引咎辞职！因 {self.nickname} 越狱事件暴露管理漏洞！"
            ]

            self.global_data.setdefault("news_feed", []).append({
                "time": now.isoformat(),
                "content": random.choice(news_msgs)
            })

            return f"{random.choice(success_msgs)}\n📛 你已使用 {prison['escape_attempts']} / 5 次越狱尝试。"

        else:
            # 惩罚：加刑30分钟
            extra = timedelta(minutes=30)
            origin = datetime.fromisoformat(prison["release_time"])
            prison["release_time"] = (origin + extra).isoformat()

            # 10种失败文本
            fail_msgs = [
                "💥 越狱失败！你刚爬上墙头就被聚光灯照个正着！",
                "💥 越狱失败！狗叫声引来了巡逻警卫，你被按倒在地。",
                "💥 越狱失败！你还没打开门锁，守卫就突然巡逻回来。",
                "💥 越狱失败！同伴临阵脱逃供出了你的位置。",
                "💥 越狱失败！你脚下一滑，直接从天花板掉了下来，被逮个正着。",
                "💥 越狱失败！你挖的地道突然坍塌，引来了大批警卫！",
                "💥 越狱失败！你假扮的警卫制服号码居然是退休老警的，当场穿帮！",
                "💥 越狱失败！你藏在洗衣车里的计划被嗅觉灵敏的警犬发现了！",
                "💥 越狱失败！你刚切断电网警报就响了，整个监狱进入封锁状态！",
                "💥 越狱失败！你贿赂的守卫其实是卧底，专门钓鱼执法！"
            ]

            return f"{random.choice(fail_msgs)}\n📛 你已使用 {prison['escape_attempts']} / 5 次越狱尝试。你被加刑 30 分钟。"


    # ✅ 管理员手动关押玩家
    def jail_user(self, target_id, hours=1, reason="管理员关押"):
        target = self.find_user(target_id)
        if not target:
            return "❌ 目标用户不存在"

        target_data = self.global_data["users"][target["user_id"]]
        release_time = (datetime.now(tz) + timedelta(hours=hours)).isoformat()

        target_data["prison"] = {
            "is_jailed": True,
            "release_time": release_time,
            "reason": reason
        }

        target_data["oasis_coins"] = 0
        target_data["inventory"] = []

        return (
            f"👮‍♂️ 玩家 {target['nickname']} 已被关入数字监狱 {hours} 小时。\n"
            f"💸 财产已清空 | 原因：{reason}"
        )

    # ✅ 管理员手动释放玩家
    def release_user(self, target_id):
        target = self.find_user(target_id)
        if not target:
            return "❌ 目标用户不存在"

        target_data = self.global_data["users"][target["user_id"]]
        target_data["prison"] = {
            "is_jailed": False,
            "release_time": None,
            "reason": ""
        }

        return f"✅ 玩家 {target['nickname']} 已被释放出监狱"


    # 赛车游戏数据
    def init_race_data(self):
        if "race_stats" not in self.user_data:
            self.user_data["race_stats"] = {
                "vehicle": random.choice(list(self.vehicle_models.keys())),
                "model": None,
                "total_races": 0,
                "wins": 0,
                "keys": [],
                "death_count": 0
            }
            # 分配初始车辆
            vehicle_type = self.user_data["race_stats"]["vehicle"]
            self.user_data["race_stats"]["model"] = random.choice(
                self.vehicle_models[vehicle_type]
            )

    # 排行榜相关方法
    def update_leaderboard(self):
        """更新排行榜数据"""
        current_coins = self.user_data["oasis_coins"]

        # 确保存在基础数据结构
        if "leaderboard" not in self.global_data:
            self.global_data["leaderboard"] = {
                "daily": [],
                "monthly": [],
                "all_time": []
            }

        # 更新所有榜单类型
        for board_type in ["daily", "monthly", "all_time"]:
            # 查找现有记录
            entry = next(
                (x for x in self.global_data["leaderboard"][board_type]
                 if x["user_id"] == self.user_id),
                None
            )

            if entry:
                # 更新现有记录
                entry["amount"] = current_coins
            else:
                # 添加新记录
                self.global_data["leaderboard"][board_type].append({
                    "user_id": self.user_id,
                    "nickname": self.nickname,
                    "amount": current_coins
                })

            # 排序并保留前100
            self.global_data["leaderboard"][board_type].sort(
                key=lambda x: x["amount"],
                reverse=True
            )
            self.global_data["leaderboard"][board_type] = \
                self.global_data["leaderboard"][board_type][:100]

    # 在OASISGame类中添加时间处理方法
    def check_reset_times(self):
        now = datetime.now()

        # 处理每日重置
        if now.date() > datetime.fromisoformat(self.global_data["daily_reset"]).date():
            self.global_data["daily_reset"] = now.isoformat()
            self.global_data["leaderboard"]["daily"] = []
            # 重置用户每日赌博胜利次数
            self.user_data["gamble_stats"]["daily_wins"] = 0

        # 处理每月重置
        last_reset = datetime.fromisoformat(self.global_data["monthly_reset"])
        if (now.year > last_reset.year) or (now.month > last_reset.month):
            self.global_data["monthly_reset"] = now.isoformat()
            self.global_data["leaderboard"]["monthly"] = []

    # 排行榜
    def show_leaderboard(self, board_type="all_time"):
        """显示排行榜"""
        board_data = self.global_data["leaderboard"].get(board_type, [])

        display = [
            "🏆 绿洲财富排行榜",
            f"📊 榜单类型: {'总榜' if board_type == 'all_time' else '月榜' if board_type == 'monthly' else '日榜'}",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        # 添加前十名
        for idx, entry in enumerate(board_data[:10], 1):
            display.append(f"{idx}. {entry['nickname']} - {entry['amount']:,} 绿洲币")

        # 添加当前用户排名
        user_entry = next((e for e in board_data if e['user_id'] == self.user_id), None)
        if user_entry:
            rank = board_data.index(user_entry) + 1
            display.append(f"\n👤 你的排名: 第 {rank} 位 (当前资产: {user_entry['amount']:,}绿洲币)")
        else:
            display.append("\n⚠️ 你尚未进入榜单")

        return "\n".join(display)

    # 修改后的find_user方法
    def find_user(self, target_id):
        clean_input = parse_mirai_at(target_id)

        # 优先尝试 user_id 直接匹配
        for uid, info in self.global_data["users"].items():
            if str(uid) == clean_input:
                return {
                    "user_id": uid,
                    "nickname": info.get("nickname", "未知用户"),
                    "oasis_coins": info.get("oasis_coins", 0)
                }

        # 再尝试昵称匹配（唯一匹配）
        for uid, info in self.global_data["users"].items():
            if info.get("nickname") == clean_input:
                return {
                    "user_id": uid,
                    "nickname": info.get("nickname", "未知用户"),
                    "oasis_coins": info.get("oasis_coins", 0)
                }

        # 未找到
        return None

    # rob模块

    def handle_rob_command(self, cmd_parts):
        """
        处理 rob 指令：
        - rob bank ...        # 银行抢劫团伙玩法，调用 RobBankModule
        - rob <@用户|昵称|ID> # 普通抢夺
        - rob admin <@用户|昵称|ID> # 管理员抢夺
        """
        if len(cmd_parts) < 2:
            return "❌ 格式错误，正确格式: rob <@用户|ID> 或 rob admin <@用户|ID> 或 rob bank ..."

        # 银行抢劫命令
        if cmd_parts[1].lower() in ["bank", "银行"]:
            return self.handle_rob_bank(cmd_parts)
        if cmd_parts[1].lower() in ["rabbit", "兔子城"]:
            return self.handle_rob_rabbit_city(cmd_parts)
        if cmd_parts[1].lower() in ["jail", "监狱"]:
            return self.handle_rob_jail(cmd_parts[2:])

        elif cmd_parts[1].lower() in ["help", "h", "帮助"]:
            return self.rob_help()

        is_admin = cmd_parts[1].lower() == "admin"

        # 提取目标参数
        if is_admin:
            if len(cmd_parts) < 3:
                return "❌ 管理员格式错误，正确格式: rob admin <@用户|ID>"
            raw_target = cmd_parts[2]
        else:
            raw_target = cmd_parts[1]

        clean_target = parse_mirai_at(raw_target)


        # 支持昵称或ID查找
        leaderboard = self.global_data.get("leaderboard", {}).get("daily", [])
        matched_user = next(
            (user for user in leaderboard if user["nickname"] == clean_target or user["user_id"] == clean_target),
            None
        )

        if matched_user:
            target_id = matched_user["user_id"]
        else:
            target_id = clean_target

        # 随机决定抢什么
        rob_mode = random.choices(["coins", "items", "both"], weights=[0.2, 0.4, 0.4])[0]

        # 检查对方是否为拳击手
        if self.check_boxer_counter(self.user_id, target_id):
            return f"🥊 @{target_id} 拳击反击！{self.nickname} 被打得鼻青脸肿，送进医院治疗！"

        if rob_mode == "coins":
            return self.rob_coins(target_id)
        elif rob_mode == "items":
            return self.rob_items(target_id)
        else:
            return self.rob_both(target_id)

    def rob_both(self, target_id):
        """同时尝试抢劫金币和物品"""
        coin_result = self.rob_coins(target_id)
        item_result = self.rob_items(target_id)

        # 如果抢劫金币时被捕，就不再抢劫物品
        if "你被投入数字监狱" in coin_result:
            return coin_result

        # 合并结果
        if item_result.startswith("🎒") or item_result.startswith("👛") or item_result.startswith("🦹"):
            return f"{coin_result}\n{item_result}"
        return coin_result

    def rob_coins(self, target_id):

        now = datetime.now(tz).date().isoformat()
        clean_id = str(target_id).lstrip('@')
        target_user = self.find_user(clean_id)
        if not target_user:
            return "🕵️ 目标已消失在数据洪流中..."
        if str(target_user["user_id"]) == str(self.user_id):
            return "💣 你掏出镜子对准自己，这有什么意义呢？"

        target_real_data = self.global_data["users"][target_user["user_id"]]

        event_dice = random.randint(1, 20)

        if random.random() < 0.65:
            fine = int(self.user_data["oasis_coins"] * 0.9)
            self.user_data["oasis_coins"] -= fine
            police_desc = random.choice([
                "🚔 天网系统锁定你，警察机器人蜂拥而至！",
                "🔦 一道战术强光打中你额头，你已被捕！",
                "💂 正在巡逻的治安部队将你按倒...",
                "👮‍♀️ AI女警出现在你身后，低语：‘现在轮到你了。’",
                "🚨 街角亮起红光：‘你涉嫌非法数据入侵，立即投降！’",
                "📡 数字审判系统宣布你有罪，量刑中..."
            ])
            result = [
                police_desc,
                f"💰 被罚款 {fine} 绿洲币",
                f"🏦 当前余额：{self.user_data['oasis_coins']}"
            ]
            jail_hours = random.randint(1, 2)
            release_time = (datetime.now(tz) + timedelta(hours=jail_hours)).isoformat()
            self.user_data["prison"] = {
                "is_jailed": True,
                "release_time": release_time,
                "reason": "抢劫失败被捕"
            }
            result.append(f"🔒 你被投入数字监狱 {jail_hours} 小时，期间无法操作。")
            # 新闻纪录
            self.global_data["news_feed"].append({
                "time": datetime.now(tz).isoformat(),
                "content": f"🚔 {self.nickname} 因抢劫行为被警察抓进了监狱，财产全部被没收！"
            })
            return "\n".join(result)

        if event_dice == 20:
            robbed = int(target_real_data["oasis_coins"] * 0.01)
            robbed = max(robbed, 1)
            self.user_data["oasis_coins"] += robbed
            target_real_data["oasis_coins"] -= robbed
            return f"🎭 你表演了一场骗局，骗走 {robbed} 绿洲币！\n💳 当前余额：{self.user_data['oasis_coins']}"

        percent = random.randint(1, 5)
        robbed = int(target_real_data["oasis_coins"] * percent / 100)
        robbed = max(1, robbed) if target_real_data["oasis_coins"] > 0 else 0
        if robbed == 0:
            return "🕸️ 这个钱包比你的未来还干净..."

        self.user_data["oasis_coins"] += robbed
        target_real_data["oasis_coins"] -= robbed

        desc = random.choice([
            f"🔪 你在小巷抢走了 {robbed} 绿洲币",
            f"🎧 在夜店中巧妙偷走了对方的钱包 ({robbed})",
            f"🌐 虚拟攻击成功，截获了 {robbed} 币",
            f"💉 你伪装成义体医生，把支付端口调包获得 {robbed} 币",
            f"🕶️ 一张假脸骗过了门禁系统，取走了 {robbed} 币",
            f"🪙 趁人群混乱，你顺走了 {robbed} 枚绿洲币",
            f"💃 趁对方沉迷虚拟舞蹈，你悄然得手 ({robbed})",
            f"📦 你拦下对方外卖，用假地址截获了 {robbed} 资金"
        ])

        return f"{desc}\n💳 当前余额：{self.user_data['oasis_coins']}"

    def rob_items(self, target_id):
        """尝试抢劫目标玩家的物品"""
        clean_id = str(target_id).lstrip('@')
        target_user = self.find_user(clean_id)
        if not target_user:
            return "🕵️ 目标已消失在数据洪流中..."
        if str(target_user["user_id"]) == str(self.user_id):
            return "💣 你掏出镜子对准自己，这有什么意义呢？"

        target_real_data = self.global_data["users"][target_user["user_id"]]
        inventory = target_real_data.get("inventory", [])
        lootable_items = [item for item in inventory if item.get("quantity", 0) > 0]

        # 65% 概率被捕
        if random.random() < 0.65:
            fine = int(self.user_data["oasis_coins"] * 0.9)
            self.user_data["oasis_coins"] -= fine
            police_desc = random.choice([
                "🚔 天网系统锁定你，警察机器人蜂拥而至！",
                "🔦 一道战术强光打中你额头，你已被捕！",
                "💂 正在巡逻的治安部队将你按倒...",
                "👮‍♀️ AI女警出现在你身后，低语：‘现在轮到你了。’"
            ])
            result = [
                police_desc,
                f"💰 被罚款 {fine} 绿洲币",
                f"🏦 当前余额：{self.user_data['oasis_coins']}"
            ]
            jail_hours = random.randint(1, 2)
            release_time = (datetime.now(tz) + timedelta(hours=jail_hours)).isoformat()
            self.user_data["prison"] = {
                "is_jailed": True,
                "release_time": release_time,
                "reason": "抢劫物品失败被捕"
            }
            result.append(f"🔒 你被投入数字监狱 {jail_hours} 小时，期间无法操作。")
            # 新闻纪录
            self.global_data["news_feed"].append({
                "time": datetime.now(tz).isoformat(),
                "content": f"🚔 {self.nickname} 因抢劫物品被警察抓进了监狱！"
            })
            return "\n".join(result)

        if not lootable_items:
            return "🎒 目标的背包空空如也..."

        # 随机抢1-3个物品
        item = random.choice(lootable_items)
        steal_qty = min(item["quantity"], random.randint(1, 3))
        item["quantity"] -= steal_qty
        if item["quantity"] <= 0:
            inventory.remove(item)

        # 添加到自己的背包
        my_inv = self.user_data.setdefault("inventory", [])
        found = next((i for i in my_inv if i["id"] == item["id"]), None)
        if found:
            found["quantity"] += steal_qty
        else:
            my_inv.append({
                "id": item["id"],
                "name": item.get("name", item["id"]),
                "quantity": steal_qty,
                "description": item.get("description", "未知来源物品")
            })

        desc = random.choice([
            f"👜 黑暗中摸索到 {steal_qty} 个「{item.get('name', item['id'])}」悄悄收入囊中",
            f"📦 混乱中你拿到了 {steal_qty} 个「{item.get('name', item['id'])}」",
            f"👀 四下无人时，你快速取走了 {steal_qty} 个「{item.get('name', item['id'])}」",
            f"🛍️ 假装挑选物品时，你藏起了 {steal_qty} 个「{item.get('name', item['id'])}」",
            f"🏃‍♂️ 擦肩而过的瞬间，{steal_qty} 个「{item.get('name', item['id'])}」已到你手中",
            f"🤫 屏住呼吸拿走了 {steal_qty} 个「{item.get('name', item['id'])}」",
            f"🌃 夜色掩护下，你获得了 {steal_qty} 个「{item.get('name', item['id'])}」",
            f"🕶️ 墨镜反射的光线中，{steal_qty} 个「{item.get('name', item['id'])}」消失了"
        ])
        return desc

    @staticmethod
    def rob_help():
        return (
            "📖【OASIS 抢劫系统使用说明】\n"
            "掠夺财富与物资，在赛博都市的阴影中生存！\n"
            "———————————————\n"
            "🔫 rob 基础指令\n"
            "📌 用法：\n"
            "🔹 rob @用户ID —— 随机抢劫目标（金币/物品/两者）\n"
            "———————————————\n"
            "💰 金币抢劫规则\n"
            "🎲 成功率：35% (65%被捕)\n"
            "📈 成功时：\n"
            "• 夺取目标 1%~5% 的绿洲币\n"
            "• 1/20 概率触发特殊事件（骗局）\n"
            "📉 失败时：\n"
            "• 被罚款 90% 当前资产\n"
            "• 入狱 1-2 小时\n"
            "———————————————\n"
            "🎒 物品抢劫规则\n"
            "🎲 成功率：35% (同金币)\n"
            "📦 成功时：\n"
            "• 随机偷取 1-3 个目标背包物品\n"
            "• 优先偷取可堆叠物品\n"
            "🕳️ 特殊状况：\n"
            "• 目标背包为空时直接失败\n"
            "———————————————\n"
            "🏦 rob bank 团伙抢劫\n"
            "📌 用法：\n"
            "🔹 rob bank —— 发起抢劫（成为队长）\n"
            "🔹 rob bank @队长ID —— 加入队伍\n"
            "🔹 rob bank start —— 执行抢劫（需4人）\n"
            "🎁 成功奖励：\n"
            "• 1w~10w 绿洲币（团队平分）\n"
            "• 小概率获得稀有道具\n"
            "💥 失败惩罚：\n"
            "• 随机1人逃脱，其余成员：\n"
            "  - 财产清空\n"
            "  - 入狱4小时\n"
            "  - 背包物品没收\n"
            "———————————————\n"
            "🐰 rob rabbit 兔子城豪劫（新）\n"
            "📌 用法：\n"
            "🔹 rob rabbit —— 农夫创建队伍（需伪装身份）\n"
            "🔹 rob rabbit @队长ID —— 加入队伍\n"
            "🔹 rob rabbit start —— 执行豪劫（需2-3人）\n"
            "⚠️ 特殊限制：\n"
            "• 队长必须是农夫\n"
            "• 队伍中不能有猎人\n"
            "🥕 成功奖励：\n"
            "• 随机获得3种蔬菜种子（1-5个/种）\n"
            "• 15%几率获得稀有【兔子戒指】\n"
            "🚨 失败惩罚：\n"
            "• 60%几率被关进兔子城监狱3小时\n"
            "• 逃脱者可保留少量种子\n"
            "———————————————\n"
            "🚔 rob prison 监狱营救任务\n"
            "📌 用法：\n"
            "🔹 rob 监狱 <目标ID> —— 发起劫狱（目标必须在监狱）\n"
            "🔹 rob 监狱 @队长ID —— 加入队伍（最多4人）\n"
            "🔹 rob 监狱 start —— 队长发起营救行动\n"
            "⚠️ 限制规则：\n"
            "• 警察职业禁止参与\n"
            "• 失败可能被抓或受伤\n"
            "• 隐者职业拥有较高逃脱概率\n"
            "🎁 成功奖励：\n"
            "• 成功将目标玩家释放出狱\n"
            "🚨 失败惩罚：\n"
            "• 队员可能入狱或进医院\n"
            "• 成员将根据职业与运气承受不同后果\n"
            "———————————————\n"
            "💡 小贴士：\n"
            "• 多人组队成功率更高（最多+60%）\n"
            "• 隐者可提升存活率\n"
            "• 被营救目标无需参与，仅需入狱状态\n"
            "———————————————\n"
            "🚨 风险提示：\n"
            "• 高价值目标可能雇佣保镖\n"
            "• 连续失败会延长刑期\n"
            "• 监狱中无法进行任何操作\n"
            "• 兔子城监狱需用50萝卜+1金萝卜保释\n"
            "———————————————\n"
            "🛠️ 管理员指令\n"
            "🔹 rob admin @用户ID —— 强制成功抢劫\n"
            "🔹 rob jail @用户ID [小时] [原因] —— 关押玩家\n"
            "🔹 rob pardon @用户ID —— 提前释放\n"
            "———————————————\n"
            "💡 实用技巧：\n"
            "• 被关押时可用 `bail` 尝试保释\n"
            "• 普通监狱用绿洲币，兔子城需物资保释\n"
            "• 凌晨3-5点警察响应较慢\n"
            "• 查看 `news` 获取最新案件信息\n"
            "• 某些道具可降低被捕概率\n"
        )

    #————————————————————职业效果——————————————
    def check_boxer_counter(self, attacker_id, target_id):
        target_data = self.global_data["users"].get(str(target_id), {})
        if target_data.get("career") == "拳击手":
            attacker_data = self.global_data["users"].get(str(attacker_id), {})
            attacker_data.setdefault("status", {})["in_hospital"] = True
            return True
        return False

    # 转账模块
    def transfer_coins(self, target_id, amount):
        """转账功能，支持 'all' 全额转账"""

        # 判断是否为 'all' 转账
        if str(amount).lower() == "all":
            amount = self.user_data["oasis_coins"]
            if amount == 0:
                return "❌ 当前余额为 0，无法全部转账"
            transfer_all = True
        else:
            transfer_all = False
            try:
                amount = int(amount)
                if amount <= 0:
                    return "❌ 转账金额必须为正整数"
            except ValueError:
                return "❌ 金额必须是数字或 'all'"

        # 查找目标用户
        target_user = parse_mirai_at(target_id)
        target_user_data = self.find_user(target_id)
        if not target_user:
            return "❌ 目标用户不存在"

        # 验证余额
        if amount > self.user_data["oasis_coins"]:
            return f"❌ 余额不足，当前绿洲币: {self.user_data['oasis_coins']}"

        # 执行转账
        self.user_data["oasis_coins"] -= amount
        self.global_data["users"][str(target_user)]["oasis_coins"] += amount

        # 构造转账记录
        transfer_record = {
            "from": self.user_id,
            "to": target_user,
            "amount": amount,
            "time": datetime.now(tz).isoformat(),
            "type": "transfer"
        }
        self.user_data.setdefault("transfer_history", []).append(transfer_record)

        # 接收方记录
        target_data = self.global_data["users"][str(target_user)]
        target_data.setdefault("transfer_history", []).append({
            "from": self.user_id,
            "to": target_user,
            "amount": amount,
            "time": datetime.now(tz).isoformat(),
            "type": "receive"
        })

        # 成功提示
        message = (
            f"✅ 成功转账 {amount} 绿洲币 给 {target_user_data['nickname']}\n"
            f"💰 当前余额: {self.user_data['oasis_coins']}"
        )
        if transfer_all:
            message += f"\n📢 {target_user_data['nickname']} 请好好使用这笔全部财富！"

        return message

    def handle_transfer_command(self, cmd_parts):
        """
        处理 transfer 指令：支持通过 @、ID、昵称转账，支持管理员模式
        格式：
            transfer <@用户|昵称|ID> <金额>
            transfer admin <@用户|昵称|ID> <金额>
        """

        raw_target = cmd_parts[1]
        amount = cmd_parts[2]
        return self.transfer_coins(raw_target, amount)

    def show_stats(self, stats_type=None):
        stats = [
            f"🌴 {self.nickname} 的绿洲统计",
            f"💰 当前绿洲币: {self.user_data.get('oasis_coins', 0)}",
            f"🏦 银行存款: {self.user_data.get('bank', {}).get('balance', 0)} 绿洲币",
            f"👔 职业: {self.user_data.get('career', '无职业')}",
            "",
            "💀 死亡统计:",
            f"- 总自杀次数: {self.user_data.get('death_stats', {}).get('total_suicides', 0)} 次",
            f"- 累计损失: {self.user_data.get('death_stats', {}).get('total_lost', 0)} 绿洲币",
            f"- 最近死亡: {self.user_data.get('death_stats', {}).get('history', [{}])[-1].get('location', '无') if self.user_data.get('death_stats', {}).get('history') else '无'}",
            "",
            "🔁 最近转账记录:"
        ]

        transfers = self.user_data.get("transfer_history", [])[-5:]
        for t in transfers:
            direction = "→" if t.get("type") == "transfer" else "←"
            time_str = datetime.fromisoformat(t.get("time")).strftime("%m-%d %H:%M") if t.get("time") else "未知时间"
            target_id = t.get("to") if direction == "→" else t.get("from")
            target = self.find_user(target_id)
            name = target.get("nickname") if target else "系统"
            stats.append(f"{direction} {name} {t.get('amount', 0)} 绿洲币 ({time_str})")

        return "\n".join(stats)

    # 背包模块

    def has_item_in_inventory(self, item_id):
        for item in self.user_data.get("inventory", []):
            if item.get("id") == item_id and item.get("quantity", 0) > 0:
                return True
        return False

    def show_inventory(self):
        """显示背包内容"""
        inventory = self.user_data.get("inventory", [])
        equipped = self.user_data.get("equipped_items", {})

        if not inventory:
            return "🎒 你的背包空空如也，快去收集物品吧！"

        # 按类型分类物品
        categories = {}
        for item in inventory:
            item_type = item.get("type", "其他")
            categories.setdefault(item_type, []).append(item)

        # 构建显示信息
        display = ["🎒 你的背包物品:"]
        for category, items in categories.items():
            display.append(f"\n【{category}】")
            for idx, item in enumerate(items, 1):
                item_id = item.get("id", "未知ID")
                item_name = item.get("name", f"未命名物品({item_id})")
                item_qty = item.get("quantity", 1)
                item_desc = item.get("description", None)

                equip_status = " (已装备)" if item_id in equipped.values() else ""
                display.append(f"{idx}. {item_name} ×{item_qty}{equip_status}")
                if item_desc:
                    display.append(f"   ▸ {item_desc}")

        return "\n".join(display)

    def add_item(self, item_id, name, item_type="其他", quantity=1, description=""):
        """添加物品到背包"""
        inventory = self.user_data["inventory"]

        # 检查是否可堆叠
        stackable = quantity > 1
        if stackable:
            for item in inventory:
                if item["id"] == item_id:
                    item["quantity"] += quantity
                    return f"✅ 已添加 {name} ×{quantity} (现有: {item['quantity']})"

        # 添加新物品
        new_item = {
            "id": item_id,
            "name": name,
            "type": item_type,
            "quantity": quantity,
            "description": description
        }
        inventory.append(new_item)
        return f"✅ 已获得新物品: {name} ×{quantity}"

    def remove_item(self, identifier, quantity=1):
        """从背包移除物品，可通过 id 或 name 识别"""
        inventory = self.user_data["inventory"]
        identifier = identifier.strip().lower()

        for idx, item in enumerate(inventory):
            match = (
                    str(item.get("id")).lower() == identifier
                    or item.get("name", "").strip().lower() == identifier
            )
            if match:
                if item.get("quantity", 1) > quantity:
                    item["quantity"] -= quantity
                    return f"✅ 已移除 {item['name']} ×{quantity} (剩余: {item['quantity']})"
                else:
                    removed_name = item["name"]
                    inventory.pop(idx)
                    # 移除装备
                    equipped = self.user_data.get("equipped_items", {})
                    for slot, eq_id in list(equipped.items()):
                        if eq_id == item.get("id"):
                            equipped.pop(slot)
                    return f"✅ 已完全移除 {removed_name}"

        return "❌ 背包中找不到该物品"

    def handle_drop(self, cmd_parts):
        """
        处理 drop 指令：
        - drop 1 [数量]：按索引移除
        - drop 名称 [数量]：按名称移除
        - drop all：清空背包
        """
        inventory = self.user_data.get("inventory", [])
        equipped = self.user_data.get("equipped_items", {})

        if len(cmd_parts) < 2:
            return "❌ 请指定要丢弃的物品编号、名称，或输入 drop all 全部清空"

        drop_target = cmd_parts[1].strip()
        quantity = 1

        if len(cmd_parts) > 2:
            try:
                quantity = int(cmd_parts[2])
                if quantity <= 0:
                    return "❌ 丢弃数量必须大于 0"
            except ValueError:
                return "❌ 丢弃数量必须是数字"

        # ✅ 清空背包
        if drop_target.lower() == "all":
            dropped_count = len(inventory)
            inventory.clear()
            equipped.clear()
            return f"🗑️ 已清空背包，共丢弃 {dropped_count} 个物品"

        # ✅ 尝试按编号丢弃
        if drop_target.isdigit():
            index = int(drop_target) - 1
            if 0 <= index < len(inventory):
                item = inventory[index]
                return self.remove_item(item["id"], quantity)
            else:
                return "❌ 无效的物品编号"

        # ✅ 尝试按名称丢弃（支持模糊匹配）
        matches = [item for item in inventory if drop_target.lower() in item.get("name", "").lower()]
        if not matches:
            return f"❌ 未找到名称包含 “{drop_target}” 的物品"

        # 如果找到多个匹配，优先取第一个
        item = matches[0]
        return self.remove_item(item["id"], quantity)

    def has_item(self, item_id: str, min_quantity: int = 1) -> bool:
        inventory = self.user_data.get("inventory", [])
        for item in inventory:
            if item.get("id") == item_id and item.get("quantity", 0) >= min_quantity:
                return True
        return False

    def add_simple_item(self, item_id, quantity=1, description=""):
        item_id = item_id.lower()
        # 先检查背包是否已有该物品，支持叠加
        for item in self.user_data.get("inventory", []):
            if item["id"] == item_id:
                item["quantity"] += quantity
                return f"✅ 【{item['name']}】数量增加了 {quantity} 个，现在共有 {item['quantity']} 个。"

        # 没有则新建
        if "inventory" not in self.user_data:
            self.user_data["inventory"] = []
        self.user_data["inventory"].append({
            "id": item_id,
            "name": item_id,  # 你也可以改为传入的名字
            "quantity": quantity,
            "description": description
        })
        return f"✅ 新获得物品：【{item_id}】 ×{quantity}。"

    # 通过id给玩家物品
    def give_item_to_user(self, user_id, item_id, quantity=1, description=""):
        item_id = item_id.lower()
        user = self.global_data["users"].setdefault(user_id, {})
        inventory = user.setdefault("inventory", [])

        # 查找是否已有此物品（支持叠加）
        for item in inventory:
            if item["id"] == item_id:
                item["quantity"] += quantity
                return f"✅ 【{item['name']}】数量增加了 {quantity} 个，现在共有 {item['quantity']} 个。"

        # 没有则添加新物品
        inventory.append({
            "id": item_id,
            "name": item_id,  # 你可以在调用时自定义更优雅的名字
            "quantity": quantity,
            "description": description
        })
        return f"✅ 向 {user.get('nickname', user_id)} 发放了：【{item_id}】 ×{quantity}。"

    def give_item_to_player(self, cmd_parts):
        """
        玩家赠送物品给另一个玩家

        """
        if len(cmd_parts) < 3:
            return "❌ 用法错误：give @玩家ID 物品名 [数量]（数量可省略）"

        target_id = cmd_parts[1]
        item_name_or_id = cmd_parts[2]

        # 尝试解析数量，默认是1
        try:
            quantity = int(cmd_parts[3]) if len(cmd_parts) > 3 else 1
        except ValueError:
            return "❌ 数量必须是一个正整数"

        if quantity <= 0:
            return "❌ 数量必须大于0"
        sender_data = self.user_data
        if not sender_data:
            return "❌ 无效的赠送者 ID"

        inventory = sender_data.get("inventory", [])
        matched_item = None

        # 模糊查找物品
        for item in inventory:
            if (item_name_or_id.lower() in item.get("id", "").lower()
                    or item_name_or_id.lower() in item.get("name", "").lower()):
                matched_item = item
                break

        if not matched_item:
            return f"❌ 你没有名为 '{item_name_or_id}' 的物品"

        if quantity <= 0:
            return "❌ 赠送数量必须大于 0"
        if matched_item["quantity"] < quantity:
            return f"❌ 你的 {matched_item['name']} 数量不足（当前：{matched_item['quantity']}）"

        # 查找目标玩家
        target = self.find_user(target_id)
        if not target:
            return f"❌ 找不到目标玩家：{target_id}"

        target_data = self.global_data["users"].get(str(target["user_id"]))
        if not target_data:
            return f"❌ 目标玩家数据异常"

        if "inventory" not in target_data:
            target_data["inventory"] = []

        # 移除赠送者物品
        matched_item["quantity"] -= quantity
        if matched_item["quantity"] <= 0:
            inventory.remove(matched_item)

        # 添加给目标玩家（可堆叠）
        for item in target_data["inventory"]:
            if item["id"] == matched_item["id"]:
                item["quantity"] += quantity
                break
        else:
            target_data["inventory"].append({
                "id": matched_item["id"],
                "name": matched_item["name"],
                "quantity": quantity,
                "type": matched_item.get("type", "其他"),
                "description": matched_item.get("description", "")
            })

        # 日志记录（可选）
        self._log_item_transfer(sender_data["nickname"], matched_item["id"], -quantity)
        self._log_item_transfer(target["nickname"], matched_item["id"], quantity)

        return (f"🎁 你成功将 {matched_item['name']} ×{quantity} "
                f"赠送给了 {target['nickname']}！")


    def is_equipped(self, target_id, item_id: str) -> bool:
        """判断玩家是否装备了指定物品 ID"""
        target_data = self.global_data["users"][target_id]
        equipped = target_data.get("equipped_items")
        return equipped is not None and equipped.get("id") == item_id

    def equip_item_by_name(self, name_str):
        inventory = self.user_data.get("inventory", [])
        if not inventory:
            return "🎒 背包为空，无法装备物品"

        # 忽略大小写匹配物品
        target_item = None
        for item in inventory:
            if name_str.lower() in [item.get("name", "").lower(), item.get("id", "").lower()]:
                target_item = item
                break

        if not target_item:
            return f"❌ 没有找到名称或 ID 为“{name_str}”的物品"

        item_name = target_item.get("name", target_item["id"])
        previous = self.user_data.get("equipped_items")

        # 已装备同一件
        if previous and previous.get("id") == target_item.get("id"):
            return f"⚠️ 你已经装备了【{item_name}】，无需重复装备。"

        # 替换装备
        self.user_data["equipped_items"] = target_item

        if previous:
            prev_name = previous.get("name", previous["id"])
            return (
                f"♻️ 你更换了装备：从【{prev_name}】 → 【{item_name}】\n"
                f"✅ 你现在装备了【{item_name}】"
            )
        else:
            return f"✅ 你现在装备了【{item_name}】"

    def _log_item_transfer(self, target_id, item_id, quantity):
        """记录物品转移日志（内部方法）"""
        log_entry = {
            "from": self.user_id,
            "to": target_id,
            "item": item_id,
            "quantity": quantity,
            "time": datetime.now(tz).isoformat()
        }
        self.global_data.setdefault("item_transfer_log", []).append(log_entry)

    #————————————————黑市——————————————————
    def show_black_market(self):
        market = self.global_data.get("black_market", {})
        if not market:
            return "🕳️ 黑市今日未开放，或已清空。"

        result = ["🛒【今日黑市商品】"]
        for item in market.values():
            result.append(
                f"🔹 {item['name']}（剩余 {item['stock']}）\n"
                f"💰 价格：{int(item['price'] * 1.5)} 绿洲币\n"
                f"📦 说明：{item['desc']}\n"
                f"🛍️ 购买指令：/buy {item['id']}"
            )
        return "\n".join(result)

    def buy_from_black_market(self, item_id):
        market = self.global_data.get("black_market", {})
        item = None
        for it in market.values():
            if it["id"] == item_id:
                item = it
                break

        if not item:
            return f"❌ 黑市中没有 ID 为 `{item_id}` 的物品。"

        if item["stock"] <= 0:
            return f"❌ 【{item['name']}】已售罄，请明日再来。"

        cost = int(item["price"] * 1.5)
        if self.user_data.get("oasis_coins", 0) < cost:
            return f"💸 你的余额不足，购买【{item['name']}】需要 {cost} 绿洲币。"

        # 扣款 & 发放物品 & 减库存
        self.user_data["oasis_coins"] -= cost
        self.user_data.setdefault("inventory", []).append({
            "id": item["id"],
            "name": item["name"],
            "desc": item["desc"]
        })
        item["stock"] -= 1

        return (
            f"✅ 你花费了 {cost} 绿洲币，从神秘黑市购得【{item['name']}】！\n"
            f"📦 {item['desc']}"
        )

    # 骰子功能

    @staticmethod
    def generate_dice(times=1, sides=6):
        """掷骰子，返回结果列表"""
        return [random.randint(1, sides) for _ in range(times)]

    def show_dice_result(self, times=1, sides=6):
        """显示掷骰结果文本及结果列表"""
        try:
            sides = max(2, min(100, int(sides)))
            times = max(1, min(10, int(times)))
        except ValueError:
            return "❌ 参数必须是整数", []

        results = self.generate_dice(times, sides)
        total = sum(results)
        specials = []

        skip_specials = (times == 1 and sides == 6)

        if not skip_specials and all(x == results[0] for x in results):
            specials.append("🎯 全等骰！")

        if not skip_specials and times >= 3 and sorted(results) == list(range(min(results), max(results) + 1)):
            specials.append("🚀 顺子！")

        if all(x == sides for x in results):
            specials.append(f"🔥 极限全{str(sides)}！")

        if all(x == 1 for x in results):
            specials.append("❄️ 极限全1！")

        counts = Counter(results)
        most_common_num, most_common_count = counts.most_common(1)[0]
        if most_common_count > 1:
            specials.append(f"🔢 {most_common_count}个{most_common_num}！")

        avg_val = sides / 2 + 0.5
        threshold_high = avg_val * 1.6 * times
        threshold_low = avg_val * 0.4 * times
        if total >= threshold_high:
            specials.append("💥 爆发高点！")
        elif total <= threshold_low:
            specials.append("⬇️ 低谷极限！")

        result_text = [
            f"🎲 掷出 {times}次{sides}面骰",
            f"▸ 结果: {results}",
            f"▸ 总和: {total}"
        ]

        if specials:
            result_text.append("✨ 特殊效果: " + " ".join(specials))

        return "\n".join(result_text), results

    # 翼装飞行游戏
    def wingsuit_flight(self, map_choice):
        maps = {
            "1": {"name": "喜马拉雅山脉", "difficulty": "专家", "height": 10000},
            "2": {"name": "迪拜城市群", "difficulty": "中级", "height": 6000},
            "3": {"name": "亚马逊雨林", "difficulty": "新手", "height": 3000}
        }

        current_map = maps.get(map_choice, maps["3"])
        self.user_data["wing_suit_stats"]["current_map"] = current_map
        height = current_map["height"]

        result = [f"🪂 翼装飞行在 {current_map['name']}（{height} 米）高度出发"]

        # 事件池（含权重）
        flight_events = [
            (50, "顺风顺水，飞行平稳。"),
            (15, "遇到一阵强风，稍微摇晃了一下。"),
            (10, "看见远处美丽的日出，心情大好。"),
            (8, "滑翔时擦过树枝，险些被刮伤。"),
            (6, "发现一只稀有鹰隼在旁边盘旋。"),
            (5, "遇到突然的气流乱流，控制难度加大。"),
            (4, "被突如其来的雷雨淋湿，视线受阻。"),
            (2, "误触岩壁，受轻微擦伤。"),
            (0, "💀 意外撞上悬崖，坠落身亡！")
        ]

        # 按权重随机选择事件的函数
        def weighted_random_event():
            weights, descriptions = zip(*flight_events)
            return random.choices(descriptions, weights=weights, k=1)[0]

        # 每100米触发事件
        for h in range(height, 1000, -100):
            desc = weighted_random_event()
            result.append(f"⛅ {h}m → {desc}")
            if desc.startswith("💀"):
                # self.handle_death()
                result.append("💥 你不幸坠亡\n游戏币与物品已清空，请使用 'revive' 指令复活")
                return "\n".join(result)

        # 开伞阶段，保留骰子判定
        _, parachute_roll = self.show_dice_result(6, 2)
        if sum(parachute_roll) <= 4:
            result.append(f"🪂 开伞失败！🎲{parachute_roll}")
            # self.handle_death()
            result.append("💥 你坠毁身亡\n游戏币与物品已清空，请使用 'revive' 指令复活")
            return "\n".join(result)
        result.append(f"🪂 开伞成功 🎲{parachute_roll}")

        # 着陆判定
        _, landing = self.show_dice_result(6, 2)
        if sum(landing) <= 5:
            result.append(f"🛬 着陆失败 🎲{landing} → 🚑 你受了伤，但保住了性命")
            return "\n".join(result)

        # 成功着陆结算
        score = 10 + (height // 100) * 5
        self.user_data["wing_suit_stats"]["total_jumps"] += 1
        self.user_data["wing_suit_stats"]["total_score"] += score
        self.user_data["oasis_coins"] += score
        self.update_leaderboard()

        result.extend([
            f"🛬 着陆成功 🎲{landing}",
            f"🎯 获得 {score} 分 & 绿洲币 {score}！"
        ])
        return "\n".join(result)

    @staticmethod
    def resolve_flight_event(roll):
        total = sum(roll)
        if total <= 2:
            return "💀 死亡事件"
        elif total <= 4:
            return "⚠️ 翼装撕裂，惊险飞行"
        elif total <= 6:
            return "💨 遇到强风"
        elif total <= 8:
            return "☁️ 云层干扰"
        else:
            return "✅ 平稳飞行"

    # 赛车游戏
    def race_game(self, map_choice):
        self.init_race_data()
        maps = {
            "1": {"name": "末日废墟", "obstacles": ["坍塌的大楼", "岩浆裂缝", "变异植物"]},
            "2": {"name": "赛博都市", "obstacles": ["全息广告牌", "悬浮车流", "机械警卫"], "easter_egg": True},
            "3": {"name": "恐龙岛", "obstacles": ["霸王龙", "翼龙群", "火山爆发"]},
            "4": {"name": "极光荒原", "obstacles": ["极寒风暴", "北极光幻觉", "冰河断裂"]},
            "5": {"name": "绿洲高速", "obstacles": ["随机传送门", "虚拟陷阱", "数据堵塞"]},
            "6": {"name": "火星殖民地", "obstacles": ["微重力漂移", "红沙尘暴", "外星地形"]},
            "7": {"name": "空中赛道", "obstacles": ["气流乱流", "浮空碎石", "断裂跑道"]},
            "8": {"name": "失落神殿", "obstacles": ["崩塌石像", "毒气机关", "幻影障碍"]}
        }
        race_death_chance = 0.15  # 后端可调死亡概率


        current_map = maps.get(map_choice, maps["1"])

        rolls = [random.randint(1, 10) for _ in range(10)]

        # 新增车辆信息展示
        vehicle_info = self.get_vehicle_info()
        speed = 240
        nitro = 100
        crash_count = 0
        result = [
            f"🏁 【{current_map['name']}】比赛正式启动！",
            f"🚗 你驾驶的是 {self.user_data['race_stats']['model']}，引擎轰鸣，马力全开！",
            f"🔧 车辆配置：{vehicle_info}",
            "━" * 30,
            f"🏎️ 起始速度：{speed} km/h | 氮气：{nitro}%",
            random.choice([
                "🎶 车载音响响起《头号玩家》主题曲，情绪拉满！",
                "📡 HUD投影点亮，虚拟赛道全息加载中……",
                "⚡ 引擎过载提示：请注意温度波动！"
            ])
        ]

        for i, roll in enumerate(rolls, 1):
            event = self.get_race_event(roll, current_map["name"])

            # 动态处理速度和氮气
            if roll >= 9:
                speed += random.randint(10, 25)
                nitro = min(100, nitro + random.randint(5, 10))
                event += " 🚀 加速器启动，风驰电掣！"
            elif roll <= 3:
                speed -= random.randint(20, 40)
                nitro = max(0, nitro - random.randint(10, 20))
                event += " 🛑 急刹减速，小心打滑！"
            elif roll == 6:
                crash_count += 1
                event += " 💥 撞上障碍！车体轻微受损！"

            # 拼接每公里内容
            result.append(f"📍 第{i}公里 | 当前速度：{speed}km/h | 氮气：{nitro}%")
            result.append(f"➡️ {event}")

            # 报废检测
            if crash_count >= 3 and random.random() < race_death_chance:
                return self.handle_race_death(result, current_map["name"])

        # 奖励系统
        base_reward = random.randint(80, 150)
        speed_bonus = max(0, 3 - crash_count) * 10
        total_reward = base_reward + speed_bonus
        self.user_data["oasis_coins"] += total_reward
        self.user_data["race_stats"]["wins"] += 1

        result.extend([
            "━" * 30,
            f"🎉 终点冲刺成功！你完成了整场比赛。",
            f"🏆 获得奖励：{total_reward} 绿洲币（基础{base_reward} + 表现加成{speed_bonus}）",
            f"💰 当前余额：{self.user_data['oasis_coins']}",
            random.choice([
                "🎤 你从车窗探出头，大喊：这才是速度与激情！",
                "🎇 终点烟火升空，庆祝这场华丽的胜利！",
                "📸 赛后留影上传绿洲社交平台，点赞破万！"
            ])
        ])
        return "\n".join(result)

    # 开局车辆信息展示
    def get_vehicle_info(self):
        info = {
            "《阿基拉》金田的摩托": {
                "desc": "经典红色科幻摩托，配备激光陀螺稳定系统",
                "skill": "【暴走冲刺】可短暂突破500km/h时速"
            },
            "创战记光轮摩托": {
                "desc": "散发着蓝色荧光的未来摩托，可展开能量护盾",
                "skill": "【光轮屏障】抵挡一次撞击伤害"
            },
            "赤色暴走机车": {
                "desc": "改装自废土的重型机车，车头配有链锯装置",
                "skill": "【暴力开路】直接摧毁小型障碍物"
            },
            "回到未来时光车": {
                "desc": "不锈钢外壳的时光机器，时速88英里可穿越时空",
                "skill": "【时光回溯】重置最近一次骰子结果"
            },
            "疯狂麦克斯拦截者": {
                "desc": "配备火焰喷射器的末日战车，车顶有机枪塔",
                "skill": "【烈焰路径】融化前方障碍物"
            },
            "侏罗纪公园巡游车": {
                "desc": "全地形探险车辆，车顶有可收缩的防暴电网",
                "skill": "【电网防护】降低生物袭击概率"
            }
        }
        model = self.user_data["race_stats"]["model"]
        return f"{info[model]['desc']} | 专属技能: {info[model]['skill']}"

    @staticmethod
    def get_race_event(roll, map_name):
        events = {
            1: {
                "末日废墟": "撞上变异巨蜥！",
                "赛博都市": "被机械哥斯拉追击！",
                "恐龙岛": "霸王龙横穿赛道！",
                "极光荒原": "极寒风暴中现出巨型冰虫！",
                "绿洲高速": "误入数据裂缝，系统警报！",
                "火星殖民地": "外星生命体冲向赛道！",
                "空中赛道": "遇到天际掠食者突袭！",
                "失落神殿": "神秘石像突然苏醒，挡住去路！"
            },
            6: {
                "all": "撞击障碍物！💥"
            },
            10: {
                "末日废墟": "发现隐藏加速带！🚀",
                "赛博都市": "触发霓虹隧道捷径！🌈",
                "恐龙岛": "借助翼龙群飞跃峡谷！",
                "极光荒原": "极光能量脉冲提升速度！",
                "绿洲高速": "数据流动加速引擎！",
                "火星殖民地": "引力井弹射推进器触发！",
                "空中赛道": "顺风气流全速前进！",
                "失落神殿": "神殿试炼成功，获得加速祝福！"
            }
        }

        if roll == 1:
            return f"⚠️ 遭遇生物：{events[1][map_name]}"
        elif roll == 6:
            return f"💥 危险！{events[6]['all']}"
        elif roll == 10:
            return f"🚀 好运！{events[10][map_name]}"
        elif 2 <= roll <= 5:
            return random.choice([
                f"擦过{random.choice(['路障', '废弃车辆', '碎石堆'])}",
                "漂移过弯！",
                "超越前车！"
            ])
        else:
            return random.choice([
                "平稳行驶",
                "使用氮气加速！",
                "刷新个人最佳圈速"
            ])

    # 处理赛车死亡
    def handle_race_death(self, result, map_name):

        self.user_data["oasis_coins"] = 0
        self.user_data["race_stats"]["death_count"] += 1

        # 生成掉落物品
        drop_items = [
            ("青铜零件", random.randint(1, 5) * 100),
            ("赛车涂装", random.choice(["火焰纹", "骷髅图腾", "霓虹线条"]))
        ]

        result.extend([
            "━" * 30,
            f"💀 连续三次撞击！在{map_name}车毁人亡！",
            f"💸 掉落物品：{', '.join([f'{v[1]}{v[0]}' for v in drop_items])}",
            f"⚠️ 剩余绿洲币：{self.user_data['oasis_coins']}"
        ])
        return "\n".join(result)

    def check_and_trigger_easter_egg(self, player_input):
        # 从全局数据获取彩蛋参数
        easter_egg = self.global_data.get("easter_egg")
        if not easter_egg:
            return "🔍 目前没有彩蛋活动。"

        trigger_word = easter_egg.get("trigger_word")
        check_word = easter_egg.get("check_word")

        # 玩家输入与check_word对比（这里示例用简单包含判断，你可以用更严格的逻辑）
        if check_word in player_input:
            # 触发彩蛋奖励，调用之前写好的find_copper_key
            result = self.find_copper_key()

            # 触发后删除彩蛋，避免重复
            del self.global_data["easter_egg"]

            return result
        else:
            return "❌ 你输入的彩蛋关键字不正确，请再试一次。"

    def find_copper_key(self):
        # 这里不再主动触发奖励，改为彩蛋参数里被触发后调用
        self.global_data.setdefault("news_feed", []).append({
            "time": datetime.now(tz).isoformat(),
            "content": f"🌟 轰动绿洲！{self.nickname} 解锁了神秘彩蛋，夺得传说中的青铜钥匙和百万绿洲币巨额奖励！"
        })

        self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + 1_000_000
        self.add_simple_item(
            "青铜钥匙", 1,
            "这把复古铜钥头雕刻着神秘谜语，传说能开启绿洲最隐秘的冒险之门。"
        )

        return "\n".join([
            "🌈 你在暗影中发现了隐藏的秘密通道！",
            "🚗 逆行穿越霓虹闪烁的街道，霓虹光影映出你的决心...",
            "🔑 手握传说——青铜钥匙，仿佛能解开所有谜团！",
            "💰 巨额奖金滚滚而来，1000000 绿洲币瞬间到账！",
            "🏆 你的名字已刻进传奇排行榜，绿洲的英雄！",
            f"💎 当前账户余额：{self.user_data['oasis_coins']} 绿洲币"
        ])

    # 彩票模块
    def buy_lottery(self, count=1):
        """购买指定数量的彩票（默认1张），立即开奖"""
        # 日期和今日购买彩票记录
        today = datetime.now(tz).date().isoformat()
        today_tickets = [t for t in self.user_data["lottery_tickets"] if t["date"] == today]
        remaining = self.lottery_config["max_daily"] - len(today_tickets)

        if remaining <= 0:
            return "⚠️ 今日彩票购买已达上限（100张）"

        # 限制购买数量
        count = min(count, remaining)
        if count <= 0:
            return "⚠️ 无效的购买数量"

        result = [f"🎫 你准备购买 {count} 张彩票："]
        total_spent = 0
        total_prize = 0
        tickets_bought = 0

        for _ in range(count):
            # 随机选择彩票类型
            lottery_type = random.choice(self.lottery_config["types"])
            price = lottery_type["price"]
            digits = lottery_type["digits"]
            prize_map = lottery_type["prize_map"]

            # 检查余额
            if self.user_data["oasis_coins"] < price:
                result.append(f"⚠️ 剩余余额不足，已停止购买。")
                break

            # 随机号码
            user_num = "".join(random.choices("0123456789", k=digits))
            winning_num = "".join(random.choices("0123456789", k=digits))
            match_count = sum(1 for u, w in zip(user_num, winning_num) if u == w)

            # 计算奖金
            prize = 0
            prize_desc = []
            for level, rule in prize_map.items():
                if match_count >= rule["match"]:
                    prize += rule["payout"]
                    prize_desc.append(f"{level}+{rule['payout']}币")

            # 更新余额
            self.user_data["oasis_coins"] += prize - price
            total_spent += price
            total_prize += prize
            tickets_bought += 1

            # 记录彩票信息
            ticket_record = {
                "type": lottery_type["name"],
                "user_num": user_num,
                "winning_num": winning_num,
                "prize": prize,
                "date": today,
                "time": datetime.now(tz).isoformat()
            }
            self.user_data["lottery_tickets"].append(ticket_record)

            # 显示信息
            line = (
                f"🎟️ [{lottery_type['name']}] "
                f"{user_num} → {winning_num} 匹配 {match_count}/{digits}"
            )
            if prize > 2000:
                line += f" 🎉中奖: {', '.join(prize_desc)}"
                self.global_data.setdefault("news_feed", []).append({
                    "time": ticket_record["time"],
                    "content": f"🎊 {self.nickname} 在 {lottery_type['name']} 彩票中中奖，获得 {prize} 绿洲币奖励！"
                })
            else:
                line += f" 💸未中奖"

            result.append(line)

        # 重新计算剩余次数（确保准确）
        remaining_after = self.lottery_config["max_daily"] - (len(today_tickets) + tickets_bought)

        # 汇总信息
        result.append("━" * 40)
        result.append(f"📊 本次购买：{tickets_bought} 张")
        result.append(f"💸 总支出：{total_spent}币")
        result.append(f"🎁 总奖金：{total_prize}币")
        result.append(f"💰 当前余额：{self.user_data['oasis_coins']}")
        result.append(f"📅 今日剩余购买次数：{remaining_after}")

        return "\n".join(result)

    def show_lottery_stats(self):
        """显示彩票统计信息"""
        today = datetime.now(tz).date().isoformat()
        today_tickets = [t for t in self.user_data["lottery_tickets"] if t["date"] == today]
        total_spent = sum(self.lottery_config["types"][t["type"]]["price"] for t in today_tickets)
        total_prize = sum(t["prize"] for t in today_tickets)

        stats = [
            "📊 今日彩票统计",
            f"▸ 购买数量: {len(today_tickets)}/{self.lottery_config['max_daily']}",
            f"▸ 总支出: {total_spent}币",
            f"▸ 总奖金: {total_prize}币",
            f"▸ 净收益: {total_prize - total_spent}币",
            "🕒 最近5笔交易:"
        ]

        for t in today_tickets[-5:][::-1]:
            status = f"+{t['prize']}" if t["prize"] > 0 else f"-{self.lottery_config['types'][t['type']]['price']}"
            stats.append(
                f"[{t['time'][11:16]}] {t['type']} "
                f"{t['user_num']}→{t['winning_num']} {status}币"
            )

        return "\n".join(stats)

    # ————————————————————商城模块————————————————————

    # 商城帮助
    @staticmethod
    def _shop_help(test):
        return (
            "🛒 shop 命令列表：\n"
            "- shop sell 名称 价格 [描述]    上架商品\n"
            "- shop buy 商品ID              购买商品\n"
            "- shop cancel 商品ID           取消自己上架的商品\n"
            "- shop market [页码]           查看商城\n"
            "- shop mystats                 查看个人售卖记录\n"
            "- shop help                    查看帮助\n"
            "- shop clear_all               （管理员）清空商城商品"
        )

    def _shop_market_wrapper(self, test):

        return self.show_marketplace()

    # 展示商城

    def show_marketplace(self):
        marketplace = self.global_data.get("marketplace", {})
        on_sale_items = [item for item in marketplace.get("items", []) if item.get("status") == "on_sale"]

        best_items = {}
        for item in on_sale_items:
            item_id = item["item"]["id"]
            if item_id not in best_items or item["price"] < best_items[item_id]["price"]:
                best_items[item_id] = item

        unique_items = list(best_items.values())

        def strip_timezone(dt):
            return dt.replace(tzinfo=None)

        result = [
            "🛒 绿洲商城 - 在售物品",
            f"📊 总商品数: {len(unique_items)}",
            "━" * 40
        ]

        for item in unique_items:
            time_ago = (datetime.now() - strip_timezone(datetime.fromisoformat(item["time"]))).days
            result.append(
                f"🆔 {item['id']}\n"
                f"📦 {item['item']['name']} - {item['price']}绿洲币\n"
                f"👤 卖家: {item['seller_name']}\n"
                f"📝 {item['description']}\n"
                f"⏱️ 上架于{time_ago}天前\n"
                f"💡 输入 buy {item['id']} 购买\n"
                "━" * 20
            )

        if not unique_items:
            result.append("商城目前没有在售物品")

        return "\n".join(result)

    # 购与卖模块


    def handle_sell_command(self, cmd_parts):
        """处理售卖命令：shop sell <物品名称> <价格> [描述]"""

        if len(cmd_parts) < 3:
            return "❌ 格式错误，正确格式: shop sell <物品名称> <价格> [描述]"

        item_name = cmd_parts[1]

        # 价格验证
        try:
            price = int(cmd_parts[2])
            if price <= 0:
                return "❌ 价格必须是正整数，例如：shop sell 水枪 100"
            elif price > 1000000:
                return "❌ 价格不能超过 100w"
        except ValueError:
            return "❌ 价格格式错误，必须是整数，例如：shop sell 水枪 100"

        # 描述拼接
        description = " ".join(cmd_parts[3:]) if len(cmd_parts) > 3 else "无描述"

        inventory = self.user_data.get("inventory", [])
        item_index = next((i for i, item in enumerate(inventory) if item.get("name") == item_name), None)

        if item_index is None:
            return f"❌ 背包中没有名为 '{item_name}' 的物品"

        item = inventory[item_index]

        # 初始化市场数据结构
        if "marketplace" not in self.global_data:
            self.global_data["marketplace"] = {"items": [], "transactions": []}
        elif "items" not in self.global_data["marketplace"]:
            self.global_data["marketplace"]["items"] = []

        # 检查该玩家是否已挂售相同物品（避免重复）
        for listing in self.global_data["marketplace"]["items"]:
            if (
                    listing.get("seller_id") == self.user_id and
                    listing.get("item", {}).get("name") == item_name and
                    listing.get("status") == "on_sale"
            ):
                return f"⚠️ 你已经上架了名为 '{item_name}' 的物品，不能重复上架"

        # 拷贝物品数据
        item_copy = item.copy()
        item_copy["quantity"] = 1  # 上架数量为 1

        # 从玩家背包扣除
        if item.get("quantity", 1) > 1:
            item["quantity"] -= 1
        else:
            inventory.pop(item_index)

        # 创建商品 ID
        listing_id = str(uuid.uuid4())[:8]

        listing = {
            "id": listing_id,
            "seller_id": self.user_id,
            "seller_name": self.nickname,
            "item": item_copy,
            "price": price,
            "description": description,
            "time": datetime.now(tz).isoformat(),
            "status": "on_sale"
        }

        # 添加至市场
        self.global_data["marketplace"]["items"].append(listing)

        # 初始化玩家 market 数据结构
        if "market" not in self.user_data:
            self.user_data["market"] = {}
        if "selling" not in self.user_data["market"]:
            self.user_data["market"]["selling"] = []
        if "sold" not in self.user_data["market"]:
            self.user_data["market"]["sold"] = 0
        if "earned" not in self.user_data["market"]:
            self.user_data["market"]["earned"] = 0

        self.user_data["market"]["selling"].append(listing_id)

        return (
            f"✅ 成功上架物品!\n"
            f"📦 物品: {item['name']}\n"
            f"💰 价格: {price} 绿洲币\n"
            f"📝 描述: {description}\n"
            f"🆔 商品ID: {listing_id}\n"
            f"💡 其他玩家可用指令: shop buy {listing_id} 进行购买"
        )

    def handle_buy_command(self, cmd_parts):
        """处理购买命令 buy <商品ID>"""
        if len(cmd_parts) < 1:
            return "❌ 格式错误，正确格式: shop buy <商品ID>"

        listing_id = cmd_parts[1]
        marketplace = self.global_data.get("marketplace", {})
        listings = marketplace.get("items", [])

        listing = next((item for item in listings if item["id"] == listing_id and item["status"] == "on_sale"), None)
        if not listing:
            return "❌ 未找到该商品或已售出"

        if listing["seller_id"] == self.user_id:
            return "❌ 你不能购买自己上架的商品"

        if self.user_data["oasis_coins"] < listing["price"]:
            return f"❌ 余额不足，需 {listing['price']} 绿洲币"

        self.user_data["oasis_coins"] -= listing["price"]

        seller_data = self.global_data["users"].get(listing["seller_id"])
        if seller_data:
            seller_data["oasis_coins"] += listing["price"]
            if "market" not in seller_data:
                seller_data["market"] = {"selling": [], "sold": 0, "earned": 0}
            if listing_id in seller_data["market"].get("selling", []):
                seller_data["market"]["selling"].remove(listing_id)
            seller_data["market"]["sold"] += 1
            seller_data["market"]["earned"] += listing["price"]

        self.add_item(
            item_id=listing["item"]["id"],
            name=listing["item"]["name"],
            item_type=listing["item"].get("type", "其他"),
            quantity=1,
            description=listing["item"].get("description", "")
        )

        listing["status"] = "sold"
        listing["buyer_id"] = self.user_id
        listing["buyer_name"] = self.nickname
        listing["sold_time"] = datetime.now(tz).isoformat()

        if "transactions" not in self.global_data["marketplace"]:
            self.global_data["marketplace"]["transactions"] = []

        self.global_data["marketplace"]["transactions"].append({
            "listing_id": listing_id,
            "item_name": listing["item"]["name"],
            "price": listing["price"],
            "seller": listing["seller_id"],
            "buyer": self.user_id,
            "time": listing["sold_time"]
        })

        return (
            f"✅ 购买成功!\n"
            f"📦 你获得了: {listing['item']['name']}\n"
            f"💰 花费: {listing['price']} 绿洲币\n"
            f"👤 卖家: {listing['seller_name']}\n"
            f"💳 当前余额: {self.user_data['oasis_coins']}"
        )

    def handle_cancel_command(self, cmd_parts):
        """玩家取消上架的商品"""
        if len(cmd_parts) < 1:
            return "❌ 格式错误，正确格式: shop cancel <商品ID>"

        listing_id = cmd_parts[0]
        marketplace = self.global_data.get("marketplace", {})
        listings = marketplace.get("items", [])

        # 查找 listing
        listing = next((item for item in listings if item["id"] == listing_id), None)
        if not listing:
            return "❌ 未找到该商品 ID"

        # 检查是否为本人挂单
        if listing["seller_id"] != self.user_id:
            return "❌ 你只能取消自己发布的商品"

        # 检查是否仍在售
        if listing["status"] != "on_sale":
            return "⚠️ 商品已售出或已下架，无法取消"

        # 设置状态
        listing["status"] = "cancelled"
        listing["cancel_time"] = datetime.now(tz).isoformat()

        # 移除用户挂单记录
        if "market" in self.user_data and "selling" in self.user_data["market"]:
            self.user_data["market"]["selling"] = [
                x for x in self.user_data["market"]["selling"] if x != listing_id
            ]

        # 把物品还给玩家
        item = listing["item"]
        self.add_item(
            item_id=item["id"],
            name=item["name"],
            item_type=item.get("type", "其他"),
            quantity=1,
            description=item.get("description", "")
        )

        return (
            f"✅ 已成功取消上架商品\n"
            f"📦 物品: {item['name']} 已退回背包"
        )

    # 商城统计模块
    def show_selling_stats(self, test):
        """显示个人售卖统计"""
        marketplace = self.global_data["marketplace"]
        user_selling = [item for item in marketplace["items"]
                        if item["seller_id"] == self.user_id and item["status"] == "on_sale"]
        user_sold = [item for item in marketplace["items"]
                     if item["seller_id"] == self.user_id and item["status"] == "sold"]

        result = [
            f"📊 {self.nickname} 的售卖统计",
            f"💰 总收益: {self.user_data['market']['earned']}绿洲币",
            f"📦 已售出: {self.user_data['market']['sold']}件",
            f"🛒 在售中: {len(user_selling)}件",
            "━" * 30,
            "📌 在售物品:"
        ]

        for item in user_selling:
            result.append(
                f"🆔 {item['id']} - {item['item']['name']} "
                f"{item['price']}绿洲币\n"
                f"📝 {item['description']}"
            )

        if not user_selling:
            result.append("暂无在售物品")

        result.append("━" * 30)
        result.append("📌 最近售出:")

        for item in user_sold[-3:]:  # 显示最近3笔
            result.append(
                f"⏱️ {datetime.fromisoformat(item['sold_time']).strftime('%m-%d')} "
                f"{item['item']['name']} → {item.get('buyer_name', '未知买家')} "
                f"+{item['price']}币"
            )

        if not user_sold:
            result.append("暂无售出记录")

        return "\n".join(result)

    # 商城命令处理模块
    def handle_shop_command(self, cmd_parts):
        if "MARKET" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"
        if len(cmd_parts) < 2:
            return self._shop_help(1)

        sub_cmd = cmd_parts[1].lower()

        shop_command_map = {
            "sell": self.handle_sell_command,
            "buy": self.handle_buy_command,
            "cancel": self.handle_cancel_command,
            "下架": self.handle_cancel_command,
            "market": self._shop_market_wrapper,
            "商城": self._shop_market_wrapper,
            "mystats": self.show_selling_stats,
            "help": self._shop_help,
            "帮助": self._shop_help,
        }

        handler = shop_command_map.get(sub_cmd)
        if not handler:
            return f"❓ 未知 shop 子命令 '{sub_cmd}'，输入 shop help 查看用法"

        return handler(cmd_parts[1:])



    # ——————————————————DC游戏模块——————————————————————————————
    @staticmethod
    def dc_help():
        help_text = """
    🎲【DC 模块帮助菜单】欢迎来到绿洲娱乐中心！

    🪙 DC玩法：
    - `dc yaya`：进入 yaya🦆游戏
    - `dc 幸运轮盘` / `dc lucky`：每日免费一次，随机抽奖赢道具或绿洲币
    - `dc 栗子机` / `dc 栗子机 <数额>`
    - `dc 动物赛跑 🐰`：动物赛跑，下🐖支持喜欢的动物（如 🐷）
    - `dc 足球 ⚽️`：支持喜欢的国家队，晚上 8 点开奖！

    📈 投注规则：
    - 每种游戏各有下🐖限制与概率计算，详情查看对应玩法说明
    - 动物/足球下🐖后将收到开奖提示消息

    📣 其他指令：
    - `dc 记录`：查看你的历史中奖记录（开发中）
    - `dc 排行榜`：查看DC赢家排行榜（开发中）
    - `dc 帮助` / `dc help`：查看此帮助菜单
    """
        return help_text.strip()

    def casino_game(self, game_type, *args):
        def safe_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # 游戏预设及下🐖验证
        game_type = game_type.strip() if isinstance(game_type, str) else ""
        if game_type not in ["栗子机", "yaya", "轮盘"]:
            return "❌ 不支持的游戏类型，请输入：栗子机 / yaya / 轮盘"

        # 参数解析
        bet_type = None
        amount = 0

        # 参数校验逻辑优化
        if game_type == "轮盘":
            if len(args) != 2:
                return "⚠️ 格式错误！轮盘正确格式：dc 轮盘 <红/黑/数字/奇数/偶数> <金额>"
            bet_type, amount = args[0], args[1]
            if not bet_type.strip():
                return "⚠️ 请提供轮盘下🐖类型"
        else:
            if len(args) != 1:
                return f"⚠️ 格式错误！正确格式：dc {game_type} <金额>"
            amount = args[0]

        # 金额解析
        amount = str(amount).lower()
        if amount == "allin":
            amount = self.user_data["oasis_coins"]
        else:
            amount = safe_int(amount)

        if amount <= 0:
            return "❌ 金额必须大于0"
        if amount > self.user_data["oasis_coins"]:
            return f"❌ 余额不足！当前余额为 {self.user_data['oasis_coins']}"
        if amount > 10000000:
            return "⚠️ 单次下🐖上限为 10000000 绿洲币"

        # 通用数据结构
        from random import choice, randint

        def calculate_hand(cards):
            total, aces = 0, 0
            for card in cards:
                val = card[:-1]
                if val in ["J", "Q", "K"]:
                    total += 10
                elif val == "A":
                    total += 11
                    aces += 1
                else:
                    total += int(val)
            while total > 21 and aces:
                total -= 10
                aces -= 1
            return total

        # ---------------------- 栗子机 ----------------------
        # 游戏类型为栗子机
        if game_type == "栗子机":
            symbols = ["🦆", "🪵", "🌰", "7️⃣", "🧪", "🍀", "🥕"]

            has_luck_grass = self.has_item("luck_grass")

            def fix_clover_to_match(roll):
                """
                如果有两个图案相同，另一个是🍀，就把🍀换成相同图案
                """
                counts = {}
                for i, symbol in enumerate(roll):
                    if symbol != "🍀":
                        counts[symbol] = counts.get(symbol, []) + [i]

                for sym, indices in counts.items():
                    if len(indices) == 2:
                        other_index = [i for i in range(3) if i not in indices][0]
                        if roll[other_index] == "🍀":
                            roll[other_index] = sym
                            return True  # 转换成功
                return False

            def score(cards):
                return 3 if cards[0] == cards[1] == cards[2] else 0

            def generate_roll_with_clover_bonus():
                roll1 = [choice(symbols) for _ in range(3)]
                fixed1 = fix_clover_to_match(roll1) if has_luck_grass else False

                if has_luck_grass and random.random() < 0.5:
                    roll2 = [choice(symbols) for _ in range(3)]
                    fixed2 = fix_clover_to_match(roll2)

                    if score(roll2) > score(roll1):
                        return roll2, fixed2
                    else:
                        return roll1, fixed1
                else:
                    return roll1, fixed1

            roll, clover_triggered = generate_roll_with_clover_bonus()

            def check_line(cards):
                if cards[0] == cards[1] == cards[2]:
                    if cards[0] == "🌰": return "三栗", 100
                    if cards[0] == "🥕": return "三栗", 80
                    if cards[0] == "🦆": return "三栗", 60
                    if cards[0] == "7️⃣": return "头奖777", 50
                    return "三连相同", 20
                return "未中奖", 0

            outcome, multiplier = check_line(roll)
            win = amount * multiplier
            net = win - amount
            self.user_data["oasis_coins"] += net

            bonus_msg = ""
            if has_luck_grass:
                if clover_triggered:
                    bonus_msg = " 🍀幸运草自动凑成三连！"
                else:
                    bonus_msg = " 🍀幸运草效果已应用！"

            return f"""🎰 栗子机结果: {' | '.join(roll)}
        🎯 {outcome} ×{multiplier}{bonus_msg}
        💰 {'赢得' if net >= 0 else '损失'} {abs(net)}币
        🏦 当前余额: {self.user_data['oasis_coins']}"""

        # ---------------------- yaya ----------------------
        if game_type == "yaya":
            def deal_card():
                return choice(["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]) + choice(
                    ["🦆", "🐟", "🐤", "🐰"])

            # 发牌流程调整
            player = [deal_card(), deal_card()]
            dealer = [deal_card(), deal_card()]

            # 玩家决策（基本策略）
            pt = calculate_hand(player)
            while pt < 17:  # 基础策略：不足17点继续要牌
                player.append(deal_card())
                pt = calculate_hand(player)
                if pt > 21:
                    break  # 爆牌立即停止

            # 庄家逻辑（保持暗牌特性）
            dt = calculate_hand([dealer[0]])  # 只显示庄家第一张牌
            while dt < 17:
                dealer.append(deal_card())
                dt = calculate_hand(dealer)

            # 结果计算（保持原逻辑）
            if pt > 21:
                result = "💥 玩家爆牌"
                win = -amount
            elif dt > 21 or pt > dt:
                result = "🎉 玩家获胜"
                win = int(amount * 1.5) if len(player) == 2 and pt == 21 else amount  # 黑杰克判断
            else:
                result = "💸 庄家胜利"
                win = -amount

            self.user_data["oasis_coins"] += win
            return f"""🦆 yaya牌结果：
        玩家: {', '.join(player)} = {pt}
        庄家: {dealer[0]} [?] → {', '.join(dealer)} = {dt}
        {result}
        💰 {'赢得' if win > 0 else '损失'} {abs(win)}币
        🏦 当前余额: {self.user_data['oasis_coins']}"""

        # ---------------------- 轮盘 ----------------------
        if game_type == "轮盘":
            spin = randint(0, 36)
            color = "红" if spin % 2 == 1 and spin != 0 else "黑"

            def check_roulette(bet):
                if bet == str(spin): return "🎯 精准数字命中", 35
                if bet == color: return "🎨 颜色命中", 1
                if bet == "奇数" and spin % 2 == 1: return "🔢 奇数命中", 1
                if bet == "偶数" and spin % 2 == 0 and spin != 0: return "🔢 偶数命中", 1
                return "💤 未中奖", 0

            result, multiplier = check_roulette(str(bet_type))
            win = amount * multiplier
            self.user_data["oasis_coins"] += win  # 赢得的钱是 amount × multiplier

            return (
                f"🎡 轮盘结果：{spin} {color}色\n"
                f"{result} ×{multiplier}\n"
                f"💰 获得 {win}币（含本金）\n"
                f"🏦 当前余额: {self.user_data['oasis_coins']}"
            )
        return None

        # 期望值参考（单次下🐖100）:
        # 栗子机：仅三连中奖，期望约 0.4 左右（可调）
        # 21点：理论期望约为 0.97（近似）
        # 轮盘：红/黑/奇/偶 期望 = 0.947；单数字 = 0.947

    def handle_casino_command(self, cmd_parts):
        if "DC" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"


        game_type = cmd_parts[1]
        if game_type in ["help", "h", "帮助"]:
            return self.dc_help()
        elif game_type in ["幸运轮盘", "lucky"]:
            return self.handle_lucky_roulette()
        elif game_type == "轮盘":
            if len(cmd_parts) < 4 or not cmd_parts[3].strip():
                return "⚠️ 轮盘参数错误！正确格式：dc 轮盘 <红/黑/单数字> <金额>"
            return self.casino_game(game_type, cmd_parts[2], cmd_parts[3])

        elif game_type in ["yaya"]:
            return self.casino_game(game_type, cmd_parts[2])

        elif game_type == "动物赛跑":
            if cmd_parts[2] == "帮助":
                return self.get_race_help()
            if len(cmd_parts) < 4:
                return "⚠️ 格式错误！例：dc 动物赛跑 兔子 2000"
            elif cmd_parts[2] is None:
                return self.get_race_help()
            return self.handle_dc_race_bet(cmd_parts[2], cmd_parts[3])

        elif game_type == "足球":
            if cmd_parts[2] == "帮助":
                return self.get_football_help()
            if len(cmd_parts) < 4:
                return "⚠️ 格式错误！例：dc 足球 巴西 1000"
            elif cmd_parts[2] is None:
                return self.get_race_help()
            return self.handle_dc_football_bet(cmd_parts[2], cmd_parts[3])
        elif game_type in ["记录", "bet"]:
            return self.handle_dc_bet_record()
        elif game_type in ["resolve"]:
            return self.auto_handle_resolve_command()
        else:
            if not cmd_parts[2].strip():
                return f"⚠️ 需要有效金额！例：dc {game_type} 5000"
            return self.casino_game(game_type, cmd_parts[2])

    def auto_handle_resolve_command(self):

        now = datetime.now(tz)
        now_time = now.time()
        today = now.date()

        # 定义触发时间段
        football_start = time(20, 0, 0)
        football_end = time(20, 59, 59)

        race_start = time(12, 0, 0)
        race_end = time(12, 59, 59)

        # 初始化触发记录字典，如果没则初始化
        if "last_resolve_date" not in self.global_data:
            self.global_data["last_resolve_date"] = {
                "football": None,
                "race": None,
            }

        last_football = self.global_data["last_resolve_date"].get("football")
        last_race = self.global_data["last_resolve_date"].get("race")

        # 判断足球赛是否今天已结算过
        if football_start <= now_time <= football_end:
            if last_football == today.isoformat():
                return "⚽️ 足球比赛今天已经结算过了，明天再来吧"
            else:
                result = self.resolve_football_match()
                self.global_data["last_resolve_date"]["football"] = today.isoformat()
                return result

        # 判断动物赛跑是否今天已结算过
        if race_start <= now_time <= race_end:
            if last_race == today.isoformat():
                return "🐰 动物赛跑今天已经结算过了，明天再来吧"
            else:
                result = self.resolve_race_game()
                self.global_data["last_resolve_date"]["race"] = today.isoformat()
                return result

        return "❌ 当前时间非结算时间，足球赛为晚上8点，动物赛跑为中午12点"

    def handle_resolve_command(self, cmd_parts):
        if self.user_id not in self.admin_ids:
            return "⛔ 仅管理员可以执行结算操作"


        if cmd_parts[0] in ["足球", "football"]:
            return self.resolve_football_match()
        elif cmd_parts[0] in ["动物", "动物赛跑"]:
            return self.resolve_race_game()
        else:
            return "❌ 无效类型，可选：足球 / 动物赛跑"


    # 幸运轮盘
    def handle_lucky_roulette(self):
        now = datetime.now(tz)
        today = now.strftime("%Y-%m-%d")  # 格式化为 "YYYY-MM-DD"
        last_spin = self.user_data.get("last_lucky_spin", "")
        if last_spin == today:
            return "🎡 你今天已经转过幸运轮盘啦，明天再来吧~"

        # 设置奖池
        reward_pool = [
            {"type": "coin", "amount": 50, "desc": "日常奖励", "weight": 30},
            {"type": "coin", "amount": 100, "desc": "运气不错", "weight": 20},
            {"type": "coin", "amount": 300, "desc": "欧气爆棚", "weight": 10},
            {"type": "item", "id": "luck_grass", "name": "🍀 幸运草", "desc": "据说会提升你的运气", "qty": 1,
             "weight": 15},
            {"type": "item", "id": "lab_flask", "name": "🧪 实验罐", "desc": "可能用于某些合成任务", "qty": 1,
             "weight": 10},
            {"type": "item", "id": "gem_box", "name": "💎 宝石箱", "desc": "打开后有意外之喜", "qty": 1, "weight": 5},
            {"type": "item", "id": "egg_fragment", "name": "🎭 彩蛋碎片", "desc": "集齐或可触发神秘剧情", "qty": 1,
             "weight": 5},
            {"type": "none", "desc": "💣 空手而归", "weight": 5}
        ]

        reward = random.choices(reward_pool, weights=[r["weight"] for r in reward_pool])[0]
        self.user_data["last_lucky_spin"] = today

        # 发奖处理
        if reward["type"] == "coin":
            return f"🎡 幸运轮盘转动中...\n" + self.add_reward(reward["amount"], reward["desc"])

        elif reward["type"] == "item":
            return (
                    f"🎡 幸运轮盘转动中...\n"
                    f"🎁 恭喜你获得了道具：{reward['name']} ×{reward['qty']}\n" +
                    self.add_simple_item(
                        item_id=reward["id"],
                        quantity=reward["qty"],
                        description=reward["desc"]
                    )
            )

        else:  # 空手而归
            return "🎡 幸运轮盘转动中...\n💣 啊哦，你什么都没转到，再接再厉吧！"

    # DC足球模块
    def handle_dc_football_bet(self, team_name, amount):
        TEAM_MAP = {
            "阿根廷": "🇦🇷", "法国": "🇫🇷", "巴西": "🇧🇷", "德国": "🇩🇪", "日本": "🇯🇵",
            "🇦🇷": "🇦🇷", "🇫🇷": "🇫🇷", "🇧🇷": "🇧🇷", "🇩🇪": "🇩🇪", "🇯🇵": "🇯🇵"
        }
        team = TEAM_MAP.get(team_name)
        if not team:
            return f"⚽ 无效国家，支持队伍：{' / '.join(TEAM_MAP.keys())}"

        amount = int(amount)
        if amount <= 0:
            return "⚠️ 金额必须大于0"
        if amount > self.user_data["oasis_coins"]:
            return f"❌ 余额不足！当前余额为 {self.user_data['oasis_coins']}"

        now = datetime.now(tz)
        match_time = time(20, 0, 0)
        today = now.date()

        if now.time() >= match_time:
            bet_date = today + timedelta(days=1)
            note = "比赛将在明天晚上20:00开始"
        else:
            bet_date = today
            note = "比赛将在今晚20:00开始"

        bet_date_str = bet_date.strftime("%Y-%m-%d")

        self.user_data["oasis_coins"] -= amount

        self.global_data.setdefault("football_bets", {})
        self.global_data["football_bets"].setdefault(bet_date_str, {})
        self.global_data["football_bets"][bet_date_str].setdefault(team, [])

        self.global_data["football_bets"][bet_date_str][team].append({
            "user_id": self.user_id,
            "amount": amount,
            "nickname": self.nickname
        })

        return f"✅ 下🐖成功！你为【{team_name}】下🐖了 {amount} 绿洲币\n🏟️ {note}，赛后将通知结果"

    def resolve_football_match(self):
        today = datetime.now(tz).strftime("%Y-%m-%d")
        bets = self.global_data.get("football_bets", {}).pop(today, None)
        if not bets:
            return "📭 今天无人下🐖，比赛取消"

        import random
        winning_team = random.choice(list(bets.keys()))
        total_pool = sum(sum(p["amount"] for p in lst) for lst in bets.values())
        winners = bets[winning_team]
        winner_total = sum(p["amount"] for p in winners)

        # 比赛过程描述随机池
        match_descriptions = [
            "开场第5分钟就进球，气势如虹！",
            "双方鏖战90分钟，最后补时绝杀！",
            "点球大战决胜负，门将扑出关键一球！",
            "上半场被压制，下半场逆风翻盘！",
            "中场调整奏效，连进两球逆转比赛！"
        ]
        match_summary = random.choice(match_descriptions)

        for team, players in bets.items():
            for p in players:
                uid = str(p["user_id"])
                is_winner = (team == winning_team)
                coins_won = int((p["amount"] / winner_total) * total_pool) if is_winner else 0

                msg = f"⚽️ 今日足球比赛结果：{winning_team} 获胜！\n"
                msg += f"📖 比赛回顾：{match_summary}\n"
                if is_winner:
                    self.global_data["users"][uid]["oasis_coins"] += coins_won
                    msg += f"🎉 你支持的球队赢了！获得 {coins_won} 绿洲币奖励"
                else:
                    msg += f"💔 你支持的【{team}】未获胜，未获得奖励"

                self.global_data["users"][uid].setdefault("inbox", []).append({
                    "from": "⚽️ 足球系统",
                    "time": datetime.now(tz).isoformat(),
                    "content": msg
                })

        return f"✅ 今日足球比赛已结算，胜队：{winning_team}，奖金已发放"

    # DC动物模块
    def handle_dc_race_bet(self, animal_name, amount):
        ANIMAL_MAP = {
            "兔子": "🐰", "🐰": "🐰",
            "猪": "🐷", "🐷": "🐷",
            "乌龟": "🐢", "🐢": "🐢",
            "青蛙": "🐸", "🐸": "🐸",
            "狗": "🐶", "🐶": "🐶"
        }
        animal = ANIMAL_MAP.get(animal_name)
        if not animal:
            return f"🐾 无效动物，请输入：{' / '.join(ANIMAL_MAP.keys())}"

        # 下🐖合法性检查
        amount = int(amount)
        if amount <= 0:
            return "⚠️ 金额必须大于0"
        if amount > self.user_data["oasis_coins"]:
            return f"❌ 余额不足，当前余额为 {self.user_data['oasis_coins']}"

        # 判断当前时间
        now = datetime.now(tz)
        noon_time = time(12, 0, 0)
        today = now.date()

        if now.time() >= noon_time:
            # 如果已经过了中午12点，下🐖算到明天
            bet_date = today + timedelta(days=1)
            note = "明天中午12:00"
        else:
            bet_date = today
            note = "今天中午12:00"

        bet_date_str = bet_date.strftime("%Y-%m-%d")

        # 扣除下🐖金额
        self.user_data["oasis_coins"] -= amount

        # 记录下🐖
        self.global_data.setdefault("race_bets", {})
        self.global_data["race_bets"].setdefault(bet_date_str, {})
        self.global_data["race_bets"][bet_date_str].setdefault(animal, [])

        self.global_data["race_bets"][bet_date_str][animal].append({
            "user_id": self.user_id,
            "amount": amount,
            "nickname": self.nickname
        })

        return f"✅ 你为 {animal_name} 下🐖了 {amount} 绿洲币，比赛将在{note}举行！"

    def resolve_race_game(self):
        today = datetime.now(tz).strftime("%Y-%m-%d")
        bets = self.global_data.get("race_bets", {}).pop(today, None)
        if not bets:
            return "🐾 今日无人下🐖，动物赛跑取消"

        import random
        winning_animal = random.choice(list(bets.keys()))
        total_pool = sum(sum(p["amount"] for p in lst) for lst in bets.values())
        winners = bets[winning_animal]
        winner_total = sum(p["amount"] for p in winners)

        # 🔧 比赛过程描述池
        race_descriptions = [
            "比赛一开始，{animal}猛地冲出起跑线，观众席瞬间爆发欢呼！",
            "{animal}中途一度落后，但关键时刻一跃而起完成超车！",
            "{animal}一路领先，其他动物根本追不上它的尾巴！",
            "在终点前最后五米，{animal}加速冲刺，惊险夺冠！",
            "{animal}起初不被看好，结果逆袭称王，现场沸腾！",
        ]

        for animal, players in bets.items():
            for p in players:
                uid = str(p["user_id"])
                is_winner = (animal == winning_animal)
                coins_won = int((p["amount"] / winner_total) * total_pool) if is_winner else 0

                # 🔧 随机选择一个过程描述
                race_process = random.choice(race_descriptions).format(animal=winning_animal)

                msg = f"🏁 今日动物赛跑冠军是：{winning_animal}！\n"
                msg += f"📜 比赛回顾：{race_process}\n"
                if is_winner:
                    self.global_data["users"][uid]["oasis_coins"] += coins_won
                    msg += f"🎉 你支持的{animal}赢了！你获得了 {coins_won} 绿洲币奖励"
                else:
                    msg += f"💨 你支持的{animal}没能拿第一，下次加油！"

                self.global_data["users"][uid].setdefault("inbox", []).append({
                    "from": "🏁 动物赛跑系统",
                    "time": datetime.now(tz).isoformat(),
                    "content": msg
                })

        return f"✅ 动物赛跑已结算，冠军：{winning_animal}，奖励已发放"

    def handle_dc_bet_record(self):
        today = datetime.now(tz).strftime("%Y-%m-%d")
        result = []

        # 足球下🐖记录
        football = self.global_data.get("football_bets", {}).get(today, {})
        football_result = []
        for team, lst in football.items():
            for p in lst:
                if p["user_id"] == self.user_id:
                    football_result.append(f"⚽ {team}：{p['amount']} 币")
        if football_result:
            result.append("🎯 今日你下🐖的足球队伍：\n" + "\n".join(football_result))

        # 动物下🐖记录
        race = self.global_data.get("race_bets", {}).get(today, {})
        race_result = []
        for animal, lst in race.items():
            for p in lst:
                if p["user_id"] == self.user_id:
                    race_result.append(f"🐾 {animal}：{p['amount']} 币")
        if race_result:
            result.append("🏁 今日你下🐖的动物赛跑：\n" + "\n".join(race_result))

        return "\n\n".join(result) if result else "📭 你今天尚未下🐖任何项目"

    def get_race_help(self):
        ANIMAL_MAP = {
            "兔子": "🐰", "🐰": "🐰",
            "猪": "🐷", "🐷": "🐷",
            "乌龟": "🐢", "🐢": "🐢",
            "青蛙": "🐸", "🐸": "🐸",
            "狗": "🐶", "🐶": "🐶"
        }
        animals = set(ANIMAL_MAP.values())
        today = datetime.now(tz).strftime("%Y-%m-%d")
        race_bets = self.global_data.get("race_bets", {}).get(today, {})

        info = [f"🎮 【动物赛跑帮助】", "每人可下🐖一只动物，胜者瓜分奖池", "当前可选："]
        info.append(" ".join(animals))
        info.append("\n📊 当前下🐖情况：")

        total = sum(sum(p['amount'] for p in lst) for lst in race_bets.values()) or 1
        for a in animals:
            bets = race_bets.get(a, [])
            amt = sum(p["amount"] for p in bets)
            pct = round(amt / total * 100)
            info.append(f"{a}：{amt}币（{pct}%）")

        return "\n".join(info)

    def get_football_help(self):
        TEAM_MAP = {
            "阿根廷": "🇦🇷", "法国": "🇫🇷", "巴西": "🇧🇷", "德国": "🇩🇪", "日本": "🇯🇵",
            "🇦🇷": "🇦🇷", "🇫🇷": "🇫🇷", "🇧🇷": "🇧🇷", "🇩🇪": "🇩🇪", "🇯🇵": "🇯🇵"
        }
        teams = set(TEAM_MAP.values())
        today = datetime.now(tz).strftime("%Y-%m-%d")
        football_bets = self.global_data.get("football_bets", {}).get(today, {})

        info = [f"🎮 【足球竞猜帮助】", "选择国家队下🐖，晚上8点开奖", "支持国家："]
        info.append(" ".join(teams))
        info.append("\n📊 当前下🐖情况：")

        total = sum(sum(p['amount'] for p in lst) for lst in football_bets.values()) or 1
        for t in teams:
            bets = football_bets.get(t, [])
            amt = sum(p["amount"] for p in bets)
            pct = round(amt / total * 100)
            info.append(f"{t}：{amt}币（{pct}%）")

        return "\n".join(info)

    # 极限跳伞模块
    def extreme_skydiving(self, aircraft_choice):
        """重构后的极限跳伞模块"""
        # 验证飞机选择
        aircraft = self.air_crafts.get(aircraft_choice, None)
        if not aircraft:
            return "❌ 无效的飞机编号，可用选项：\n" + "\n".join(
                [f"{k}. {v['name']} ({v['cost']}绿洲币)"
                 for k, v in self.air_crafts.items()]
            )

        # 检查资金
        if self.user_data["oasis_coins"] < aircraft["cost"]:
            return f"❌ 资金不足！需要{aircraft['cost']}绿洲币租用{aircraft['name']}"

        # 扣费
        self.user_data["oasis_coins"] -= aircraft["cost"]

        # 初始化状态
        current_height = aircraft["base_height"]
        base_risk = 0.2 + aircraft["risk_mod"]
        total_score = 0
        bonus_multiplier = 1.0  # 视频质量系数

        result = [
            f"✈️【极限拍摄挑战 - {aircraft['name']}】",
            f"📷 赞助商合约：萝卜神能量饮料",
            f"🚁 起始高度：{current_height // 1000} 千米",
            f"💸 已支付租赁费：{aircraft['cost']} 绿洲币",
            f"✈ 载具描述：{aircraft['desc']}",
            "━" * 40
        ]

        # 主循环
        for minute in range(1, 60):
            # 3D6掷骰
            dice = sum(random.choices(range(1, 7), k=3))
            event = self.skydive_events[dice]

            # 处理事件效果
            effect_log = []
            for effect in event["effect"].split('|'):
                if current_height < 0:
                    result.append(f"🪂 高度跌破地面！{event['name']} 导致拍摄失败！")
                    total_score = 0
                    break
                if 'height' in effect:
                    if '*' in effect:
                        try:
                            factor = float(effect.split('*')[1])
                            delta = int(current_height * factor)
                        except ValueError:
                            delta = 0
                        current_height += delta
                        effect_log.append(f"高度变化: {delta:+}米")
                    else:
                        delta = int(effect.replace('height', '').strip())
                        current_height += delta
                        effect_log.append(f"高度变化: {delta:+}米")
                elif 'score' in effect:
                    if '*' in effect:
                        try:
                            factor = float(effect.split('*')[1])
                            total_score = int(total_score * factor)
                            effect_log.append(f"积分倍增: ×{factor}")
                        except ValueError:
                            pass
                    else:
                        delta = int(effect.replace('score', '').strip())
                        total_score += delta
                        effect_log.append(f"积分变化: {delta:+}")
                elif 'ascent' in effect:
                    pass  # 未来扩展

            # 基础爬升
            ascent = random.randint(*aircraft["ascent_rate"])
            current_height += ascent
            total_score += ascent * 1  # 每米1币基础奖励

            # 高度过低判断
            if current_height < 0:
                result.append(
                    f"💥【第{minute}分钟】{event['name']}！高度跌破地面，拍摄失败！"
                )
                total_score = 0
                break

            # 风险计算
            risk = max(0.0, base_risk + event["risk"])
            if random.random() < risk:
                result.append(
                    f"💥【第{minute}分钟】{event['name']}！"
                    f"风险率:{risk * 100:.1f}% → 拍摄失败！"
                )
                total_score = 0
                break

            # 奖励加成
            height_bonus = current_height // 100 * 1
            total_score += height_bonus

            result.append(
                f"⏱️【第{minute}分钟】{event['name']}\n"
                f"▸ {' | '.join(effect_log)}\n"
                f"▸ 当前高度: {current_height}米\n"
                f"▸ 累计收益: {total_score}绿洲币"
            )

            # 突破奖励加成
            if current_height >= 20000:
                bonus_multiplier *= 1.5
                result.append(f"🎉 突破2万米！赞助奖励翻倍！")
            elif current_height >= 10000:
                bonus_multiplier *= 1.2
                result.append(f"🌟 突破1万米！获得高空奖金！")
            elif current_height >= 5000:
                bonus_multiplier *= 1.1
                result.append(f"🌟 突破5000米！获得高空奖金！")

        # 最终结算
        final_score = int(total_score * bonus_multiplier)
        self.user_data["oasis_coins"] += final_score

        # 更新排行榜
        self.update_skydive_rank(current_height, final_score)

        result.append(
            "━" * 40 +
            f"\n🎬 拍摄结束！最终高度: {current_height}米\n"
            f"💰 获得赞助奖金: {final_score}绿洲币\n"
            f"💳 当前余额: {self.user_data['oasis_coins']}"
        )
        return "\n".join(result)

    def update_skydive_rank(self, height, score):
        """更新极限运动排行榜"""
        rank_entry = {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "height": height,
            "score": score,
            "time": datetime.now().isoformat()
        }

        # 初始化排行榜
        if "extreme_rank" not in self.global_data:
            self.global_data["extreme_rank"] = []

        # 更新记录
        self.global_data["extreme_rank"].append(rank_entry)
        # 保留前100名（按高度降序）
        self.global_data["extreme_rank"].sort(key=lambda x: x["height"], reverse=True)
        self.global_data["extreme_rank"] = self.global_data["extreme_rank"][:100]

    def show_extreme_rank(self):
        """显示极限运动排行榜"""
        display = [
            "🏆【极限运动排行榜】",
            "排名 | 玩家 | 最高高度 | 单次收益",
            "━" * 40
        ]

        for idx, entry in enumerate(self.global_data.get("extreme_rank", [])[:10], 1):
            display.append(
                f"{idx}. {entry['nickname']} "
                f"| {entry['height'] // 1000}千米{entry['height'] % 1000}米 "
                f"| {entry['score']}绿洲币"
            )

        return "\n".join(display)

    # 睡觉模块

    def sleep(self, input_text=None, with_user=None):
        # 判断当前睡眠状态
        if "SLEEP" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        state = self.user_data.get("sleep_state", "awake")

        if state == "deepsleep":
            return "💤 你正处于深度睡眠中，无法自行醒来。请输入 wake 指令才能醒过来。"

        # if state == "sleep":
        #     return "😴 你已经在梦乡了，继续享受你的梦境吧。"

        # 玩家刚刚进入睡眠
        self.user_data["sleep_state"] = "sleep"
        msg = ""

        # 这里随机决定是否进入深度睡眠（比如 30% 概率）
        if random.random() < 0.3:
            self.user_data["sleep_state"] = "deepsleep"
            msg += "你渐渐进入了深度睡眠，意识模糊，只有 wake 指令才能唤醒你。\n"

        # 原本的梦境事件逻辑，简化调用
        dream_msg = self._generate_dream_event(input_text=input_text, with_user=with_user)
        msg = dream_msg
        return msg

    def _generate_dream_event(self, input_text=None, with_user=None):
        """
        模拟玩家睡觉时梦到的事件。
        :param input_text: 玩家输入的梦境关键词（可选）
        :param with_user:   同梦对象名称（可选）
        """
        msg = "😴 你进入了梦乡...\n"
        self.user_data.setdefault("buffs", {})

        # 事件池按主题分类
        gain_pool = [
            {"coins": random.randint(5, 15), "text": "梦中你在古老宝藏里发现了一堆金币。"},
            {"coins": random.randint(8, 20), "text": "你梦见神秘商人赠送了你一袋绿洲币。"},
            {"coins": random.randint(10, 30), "text": "财神在梦里向你伸出援手，敲响了金库大门。"},
        ]
        lose_pool = [
            {"coins": random.randint(10, 200), "text": "入梦遭盗，布满裂痕的钱袋掉了几把币。"},
            {"coins": random.randint(60, 120), "text": "梦里被黑市骗子骗走了一笔钱…"},
            {"coins": random.randint(50, 150), "text": "梦中赌局失利，你破产醒来。"},
        ]
        romance_pool = [
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{name} 送给你一束美丽的鲜花，你们共享一个甜蜜的时刻。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "在梦中，你和 {name} 一起走在月光下，谈天说地，时光如流水般流逝。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {name} 一起翩翩起舞，心灵相通，世界变得柔和而美好。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {name} 在星空下共度良宵，仿佛整个宇宙都在为你们祝福。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦中，你和 {name} 一起度过一个浪漫的夜晚，心情愉悦，忘却一切烦恼。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{name} 轻轻拥抱你，温柔的气息让你心跳加速，难以忘怀。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {name} 在梦中共度激情时刻，彼此间的火花点燃了整个夜晚。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦里，{name} 低声在你耳畔呢喃，带着撩人的气息和深情的眷恋。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {name} 一起沉浸在温暖的拥抱中，感受彼此的体温与心跳交融。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{name} 轻抚你的脸颊，眼神深邃而炽热，让你无法抗拒这份诱惑。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦中你们共浴在月光下，水波荡漾，心与心的距离无限接近。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{name} 轻吻你的唇，细腻温柔，让人沉醉其中，忘却现实烦忧。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你们在梦里缠绵，爱意绵绵不绝，仿佛世界只剩下彼此。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "与 {name} 共度夜晚的甜蜜回忆，像酒一般醇厚，令人沉醉。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦境中你和 {name} 在被窝里互诉衷肠，心动不已，无法自拔。"}
        ]
        special_pool = [
            {"text": "你梦见自己化身风暴中心，所有事物都在你的掌控中。"},
            {"text": "你步入迷宫尽头，看见一扇通往未知的门。"},
            {"text": "梦醒后，你对未来有了全新的领悟。"},
        ]
        nothing_pool = [
            {"text": "今夜无波无澜，一觉安睡至天明。"},
            {"text": "只是平凡地做了个白日梦，然后醒来。"},
        ]

        # 同梦事件池（文本中需要插入 {user}）
        shared_pool = [
            {"type": "gain", "coins": random.randint(8, 50), "text": "你和 {user} 联手抢劫梦境银行，满载而归！"},
            {"type": "lose", "coins": random.randint(5, 15), "text": "你信任了 {user}，却被引入陷阱，损失惨重…"},
            {"type": "buff", "buff_key": "shared_insight", "text": "你和 {user} 心灵共鸣，梦醒后更具洞察力。"},
            {"type": "nothing", "text": "你与 {user} 在星空下沉眠，梦境宁静祥和。"},
            {"type": "betray", "text": "你梦到 {user} 在背后出卖了你，心中百感交集。"},
            {"type": "romance", "buff_key": "shared_love", "text": "你和 {user} 在梦中共舞，情意绵绵。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{user} 送给你一束美丽的鲜花，你们共享一个甜蜜的时刻。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "在梦中，你和 {user} 一起走在月光下，谈天说地，时光如流水般流逝。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {user} 一起翩翩起舞，心灵相通，世界变得柔和而美好。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {user} 在星空下共度良宵，仿佛整个宇宙都在为你们祝福。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦中，你和 {user} 一起度过一个浪漫的夜晚，心情愉悦，忘却一切烦恼。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{user} 轻轻拥抱你，温柔的气息让你心跳加速，难以忘怀。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {user} 在梦中共度激情时刻，彼此间的火花点燃了整个夜晚。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦里，{user} 低声在你耳畔呢喃，带着撩人的气息和深情的眷恋。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你和 {user} 一起沉浸在温暖的拥抱中，感受彼此的体温与心跳交融。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{user} 轻抚你的脸颊，眼神深邃而炽热，让你无法抗拒这份诱惑。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦中你们共浴在月光下，水波荡漾，心与心的距离无限接近。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "{user} 轻吻你的唇，细腻温柔，让人沉醉其中，忘却现实烦忧。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "你们在梦里缠绵，爱意绵绵不绝，仿佛世界只剩下彼此。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "与 {user} 共度夜晚的甜蜜回忆，像酒一般醇厚，令人沉醉。"},
            {"type": "romance", "buff_key": "romance_buff",
             "text": "梦境中你和 {user} 在被窝里互诉衷肠，心动不已，无法自拔。"}
        ]

        # 选择事件
        if with_user:
            event = random.choice(shared_pool).copy()
            # 格式化字符串，替换 {user} 占位符
            event["text"] = event["text"].format(user=with_user)
        else:
            key = input_text.lower() if input_text else ""
            if "财" in key or "运" in key:
                template = random.choice(gain_pool)
                event = {"type": "gain", "coins": template["coins"], "text": template["text"]}
            elif "危" in key or "负" in key or "丢" in key:
                template = random.choice(lose_pool)
                event = {"type": "lose", "coins": template["coins"], "text": template["text"]}
            elif "爱" in key or "浪漫" in key:
                template = random.choice(romance_pool)
                event = {"type": "romance", "buff_key": template["buff_key"], "text": template["text"]}
                # 格式化字符串，替换 {name} 占位符
                event["text"] = event["text"].format(name=with_user if with_user else "梦中人")
            elif "奇" in key or "特" in key:
                template = random.choice(special_pool)
                event = {"type": "special", "text": template["text"]}
            elif not input_text:
                pool = gain_pool + lose_pool + romance_pool + special_pool + nothing_pool
                tpl = random.choice(pool)
                if "coins" in tpl:
                    event = {"type": "gain" if tpl in gain_pool else "lose",
                             "coins": tpl["coins"], "text": tpl["text"]}
                elif tpl in romance_pool:
                    event = {"type": "romance", "buff_key": tpl["buff_key"], "text": tpl["text"]}
                    event["text"] = event["text"].format(name=with_user if with_user else "梦中人")
                else:
                    event = {"type": "special" if tpl in special_pool else "nothing", "text": tpl["text"]}
            else:
                template = random.choice(nothing_pool)
                event = {"type": "nothing", "text": template["text"]}

        # 处理结果
        if event["type"] == "gain":
            self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + event["coins"]
            msg += f"{event['text']}（+{event['coins']} 绿洲币）"
        elif event["type"] == "lose":
            self.user_data["oasis_coins"] = max(0, self.user_data.get("oasis_coins", 0) - event["coins"])
            msg += f"{event['text']}（-{event['coins']} 绿洲币）"
        elif event["type"] in ("buff", "romance", "shared_love", "shared_insight"):
            self.user_data["buffs"][event["buff_key"]] = True
            msg += event["text"]
        else:
            msg += event["text"]

        return msg

        # 处理唤醒命令

    def _wake(self, args=None):
        """
        - 如果没有参数，尝试把自己从“深度睡眠”中唤醒。
        - 如果带 @玩家 参数，尝试把该玩家从“催眠状态”中唤醒。
        """
        # 带参数时，尝试唤醒别人
        if args:
            target_id = parse_mirai_at(args[1])
            if target_id not in self.global_data["users"]:
                return "❌ 找不到要唤醒的目标玩家。"

            target_data = self.find_user(target_id)
            if target_data.get("is_hypnotized", False):
                return f"⚠️ 玩家 {target_data.get('nickname', '未知')}（{target_id}）并未处于催眠状态。"

            # 清除催眠标记
            self.global_data["users"][target_data["user_id"]]["is_hypnotized"] = False
            return f"🌟 {target_data.get('nickname', '未知')}已被唤醒，恢复正常状态。"

        # 不带参数时，尝试自己从深度睡眠中苏醒
        if not self.user_data.get("is_sleeping"):
            return "😐 你现在并未处于深度睡眠状态。"

        self.user_data["is_sleeping"] = False
        return "🌅 你醒来了，精神焕发地回到了绿洲世界！"

    def deepsleep(self):
        if self.user_data.get("is_jailed"):
            return "🚫 你在监狱中，无法进入深度睡眠。"

        if self.user_data.get("is_sleeping"):
            return "😴 你已经在深度睡眠中了，无法重复进入。"

        self.user_data["is_sleeping"] = True
        return "🌙 你进入了深度睡眠状态，身体逐渐放松，意识慢慢飘远...\n🛌 输入 /wake 才能醒来。"

    @staticmethod
    def get_sleep_help():
        return (
            "😴 【睡觉指令帮助】\n"
            "🛏️ 输入 /sleep [内容]，触发不同梦境事件。\n"
            "🧑‍🤝‍🧑 输入 /sleep [内容] @用户名，可与指定玩家同床共梦，梦境随机且可能正面或负面。\n"
            "🌙 输入 /deepsleep 进入深度睡眠状态，无法进行其他操作，需使用 /wake 才能醒来。\n"
            "🌸 支持关键词示例：\n"
            "   - 爱情 / 浪漫：梦见真爱，获得情感增益。\n"
            "   - 财运：梦中发财，增加绿洲币。\n"
            "   - 危险 / 负面：遭遇坏运，可能失去绿洲币。\n"
            "   - 奇异 / 特殊：体验奇幻或神秘的梦境。\n"
            "📘 示例：\n"
            "   /sleep 爱情\n"
            "   /sleep 财运 @alice\n"
            "   /sleep 危险\n"
            "💤 示例（深度睡眠）：\n"
            "   /deepsleep   → 进入深度睡眠\n"
            "   /wake        → 醒来并恢复操作"
        )

    def get_info(self):
        sleeping = "🛌 深度睡眠中" if self.user_data.get("is_sleeping") else "☀️ 清醒状态"
        jailed = "🚔 被监禁" if self.user_data.get("is_jailed") else "✅ 自由活动"
        return f"📋 当前状态：\n - 睡眠状态：{sleeping}\n - 自由状态：{jailed}"

    def change_coin(self, amount: int, reason: str = ""):
        """增加或减少绿洲币，带动画和彩蛋"""
        self.user_data["coin"] = self.user_data.get("coin", 0) + amount
        symbol = "🟢" if amount >= 0 else "🔴"
        animation = "💸" if abs(amount) >= 100 else "🪙"

        # 彩蛋触发
        easter_egg = ""
        if amount >= 888:
            easter_egg = "🎉 你触发了神秘的 888 彩蛋，幸运之神保佑你一整天！"
        elif amount <= -666:
            easter_egg = "💀 你遭遇了传说中的 -666 厄运……好运离你远去。"

        return f"{animation} {symbol} {'增加' if amount >= 0 else '减少'}了 {abs(amount)} 绿洲币。\n{reason}\n{easter_egg}".strip()

    # 催眠模块
    def handle_hypnosis(self, target_id):
        """处理催眠命令：催眠成功后，对方将无法进行下一步操作，直到被唤醒。"""
        if "HYPNO" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        if not target_id:
            return "❌ 请指定要催眠的对象，例如：催眠 @玩家名"

        # 解析 @玩家
        target_user_id = parse_mirai_at(target_id)
        target = self.find_user(target_user_id)
        if self.is_equipped(target_user_id, "防催眠项链"):
            result = [
                "💎 防催眠项链发出清脆的声响，你的催眠波动被抵消，毫无效果！",
                "🛡️ 对方的项链形成一道精神屏障，你的催眠能量如泥牛入海，毫无反应！",
                "🔮 项链上的符文微微发亮，你的催眠咒语被瞬间破解，无法生效！",
                "🌀 催眠能量刚刚靠近，就被项链吸收殆尽，对方依然清醒无比！",
            ]
            return random.choice(result)  # 随机选择一条返回
        if not target:
            return "❌ 找不到要催眠的目标玩家。"

        # 40% 概率催眠成功
        description = random.choice(self.hypnosis_descriptions).format(target=target['nickname'])
        if random.random() < 0.4:
            # 标记目标为“催眠中”
            self.global_data["users"][target["user_id"]]["is_hypnotized"] = True
            return (
                f"{description}\n"
                f"✨ 催眠成功！{target['nickname']}现在处于催眠状态，将无法进行任何操作。"
            )
        else:
            return (
                f"{description}\n"
                f"⚠️ 催眠失败！{target['nickname']}摇摇头，似乎抵抗住了你的催眠。"
            )
    # 敲模块
    def handle_knock(self, target):
        """处理敲击命令"""
        if "KNOCK" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        if not target:
            return "❌ 请指定敲击目标，例如：敲 铁门"

        # 随机选择动作和结果
        action = random.choice(self.knock_data["actions"])
        if random.random() < 0.5:  # 50%成功率
            result = random.choice(self.knock_data["success"])
            status = "✨ 似乎激发了某种深层次的反应……"
        else:
            result = random.choice(self.knock_data["failure"])
            status = "💥 似乎没有什么作用，反倒触发了警告……"

        return (
            f"🔨 {action} {target}\n"
            f"⚡ {result}\n"
            f"{status}"
        )

    # 自杀模块
    def commit_suicide(self):
        if "SUICIDE" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        # 自杀失败判定
        if random.random() < 0.2:
            return "🧠 你犹豫了……最终没有跳下去。\n💡 珍惜生命，也许还有别的路。"

        lost_coins = self.user_data.get("oasis_coins", 0)
        self.user_data["oasis_coins"] = 0

        # 自杀地点与描述池
        suicide_scenes = [
            ("赛博都市钟楼顶", "你站在霓虹残影中的钟楼边缘，风声呼啸，光影在你脸上闪烁"),
            ("恐龙岛火山口", "你爬上灼热的火山口，脚下是咕嘟咕嘟冒泡的岩浆"),
            ("末日废墟核爆中心", "你伫立在辐射荒原中央，残破警报灯一闪一闪"),
            ("星际飞艇舱门外", "你按下了紧急释放阀，舱门在真空中缓缓打开"),
            ("深海基地泄压舱", "你拉下了泄压阀门，海水如野兽般扑面而来"),
            ("天空巨树最顶端", "你站在树冠之巅，俯瞰整座绿洲，闭上了眼"),
            ("虚拟幻境断层边缘", "你触碰到了边缘的代码裂缝，身影逐渐碎裂消散"),
            ("AI 裁判塔楼", "你在审判者的目光中自行宣判，纵身跃下")
        ]

        location, scene_desc = random.choice(suicide_scenes)

        # 死亡记录写入
        death_record = {
            "time": datetime.now(tz).isoformat(),
            "lost_coins": lost_coins,
            "location": location
        }

        self.user_data.setdefault("death_stats", {
            "total_suicides": 0,
            "total_lost": 0,
            "history": []
        })
        self.user_data["death_stats"]["total_suicides"] += 1
        self.user_data["death_stats"]["total_lost"] += lost_coins
        self.user_data["death_stats"]["history"].append(death_record)

        # 设置住院状态
        self.user_data["oasis_coins"] = 100
        self.user_data.setdefault("status", {})
        self.user_data["status"]["in_hospital"] = {
            "start_time": datetime.now(tz).isoformat(),
            "duration_hours": 1
        }

        msg = [
            f"💀 {scene_desc}",
            f"🪂 你从【{location}】纵身跃下……",
            f"💸 财产清零 | 损失 {lost_coins} 绿洲币",
            "🕰️ 你将在医院治疗 1 小时后苏醒",
            "🏥 医疗记录：已开始基因修复重组",
            "💰 初始补助到账：100 绿洲币",
            "⚠️ 当前处于住院状态，无法进行其他操作"
        ]

        self.update_leaderboard()
        return "\n".join(msg)

    # 检测是否在医院
    def is_hospitalized(self):
        if self.is_admin(self.user_id):
            return False
        status = self.user_data.get("status", {}).get("in_hospital")
        if not status:
            return False
        start = datetime.fromisoformat(status["start_time"])
        duration = timedelta(hours=status.get("duration_hours", 1))
        now = datetime.now(tz)
        if now >= start + duration:
            self.user_data["status"]["in_hospital"] = None
            return False
        return True

    def rescue_from_hospital(self, target_user_id):
        # 获取救人者职业
        job = self.user_data.get("career", "")
        is_doctor = (job == "医生")

        # 随机没钱时的描述
        no_money_texts = [
            "💸 你的绿洲币不够，钱包空空如也，无法救人。",
            "😓 钱包瘪了，救人计划失败了。",
            "🚫 绿洲币不足10000，救援任务无法启动。",
            "🪙 没有足够的绿洲币，救人只能等下次了。",
            "❌ 你的绿洲币不够，没法帮忙救出玩家。"
        ]

        # 如果不是医生且钱不够，无法救人
        if not is_doctor and self.user_data.get("oasis_coins", 0) < 10000:
            return random.choice(no_money_texts)

        # 解析目标玩家 ID 并获取数据
        target_user_id = parse_mirai_at(target_user_id)
        target_data = self.global_data["users"].get(target_user_id)
        if not target_data:
            return "❌ 找不到目标玩家。"

        target_name = target_data.get("nickname", target_user_id)

        # 检查目标是否真在医院
        status = target_data.get("status", {}).get("in_hospital")
        if not status:
            return f"❌ 玩家 {target_name} 并不在医院中。"

        # 如果不是医生，扣除绿洲币
        if not is_doctor:
            self.user_data["oasis_coins"] -= 10000

        # 解除目标玩家医院状态
        target_data["status"]["in_hospital"] = None

        # 描述文本
        if is_doctor:
            doctor_texts = [
                f"🩺 你作为医生施展精湛医术，成功免费治疗了玩家 {target_name}！",
                f"🌡️ 医者仁心，玩家 {target_name} 已康复出院，未收取任何费用！",
                f"👨‍⚕️ 你动用了职业技能，让 {target_name} 奇迹般地恢复健康！"
            ]
            return random.choice(doctor_texts)
        else:
            rescue_texts = [
                f"🏥 你花费10000绿洲币，亲自前往医院，把玩家 {target_name} 带出了病房！",
                f"✨ 神秘的绿洲币力量发挥作用，玩家 {target_name} 获得奇迹般的康复和自由！",
                f"⛑️ 你紧急支付救护费，成功将玩家 {target_name} 从医院释放出来，重获自由！",
                f"💸 你不惜重金，解救了玩家 {target_name}，医院门口欢呼声一片！",
                f"🚑 绿洲币换来了生命的希望，玩家 {target_name} 已经脱离医院的束缚！"
            ]
            return random.choice(rescue_texts)

    # 死亡模块
    def handle_death(self):
        self.user_data["oasis_coins"] = 0
        self.user_data["inventory"] = []
        self.user_data["wing_suit_stats"]["is_alive"] = False

    # ————————————————————————rob bank银行豪杰————————————————————
    def handle_rob_bank(self, cmd_parts):
        if len(cmd_parts) < 2:
            return "❌ 指令错误，用法: rob bank / rob bank @队长ID / rob bank start / rob bank quit"

        subcmd = cmd_parts[1].lower()
        if subcmd != "bank":
            return "❌ 未知子命令，用法: rob bank / rob bank @队长ID / rob bank start / rob bank quit"

        if len(cmd_parts) == 2:
            return self.create_team()

        if len(cmd_parts) == 3:
            if cmd_parts[2].lower() == "start":
                return self.start_heist()
            elif cmd_parts[2].lower() == "quit":
                return self.quit_team()
            return self.join_team(cmd_parts[2])

        return "❓ 用法: rob bank / rob bank @队长ID / rob bank start / rob bank quit"

    def create_team(self):
        heists = self.global_data.setdefault("bank_heist_rooms", {})

        if len(heists) >= 3:
            return "🚫 当前已存在 3 个等待中的抢劫队伍，请稍后再试"

        # 分配一个唯一房间ID（1~3）
        for room_id in ['room1', 'room2', 'room3']:
            if room_id not in heists:
                heists[room_id] = {
                    "room_id": room_id,
                    "leader_id": self.user_id,
                    "members": [self.user_id],
                    "status": "waiting",
                    "start_time": datetime.now(tz).isoformat()
                }
                return f"🎭 你已创建银行抢劫队伍（房间：{room_id}）！\n还需 3 人加入，可输入：#run oas rob bank {self.user_id} "
        return "❌ 创建队伍失败"

    def join_team(self, raw_target):
        from_id = self.user_id
        target_id = parse_mirai_at(raw_target)
        heists = self.global_data.get("bank_heist_rooms", {})

        for room_id, heist in heists.items():
            if heist["leader_id"] == target_id and heist["status"] == "waiting":
                if from_id in heist["members"]:
                    return "🔁 你已在该队伍中"
                if len(heist["members"]) >= 4:
                    return "🚫 队伍已满"

                heist["members"].append(from_id)
                return f"✅ 加入成功（房间：{room_id}）当前队伍人数：{len(heist['members'])}/4"

        return "❌ 无法加入，该队伍不存在或已开始抢劫"

    def start_heist(self):
        heists = self.global_data.get("bank_heist_rooms", {})
        for room_id, heist in list(heists.items()):
            if heist["leader_id"] == self.user_id and heist["status"] == "waiting":
                if len(heist["members"]) < 4:
                    return f"⚠️ 队伍人数不足：{len(heist['members'])}/4"
                return self.resolve_heist(room_id, heist)
        return "⛔ 只有队长可以发起抢劫，或队伍状态异常"

    def resolve_heist(self, room_id, heist):
        members = heist["members"]
        now = datetime.now(tz)
        loot = random.randint(10_000, 100_000)
        success = random.random() < 0.25

        log = []
        # 开场经典对白
        log.append(f"💰 【底库现金】今晚这桶金有 {loot} 绿洲币，兄弟们，准备上！")
        log.append("🕶️ 老大冷冷说道：‘这次咱们得干净利落，别给他们留活口。’")
        log.append("🔫 面具戴好，枪膛上膛，走位走位，冲锋号响起！")

        # 各成员冲锋描写，随机酷炫表情加持
        for uid in members:
            nickname = self.global_data["users"].get(uid, {}).get("nickname", f"用户{uid}")
            emoji = random.choice(["🕶️", "🔫", "💣", "🧨", "😎", "🥷"])
            log.append(f"{emoji} {nickname} 一脚踹开大门，带着火药味冲进去！")

        # 中间过程：麻烦人质 + 烦人警察剧情分支
        if random.random() < 0.4:
            hostage = random.choice(members)
            log.append(f"😤 【麻烦人质】哎呦，{self.global_data['users'][hostage]['nickname']} 抓着人质不放，场面一度胶着！")
            log.append("👮 【烦人警察】警察局长通过扩音器喊话：‘放下武器，乖乖投降，不然我们一锅端了！’")
            log.append("💥 老大怒吼：‘谁TM给他们加戏，给我拿下这帮搅局的狗东西！’")

            if random.random() < 0.5:
                log.append("🔥 经过一阵激烈对峙，终于制服了人质，快点，时间不多！")
            else:
                log.append("💣 现场乱成一锅粥，人质失控，计划险些全盘皆输……")

        # 额外彩蛋：戏精人质触发
        if random.random() < 0.15:
            actor = random.choice(members)
            log.append(
                f"🎭 【戏精人质】突然，{self.global_data['users'][actor]['nickname']}开始用电影台词软磨硬泡，警察差点被带跑偏！")
            if random.random() < 0.5:
                log.append("👮 警察局长居然开始跟他“谈判”，这TM成了相声现场！")
            else:
                log.append("🔥 但老大不干了，‘别磨叽，干了他们！’枪声又响起！")

        # 额外彩蛋：黑警察 or 铁面无情警察
        if random.random() < 0.25:
            corrupt_cop = random.choice(members)
            log.append(
                f"🕶️ 【黑警察】{self.global_data['users'][corrupt_cop]['nickname']}在暗处摸黑，偷偷塞现金袋，老大心里默默点头：‘可靠的小子。’")
        elif random.random() < 0.25:
            strict_cop = random.choice(members)
            log.append(f"👮 【铁面无情】警察头头咆哮：‘放下武器！不然你们见识见识警察的怒火！’")

        if success:
            bonus = int(loot * 0.1)  # 队长分红 10%
            remaining = loot - bonus
            share = remaining // len(members)

            for uid in members:
                self.global_data["users"][uid]["oasis_coins"] += share
                log.append(f"💸 {self.global_data['users'][uid]['nickname']} 藏好钱袋，分得 {share} 绿洲币")

            self.global_data["users"][heist["leader_id"]]["oasis_coins"] += bonus
            log.append(f"👑 老大额外拿走了 {bonus} 绿洲币，毕竟头儿的光环不是白来的")

            log.append("🎉 【行动成功】这次干得漂亮，别忘了今晚大喝一场！🥃🍾")
            self.global_data.setdefault("news_feed", []).append({
                "time": now.isoformat(),
                "content": f"🎉 【黑帮新闻】银行抢劫成功！队伍成员：{', '.join(self.global_data['users'][uid]['nickname'] for uid in members)}，共抢得 {loot} 绿洲币"
            })

        else:
            log.append("🚨 【警报拉响】卧底来了，局势急转直下……")

            failure_type = random.choices(
                ["all_caught", "one_caught", "partial_caught", "all_escape"],
                weights=[0.3, 0.2, 0.45, 0.05], k=1
            )[0]

            caught = []
            escaped = []

            if failure_type == "all_caught":
                log.append("🚔 警察像猎犬一样包围了我们，兄弟们一个不漏地全被铐上了手铐！")
                caught = members
            elif failure_type == "one_caught":
                caught = [random.choice(members)]
                escaped = [uid for uid in members if uid not in caught]
                log.append(f"😱 有个兄弟动作慢半拍，{self.global_data['users'][caught[0]]['nickname']}栽在了警察手里！")
            elif failure_type == "partial_caught":
                caught = random.sample(members, k=random.randint(1, len(members) - 1))
                escaped = [uid for uid in members if uid not in caught]
                log.append("💥 混战中分崩离析，有的逃了，有的被抓！")
            elif failure_type == "all_escape":
                escaped = members
                log.append("🔥 就差一点点就被包围，结果咱们狡猾得很，成功甩掉了追兵！")

            escape_texts = [
                "🛵 兄弟骑着哈雷摩托呼啸而去",
                "🚕 跳上出租车，消失在城市烟雾中",
                "🏃‍♂️ 狂奔穿过街头巷尾，根本不给他们抓住机会",
                "🧥 扔下风衣伪装，变成了人群里一条普通的鱼",
                "🚁 直升机来了，咱们的救援可不是闹着玩的"
            ]

            for uid in caught:
                now = datetime.now(tz)
                if not self.global_data["users"].get(uid):
                    continue
                self.global_data["users"][uid].setdefault("status", {})["is_jailed"] = {
                    "start_time": now.isoformat(),
                    "duration_hours": 2,
                    "reason": "银行抢劫失败"
                }
                jail_hours = 2
                release_time = (datetime.now(tz) + timedelta(hours=jail_hours)).isoformat()
                self.global_data["users"][uid]["prison"] = {
                    "is_jailed": True,
                    "release_time": release_time,
                    "reason": "抢劫失败被捕"
                }
                nickname = self.global_data["users"][uid]["nickname"]
                emoji = random.choice(["🚔", "👮", "🔒", "🚓"])
                log.append(f"{emoji} {nickname} 被捕，铁窗后面等着你，兄弟……")

            for uid in escaped:
                nickname = self.global_data["users"][uid]["nickname"]
                style = random.choice(escape_texts)
                log.append(f"🕶️ {nickname} 成功逃脱，{style}")

            # 分红给逃脱者
            if escaped:
                escape_share = loot // len(escaped)
                for uid in escaped:
                    self.global_data["users"][uid]["oasis_coins"] += escape_share
                    log.append(f"💸 {self.global_data['users'][uid]['nickname']} 偷渡成功，分得 {escape_share} 绿洲币")


            self.global_data.setdefault("news_feed", []).append({
                "time": now.isoformat(),
                "content": f"🚨 【黑帮新闻】银行抢劫失败！逃脱者：{', '.join(self.global_data['users'][uid]['nickname'] for uid in escaped) or '无'}；被捕：{', '.join(self.global_data['users'][uid]['nickname'] for uid in caught)}"
            })

        # 删除房间，结束这次抢劫
        self.global_data["bank_heist_rooms"].pop(room_id, None)

        return "\n".join(log)


    def quit_team(self):
        heists = self.global_data.get("bank_heist_rooms", {})
        for room_id, heist in list(heists.items()):
            if self.user_id in heist["members"] and heist["status"] == "waiting":
                if self.user_id == heist["leader_id"]:
                    self.global_data["bank_heist_rooms"].pop(room_id)
                    return f"🛑 你是队长，已解散房间 {room_id} 的银行抢劫队伍"
                else:
                    heist["members"].remove(self.user_id)
                    return f"🚪 你已退出抢劫队伍（房间：{room_id}，剩余成员：{len(heist['members'])}/4）"
        return "❌ 当前没有等待中的抢劫队伍可退出"

    #——————————————————兔子城豪杰————————————————————

    def handle_rob_rabbit_city(self, cmd_parts):
        if len(cmd_parts) < 2:
            return "❌ 指令错误，用法: rob 兔子城 / rob 兔子城 @队长ID / rob 兔子城 start / rob 兔子城 quit"

        subcmd = cmd_parts[1].lower()
        if subcmd not in ["rabbit", "兔子城"]:
            return "❌ 未知子命令，用法: rob 兔子城 / rob 兔子城 @队长ID / rob 兔子城 start / rob 兔子城 quit"

        if len(cmd_parts) == 2:
            return self.create_rabbit_team()

        if len(cmd_parts) == 3:
            if cmd_parts[2].lower() in ["start", "开始"]:
                return self.start_rabbit_heist()
            elif cmd_parts[2].lower() in ["quit", "退出"]:
                return self.quit_rabbit_team()
            return self.join_rabbit_team(cmd_parts[2])

        return "❓ 用法: rob 兔子城 / rob 兔子城 @队长ID / rob 兔子城 start / rob 兔子城 quit"

    def is_farmer(self, user_id=None):
        """检查玩家是否为农夫"""
        uid = user_id if user_id else self.user_id
        return self.global_data["users"].get(uid, {}).get("career", "") == "农夫"

    def is_hunter(self, user_id=None):
        """检查玩家是否为猎人"""
        uid = user_id if user_id else self.user_id
        return self.global_data["users"].get(uid, {}).get("career", "") == "猎人"

    def create_rabbit_team(self):
        heists = self.global_data.setdefault("rabbit_heist_rooms", {})

        if len(heists) >= 3:
            return "🚫 当前已存在 3 个等待中的兔子城豪劫队伍，请稍后再试"

        # 检查队长职业
        if not self.is_farmer():
            return "🚫 只有农夫可以创建兔子城豪劫队伍（需要伪装身份）"

        # 分配一个唯一房间ID
        for room_id in ['carrot', 'cabbage', 'radish']:
            if room_id not in heists:
                heists[room_id] = {
                    "room_id": room_id,
                    "leader_id": self.user_id,
                    "members": [self.user_id],
                    "status": "waiting",
                    "start_time": datetime.now(tz).isoformat()
                }
                return f"🐰 你已创建兔子城豪劫队伍（房间：{room_id}）！\n还需 2 人加入，可输入：#run oas rob rabbit {self.user_id} \n⚠️ 队伍中不能有猎人"
        return "❌ 创建队伍失败"

    def join_rabbit_team(self, raw_target):
        from_id = self.user_id
        target_id = parse_mirai_at(raw_target)
        heists = self.global_data.get("rabbit_heist_rooms", {})

        # 检查加入者是否为猎人
        if self.is_hunter(from_id):
            return "🚫 猎人不能加入兔子城豪劫队伍（兔子讨厌猎人）"

        for room_id, heist in heists.items():
            if heist["leader_id"] == target_id and heist["status"] == "waiting":
                if from_id in heist["members"]:
                    return "🔁 你已在该队伍中"
                if len(heist["members"]) >= 3:
                    return "🚫 队伍已满（最多3人）"

                # 检查队长是否仍是农夫
                if not self.is_farmer(heist["leader_id"]):
                    return "🚫 队长已不是农夫，队伍无效"

                heist["members"].append(from_id)
                return f"✅ 加入兔子城豪劫队伍成功（房间：{room_id}）当前队伍人数：{len(heist['members'])}/3"

        return "❌ 无法加入，该队伍不存在或已开始行动"

    def start_rabbit_heist(self):
        heists = self.global_data.get("rabbit_heist_rooms", {})
        for room_id, heist in list(heists.items()):
            if heist["leader_id"] == self.user_id and heist["status"] == "waiting":
                # 检查队长是否仍是农夫
                if not self.is_farmer():
                    return "🚫 只有农夫可以发起兔子城豪劫"

                # 检查队伍中是否有猎人
                if any(self.is_hunter(uid) for uid in heist["members"]):
                    return "🚫 队伍中有猎人，兔子会察觉危险！"

                if len(heist["members"]) < 2:
                    return f"⚠️ 队伍人数不足：{len(heist['members'])}/3"
                return self.resolve_rabbit_heist(room_id, heist)
        return "⛔ 只有队长可以发起豪劫，或队伍状态异常"

    def resolve_rabbit_heist(self, room_id, heist):
        members = heist["members"]
        now = datetime.now(tz)

        # 完整的物品定义（包含名称和描述）
        item_definitions = {
            # 种子类
            "胡萝卜种子": {"name": "胡萝卜种子", "desc": "能种出甜美胡萝卜的种子"},
            "卷心菜种子": {"name": "卷心菜种子", "desc": "卷心菜种植必备"},
            "萝卜种子": {"name": "萝卜种子", "desc": "普通萝卜的种子"},
            "草莓种子": {"name": "草莓种子", "desc": "红色诱人的草莓种子"},
            "南瓜种子": {"name": "南瓜种子", "desc": "万圣节必备"},
            # 稀有物品
            "兔子戒指": {"name": "兔子戒指", "desc": "兔子公主的珍贵戒指，据说能听懂兔子语言"},
            "金萝卜": {"name": "金萝卜", "desc": "传说中的金萝卜，兔子城的至宝"}
        }

        # 随机选择3种种子作为战利品
        seed_types = ["胡萝卜种子", "卷心菜种子", "萝卜种子", "草莓种子", "南瓜种子", "金萝卜"]
        selected_seeds = random.sample(seed_types, 3)
        loot = {
            "seeds": {seed: random.randint(1, 3) for seed in selected_seeds},
            "rabbit_ring": random.random() < 0.01,  # 15%几率获得兔子戒指
            "gold_carrot": random.random() < 0.1  # 10%几率获得金萝卜
        }

        # 根据队伍人数调整成功率
        base_success_rate = 0.15
        success_rate = base_success_rate + (len(members) - 1) * 0.05
        success = random.random() < success_rate
        uid = 0
        log = []
        # 开场剧情 - 随机选择不同潜入方式
        entry_style = random.choice([
            "推着装满稻草的推车接近城门",
            "伪装成园艺师混入送货队伍",
            "趁着夜色翻越城墙",
            "贿赂守门兔子获得临时通行证"
        ])
        log.append(f"🐰 【兔子城大门】你们{entry_style}...")

        # 随机守卫反应
        guard_reaction = random.choice([
            "卫兵兔子嗅了嗅鼻子：‘嗯？今天的胡萝卜味道有点怪？’",
            "卫兵兔子扶了扶眼镜：‘等等，你们的通行证颜色不对啊？’",
            "卫兵兔子突然举起长矛：‘站住！最近有小偷出没！’",
            "卫兵兔子打着哈欠：‘快点快点，别耽误我换岗’"
        ])
        log.append(f"🛒 {guard_reaction}")

        leader_nickname = self.global_data['users'][heist['leader_id']]['nickname']
        reply_style = random.choice([
            f"👨‍🌾 {leader_nickname} 憨厚一笑：‘新品种，新品种！’",
            f"🤫 {leader_nickname} 偷偷塞给卫兵一袋金币",
            f"😅 {leader_nickname} 假装摔倒制造混乱",
            f"🎭 {leader_nickname} 突然开始表演兔子舞转移注意力"
        ])
        log.append(reply_style)

        # 随机混入结果
        mix_in_success = random.random() < 0.5  # 50%几率能混进去
        if success or mix_in_success:
            # 随机成功混入的方式
            success_entry = random.choice([
                "卫兵兔子挥挥手：‘进去吧，别在门口挡道！’",
                "趁着卫兵换岗的空隙溜了进去",
                "伪装成皇家供应商成功蒙混过关",
                "用胡萝卜香水掩盖了人类气味"
            ])
            log.append(f"✅ {success_entry}")
            log.append("🌿 你们成功混入了兔子城，开始寻找种子仓库...")

            # 随机仓库事件
            warehouse_events = [
                ("撬开了上锁的储藏室", "发现门锁已经生锈，轻轻一撬就开了"),
                ("打晕了看守的兔子", "一记手刀放倒了打瞌睡的守卫"),
                ("用胡萝卜引开了守卫", "扔出会发光的金胡萝卜引开了所有守卫"),
                ("发现了一个没锁的仓库", "运气爆棚找到没上锁的皇家种子库"),
                ("破解了电子锁", "没想到兔子城也用电子锁，正好带着解码器"),
                ("挖地道进入", "提前准备好的迷你钻地机派上用场")
            ]
            event_desc, event_detail = random.choice(warehouse_events)
            log.append(f"🔍 【仓库奇遇】{event_desc}")
            log.append(f"💡 {event_detail}")

            # 千钧一发事件 - 50%几率触发
            if random.random() < 0.5:
                close_call = random.choice([
                    f"🚨 突然警报响起！{random.choice(members)} 迅速切断了电源",
                    "🐰 兔子公主的卫队经过！你们屏住呼吸躲在货架后",
                    "💥 有兔子发现异常！你们假装在例行检查蒙混过去",
                    "🔊 一个种子袋掉落发出巨响！你们立刻学兔子叫蒙混过关"
                ])
                log.append(close_call)

            log.append("🏆 找到了以下珍贵种子：")

            # 分配种子给所有成员
            for seed, total_amount in loot["seeds"].items():
                seed_info = item_definitions[seed]
                per_member = max(1, total_amount // len(members))
                remainder = total_amount % len(members)

                for i, uid in enumerate(members):
                    give_amount = per_member + (1 if i < remainder else 0)
                    if give_amount > 0:
                        self.add_simple_item(
                            item_id=seed,
                            quantity=give_amount,
                            description=seed_info["desc"]
                        )
                        log.append(
                            f"🌱 {self.global_data['users'][uid]['nickname']} 获得了 {seed_info['name']} x{give_amount}")
            uid = self.global_data['users'][uid]
            # 稀有物品获取
            if loot["rabbit_ring"]:
                lucky_member = random.choice(members)
                self.give_item_to_user(
                    user_id=uid,
                    item_id="兔子戒指",
                    quantity=1,
                    description=item_definitions["兔子戒指"]["desc"]
                )
                log.append(f"💍 {self.global_data['users'][lucky_member]['nickname']} 在角落发现了兔子公主的戒指！")

            if loot["gold_carrot"]:
                lucky_member = random.choice(
                    [uid for uid in members if uid != lucky_member] if loot["rabbit_ring"] else members)
                self.give_item_to_user(
                    user_id=uid,
                    item_id="金萝卜",
                    quantity=1,
                    description=item_definitions["金萝卜"]["desc"]
                )
                log.append(f"🌟 {self.global_data['users'][lucky_member]['nickname']} 找到了传说中的金萝卜！")

            # 随机撤离方式
            escape_style = random.choice([
                "推着装满种子的推车，大摇大摆地离开",
                "利用下水道系统秘密撤离",
                "乘坐事先准备好的气球飞离",
                "伪装成受伤兔子被送往医院"
            ])
            log.append(f"🏃‍♂️ 【撤离】你们{escape_style}")
            log.append("🎉 行动成功！兔子们还没发现种子被偷了呢~")

            self.global_data.setdefault("news_feed", []).append({
                "time": now.isoformat(),
                "content": f"🎉 【农夫新闻】兔子城豪劫成功！{', '.join(self.global_data['users'][uid]['nickname'] for uid in members)} 盗取了珍贵种子"
            })
        else:
            # 失败剧情
            detection_style = random.choice([
                "卫兵兔子突然瞪大眼睛：‘等等！你们不是农夫！’",
                "一个种子袋突然破裂，露出里面的武器",
                "你们的伪装在过安检时被X光机识破",
                "有兔子认出了你们是通缉犯"
            ])
            log.append(f"🚨 {detection_style}")

            princess_appear = random.choice([
                "兔子公主出现在城墙上：‘抓住这些小偷！’",
                "兔子公主的卫队从四面八方包围过来",
                "兔子公主吹响了警报口哨",
                "兔子公主直接扔出了一个胡萝卜炸弹"
            ])
            log.append(f"👑 {princess_appear}")

            # 逃跑过程
            escape_attempts = []
            for uid in members:
                member_name = self.global_data['users'][uid]['nickname']
                attempt = random.choice([
                    f"{member_name} 试图翻越城墙但被网兜抓住",
                    f"{member_name} 躲进酒桶但还是被嗅觉灵敏的兔子发现",
                    f"{member_name} 假装晕倒但被识破",
                    f"{member_name} 试图贿赂卫兵结果被加倍处罚",
                    f"{member_name} 成功躲过第一波追捕",
                    f"{member_name} 用烟雾弹制造混乱",
                    f"{member_name} 跳进运胡萝卜的车里"
                ])
                escape_attempts.append(attempt)

            log.extend(escape_attempts)

            # 失败处理
            caught = []
            escaped = []

            for uid in members:
                if "被" in escape_attempts[members.index(uid)] or "识破" in escape_attempts[members.index(uid)]:
                    caught.append(uid)
                else:
                    escaped.append(uid)

            # 确保至少一个人被抓或逃脱
            if not caught and escaped:
                caught.append(random.choice(escaped))
                escaped.remove(caught[0])
            elif not escaped and caught:
                escaped.append(random.choice(caught))
                caught.remove(escaped[0])

            if not caught:
                log.append("🏃‍♂️ 你们跑得比兔子还快，全员成功逃脱！简直是奇迹！")
            elif not escaped:
                log.append("😭 全员被捕，兔子城的胡萝卜监狱等着你们...")
            else:
                log.append(f"💨 经过激烈追逐，{len(escaped)}人逃脱，{len(caught)}人不幸被捕")

            # 处理被捕玩家
            for uid in caught:
                self.global_data["users"][uid].setdefault("status", {})["is_jailed"] = {
                    "start_time": now.isoformat(),
                    "duration_hours": 3,
                    "reason": "兔子城豪劫失败"
                }
                nickname = self.global_data["users"][uid]["nickname"]
                prison_style = random.choice([
                    f"🚨 {nickname} 被关进了充满胡萝卜味的监狱",
                    f"🔒 {nickname} 被锁在了一个巨型胡萝卜里",
                    f"🐰 {nickname} 被迫参加兔子城的劳动改造",
                    f"🥕 {nickname} 被罚种胡萝卜直到刑满释放"
                ])
                log.append(prison_style)

            # 逃脱者可能还是拿到一些东西
            if escaped:
                for uid in escaped:
                    if random.random() < 0.5:  # 50%几率拿到少量种子
                        seed = random.choice(list(loot["seeds"].keys()))
                        amount = random.randint(1, 2)
                        seed_info = item_definitions[seed]
                        self.add_simple_item(
                            item_id=seed,
                            quantity=amount,
                            description=seed_info["desc"]
                        )
                        escape_with_loot = random.choice([
                            f"🌱 {self.global_data['users'][uid]['nickname']} 逃跑时顺手抓了一把{seed_info['name']}",
                            f"🛍️ {self.global_data['users'][uid]['nickname']} 的衣服里掉出来{amount}个{seed_info['name']}",
                            f"🎒 {self.global_data['users'][uid]['nickname']} 的背包里意外装着{amount}个{seed_info['name']}"
                        ])
                        log.append(escape_with_loot)

            self.global_data.setdefault("news_feed", []).append({
                "time": now.isoformat(),
                "content": f"🚨 【农夫新闻】兔子城豪劫失败！{', '.join(self.global_data['users'][uid]['nickname'] for uid in caught)} 被兔子卫兵逮捕"
            })

        # 删除房间
        self.global_data["rabbit_heist_rooms"].pop(room_id, None)
        return "\n".join(log)

    def quit_rabbit_team(self):
        heists = self.global_data.get("rabbit_heist_rooms", {})
        for room_id, heist in list(heists.items()):
            if self.user_id in heist["members"] and heist["status"] == "waiting":
                if self.user_id == heist["leader_id"]:
                    self.global_data["rabbit_heist_rooms"].pop(room_id)
                    return f"🛑 你是队长，已解散房间 {room_id} 的兔子城豪劫队伍"
                else:
                    heist["members"].remove(self.user_id)
                    return f"🚪 你已退出兔子城豪劫队伍（房间：{room_id}，剩余成员：{len(heist['members'])}/3）"
        return "❌ 当前没有等待中的兔子城豪劫队伍可退出"

    # ——————————OASIS-监狱营救模块——————————

    def handle_rob_jail(self, cmd_parts):
        """
        处理“rob 监狱”相关子命令：
        用法：
          rob 监狱 创建 @被救玩家ID       → 创建营救队伍
          rob 监狱 加入 @队长ID          → 加入队伍
          rob 监狱 start                 → 队长发起行动
          rob 监狱 quit                  → 退出队伍
        """

        subcmd = cmd_parts[0].lower()
        if subcmd in ["start", "开始"]:
            return self.start_jail_rescue()
        elif subcmd in ["quit", "退出"]:
            return self.quit_jail_team()
        elif subcmd in ["加入", "join"]:
            if len(cmd_parts) != 2 or not cmd_parts[1]:
                return "❌ 用法错误：rob 监狱 加入 @队长ID"
            return self.join_jail_team(cmd_parts[1])
        elif subcmd in ["创建", "create"]:
            if len(cmd_parts) != 2 or not cmd_parts[1]:
                return "❌ 用法错误：rob 监狱 创建 @被救玩家ID"
            return self.create_jail_team(cmd_parts[1])
        else:
            return f"❌ 未知子命令，用法: rob 监狱 创建 @被救玩家ID / rob 监狱 加入 @队长ID / rob 监狱 start / rob 监狱 quit"

    def is_police(self, user_id=None):
        """检查玩家是否为警察职业"""
        uid = user_id if user_id else self.user_id
        return self.global_data["users"].get(uid, {}).get("career", "") == "警察"

    def is_hidden(self, user_id=None):
        """检查玩家是否为隐者职业"""
        uid = user_id if user_id else self.user_id
        return self.global_data["users"].get(uid, {}).get("career", "") == "隐者"

    def is_boxer(self, user_id=None):
        """检查玩家是否为拳击手职业"""
        uid = user_id if user_id else self.user_id
        return self.global_data["users"].get(uid, {}).get("career", "") == "拳击手"

    @staticmethod
    def is_player_in_prison(player_data: dict) -> bool:
        prison_info = player_data.get('prison', {})
        return prison_info.get('is_jailed', False) is True

    def create_jail_team(self, target_raw):
        heists = self.global_data.setdefault("jail_rescue_rooms", {})
        # 检查该用户是否已有创建的队伍
        for r in heists.values():
            if r["leader_id"] == self.user_id and r["status"] == "waiting":
                return "⛔ 你已经创建了一个营救队伍，无法重复创建"

        if len(heists) >= 3:
            return "🚫 当前已存在 3 个等待中的监狱营救队伍，请稍后再试"


        if not target_raw:
            return "❌ 创建队伍需要指定一位被救援的玩家，例如：rob 监狱 @玩家ID"

        target_id = parse_mirai_at(target_raw)
        target_info = self.global_data["users"].get(target_id, {})

        # 检查目标是否在监狱
        if self.is_player_in_prison(target_info):
            return "🚫 指定玩家不在监狱中，无法作为营救对象"

        # 分配一个唯一房间ID
        for room_id in ['A', 'B', 'C']:
            if room_id not in heists:
                heists[room_id] = {
                    "room_id": room_id,
                    "leader_id": self.user_id,
                    "rescue_target": target_id,  # 新增：营救对象
                    "members": [self.user_id],
                    "status": "waiting",
                    "start_time": datetime.now(tz).isoformat()
                }
                target_nickname = target_info.get("nickname", "神秘囚徒")
                return (f"🥷🏿 你已创建监狱营救【营救行动】队伍（房间：{room_id}）\n"
                        f"🎯 本次目标：救出『{target_nickname}』！\n"
                        f"还需 2 人加入，可输入：#run oas rob jail 加入 {self.user_id} \n"
                        f"⚠️ 队伍中不能有警察")

        return "❌ 创建队伍失败"

    def join_jail_team(self, raw_target):
        from_id = self.user_id
        target_id = parse_mirai_at(raw_target)
        rooms = self.global_data.get("jail_rescue_rooms", {})

        # 检查本人是否为警察，不允许加入
        if self.is_police(from_id):
            return "🚫 警察不可加入监狱营救队伍"

        for room_id, room in rooms.items():
            if room["leader_id"] == target_id and room["status"] == "waiting":
                if from_id in room["members"]:
                    return "🔁 你已在该队伍中"
                if len(room["members"]) >= 4:
                    return "🚫 队伍已满（最多4人）"

                room["members"].append(from_id)
                return (
                    f"✅ 加入监狱营救队伍成功（房间：{room_id}）"
                    f"当前队伍人数：{len(room['members'])}/4"
                )
        return "❌ 无法加入，该队伍不存在或已开始行动"


    def start_jail_rescue(self):
        rooms = self.global_data.get("jail_rescue_rooms", {})
        for room_id, room in list(rooms.items()):
            if room["leader_id"] == self.user_id and room["status"] == "waiting":
                # 只有非警察才能发起
                if self.is_police():
                    return "🚫 警察无法发起监狱营救任务"

                member_count = len(room["members"])
                if member_count < 1:
                    return f"⚠️ 队伍人数不足：{member_count}/1"

                return self.resolve_jail_rescue(room_id, room)
        return "⛔ 只有队长可以发起营救，或队伍状态异常"


    def resolve_jail_rescue(self, room_id, room):
        members = room["members"]
        now = datetime.now(tz)

        log = []
        # 开场剧情 - 随机进入监狱外围
        entry_style = random.choice([
            "夜幕下偷偷潜入监狱侧门",
            "假扮清洁工混入监狱后门",
            "从监狱下水道爬进牢房区",
            "伪装成狱警获得短暂通行"
        ])
        log.append(f"🔓 【监狱围墙】你们{entry_style}...")

        # 计算基础成功率：20%，每增加一人 +20%
        base_rate = 0.20
        success_rate = base_rate + (len(members) - 1) * 0.10
        success_rate = min(success_rate, 0.9)  # 最多 90%
        success = random.random() < success_rate

        if success:
            log.append("✅ 你们成功找到了囚犯牢房，开始营救行动...")

            # 随机解除牢门方式
            door_events = [
                ("破解了机械锁", "用随身工具成功打开了牢门"),
                ("制服了狱卒", "一招制服了看守狱卒，悄悄拉开牢门"),
                ("用铁丝撬锁", "铁丝从门缝伸进去，锁芯嘀嗒一声解开"),
                ("借助狱卒的钥匙", "从被打晕的狱卒腰间抢到钥匙")
            ]
            evt, detail = random.choice(door_events)
            log.append(f"🔑 【牢门解除】{evt}")
            log.append(f"💡 {detail}")

            # 成功营救：给每个成员奖励，比如“囚犯感激物资”
            for uid in members:
                self.add_simple_item(
                    item_id="救援物资包",
                    quantity=1,
                    description="从囚犯处得到的求生物资包"
                )
                log.append(
                    f"🎁 {self.global_data['users'][uid]['nickname']} 获得了 救援物资包 x1"
                )

            log.append("🏃‍♂️ 【撤离】你们成功带走了囚犯，一路无声无息地离开监狱…")
            self.global_data.setdefault("news_feed", []).append({
                "time": now.isoformat(),
                "content": (
                    f"🎉 【营救新闻】监狱营救成功！"
                    f"{', '.join(self.global_data['users'][uid]['nickname'] for uid in members)} 雇佣兵"
                )
            })
            # 成功解救目标囚犯
            target_id = room["rescue_target"]
            self.global_data["users"][target_id]["prison"]["is_jailed"] = False
            log.append(f"🕊️ 『{self.global_data['users'][target_id]['nickname']}』成功脱离监狱！")

        else:
            log.append("🚨 营救行动失败，狱卒发现了你们！")
            # 逐个判断结果：受伤或被捕
            caught = []
            injured = []
            for uid in members:
                # 抓捕基准概率 50%，若为隐者则减半
                arrest_chance = 0.50
                if self.is_hidden(uid):
                    arrest_chance *= 0.5

                if random.random() < arrest_chance:
                    # 本该被捕：若是拳击手，则攻击狱卒送对方医院，自己受伤去医院
                    if self.is_boxer(uid):
                        nickname = self.global_data['users'][uid]['nickname']
                        log.append(f"🥊 拳击手{nickname} 怒击狱卒，对方被送入医院，{nickname} 自己重伤去医院")
                        # 设置为住院状态
                        self.global_data["users"][uid].setdefault("status", {})["in_hospital"] = {
                            "start_time": now.isoformat(),
                            "duration_hours": 4,
                            "reason": "监狱营救受伤"
                        }
                        injured.append(uid)
                    else:
                        caught.append(uid)
                else:
                    # 逃脱者：有 30% 几率轻伤
                    if random.random() < 0.30:
                        nickname = self.global_data['users'][uid]['nickname']
                        log.append(f"🤕 {nickname} 在逃亡途中受轻伤，被送到医院治疗")
                        self.global_data["users"][uid].setdefault("status", {})["in_hospital"] = {
                            "start_time": now.isoformat(),
                            "duration_hours": 2,
                            "reason": "监狱营救逃亡受伤"
                        }
                        injured.append(uid)
                    else:
                        log.append(f"🏃‍♂️ {self.global_data['users'][uid]['nickname']} 机智逃脱，暂时脱离危险")

            # 处理被捕的玩家：送监狱
            for uid in caught:
                nickname = self.global_data['users'][uid]['nickname']
                self.global_data["users"][uid].setdefault("status", {})["is_jailed"] = {
                    "start_time": now.isoformat(),
                    "duration_hours": 3,
                    "reason": "监狱营救失败"
                }
                jail_msg = random.choice([
                    f"🔒 {nickname} 被关回了监狱牢房",
                    f"🚔 {nickname} 被狱卒铐上送回牢里",
                    f"👮‍♂️ {nickname} 重回囚室，铁窗无情"
                ])
                log.append(jail_msg)

            # 汇总失败新闻
            if caught:
                self.global_data.setdefault("news_feed", []).append({
                    "time": now.isoformat(),
                    "content": (
                        f"🚨 【营救新闻】监狱营救失败！"
                        f"{', '.join(self.global_data['users'][uid]['nickname'] for uid in caught)} 被重新逮捕"
                    )
                })

        # 删除房间
        self.global_data["jail_rescue_rooms"].pop(room_id, None)
        return "\n".join(log)


    def quit_jail_team(self):
        rooms = self.global_data.get("jail_rescue_rooms", {})
        for room_id, room in list(rooms.items()):
            if self.user_id in room["members"] and room["status"] == "waiting":
                if self.user_id == room["leader_id"]:
                    self.global_data["jail_rescue_rooms"].pop(room_id)
                    return f"🛑 你是队长，已解散房间 {room_id} 的监狱营救队伍"
                else:
                    room["members"].remove(self.user_id)
                    return (
                        f"🚪 你已退出监狱营救队伍（房间：{room_id}，"
                        f"剩余成员：{len(room['members'])}/4）"
                    )
        return "❌ 当前没有等待中的监狱营救队伍可退出"



    #——————————————————监狱营救————————————————————


    # ————————————————职业模块————————————————
    # 获取玩家职业
    def get_player_career(self):
        """获取当前玩家职业，无需参数"""
        career = self.user_data.get("career", "无业游民")
        return career

    # 申请职业模块
    def apply_career(self, job_name):
        if "APPLY" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        config = self.career_config.get(job_name)
        if not config:
            available = ", ".join(self.career_config.keys())
            return f"❌ 当前可申请的职业有：{available}"

        if self.user_data.get("career"):
            return f"⚠️ 你已是【{self.user_data['career']}】，请先辞职再申请其他职业。"

        req = config.get("requirements", {})

        if req.get("admin_only") and str(self.user_id) not in self.admin_ids:
            return "🚫 该职业仅限管理员申请"

        # 通用条件判断
        if "coins" in req:
            if self.user_data.get("oasis_coins", 0) < req["coins"]:
                return f"💰 申请此职业需要至少 {req['coins']} 绿洲币"

        if "item" in req:
            if not self.has_item_in_inventory(req["item"]):
                return f"📦 你需要持有【{req['item']}】才能申请该职业"

        if "inventory_item" in req:
            if not self.has_item_in_inventory(req["inventory_item"]):
                return f"🌾 你需要持有【{req['inventory_item']}】才可成为 {job_name}"

        # 警察职业专属：射击条件
        shooting_req = req.get("shooting")
        if shooting_req:
            shooting = self.user_data.get("shooting", {})
            shots = shooting.get("total_shots", 0)
            accuracy = shooting.get("accuracy", 0)
            avg_rings = shooting.get("avg_rings", 0)

            if shots < shooting_req.get("shots", 0):
                return f"🔫 需完成至少 {shooting_req['shots']} 次射击训练"
            if accuracy < shooting_req.get("accuracy", 0):
                return f"🎯 命中率需达到 {shooting_req['accuracy']:.0%}，当前为 {accuracy:.2%}"
            if avg_rings < shooting_req.get("avg_rings", 0):
                return f"🎯 平均环数需达到 {shooting_req['avg_rings']} 环，当前为 {avg_rings:.2f} 环"

        self.user_data["career"] = job_name
        return f"✅ 恭喜你成为了【{job_name}】！\n📋 职责：{config['desc']}"

    def can_apply_for_police(self):
        shooting = self.user_data.get("shooting", {})
        shots = shooting.get("total_shots", 0)
        accuracy = shooting.get("accuracy", 0)
        avg_rings = shooting.get("avg_rings", 0)

        if shots < 2000:
            return False, "🔫 申请该职业需完成至少 2000 次靶场射击训练"
        if accuracy < 0.8:
            return False, f"🎯 当前命中率为 {accuracy:.2%}，需达到 80% 以上才能申请此职业"
        if avg_rings < 9.0:
            return False, f"🎯 当前平均环数为 {avg_rings:.2f} 环，需要达到至少 9.00 环才能申请此职业"

        return True, "✅ 你符合申请条件，可以尝试申请该职业"

    # 辞职模块
    def resign_career(self):
        """辞去当前职业"""
        if not self.user_data.get("career"):
            return "📭 你当前没有职业，无需辞职。"

        old = self.user_data["career"]
        self.user_data["career"] = None

        return (
            f"👋 你已成功辞去【{old}】的工作。\n"
            f"💼 你现在是自由人，可以重新申请新职业了。"
        )

    def career_help(self):
        """展示所有可申请的职业与条件"""
        lines = ["## 💼 可申请职业一览："]

        for name, cfg in self.career_config.items():
            desc = cfg.get("desc", "")
            req = cfg.get("requirements", {})

            # 格式化要求文字
            condition_parts = []
            if req.get("admin_only"):
                condition_parts.append("仅限管理员")
            if "coins" in req:
                condition_parts.append(f"{req['coins']}币以上")
            if "item" in req:
                condition_parts.append(f"需持有【{req['item']}】")
            if "inventory_item" in req:
                condition_parts.append(f"需持有【{req['inventory_item']}】")
            if "min_level" in req:
                condition_parts.append(f"等级 ≥ {req['min_level']}")

            cond_text = " | ".join(condition_parts) if condition_parts else "无特殊条件"

            lines.append(f"🔹 **{name}**：{desc}\n    条件：{cond_text}")

        lines.append("\n📌 输入 `申请 <职业名>` 申请职位，`辞职` 可辞去当前职业。")
        return "\n".join(lines)

    def check_shooting_conditions(self, reqs):
        shooting = self.user_data.get("shooting", {})
        shots = shooting.get("total_shots", 0)
        accuracy = shooting.get("accuracy", 0)
        avg_rings = shooting.get("avg_rings", 0)

        if shots < reqs.get("shots", 0):
            return False, f"🔫 你需要完成至少 {reqs['shots']} 次射击训练"
        if accuracy < reqs.get("accuracy", 0):
            return False, f"🎯 命中率需达到 {reqs['accuracy'] * 100:.2f}%（当前 {accuracy * 100:.2f}%）"
        if avg_rings < reqs.get("avg_rings", 0):
            return False, f"🎯 平均环数需达到 {reqs['avg_rings']}（当前 {avg_rings:.2f}）"

        return True, "✅ 你符合射击训练要求"


    # 警察逮捕玩家
    def police_arrest_player(self, cmd_part):
        if "POLICE" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        police_role = self.user_data.get("career", "")
        if police_role not in ["警察", "黑警", "巡逻警察", "刑警", "特警", "卧底警察"]:
            return "❌ 你不是执法人员，无法抓捕！"

        target_id = parse_mirai_at(cmd_part[1])
        if not target_id or target_id not in self.global_data["users"]:
            return "❌ 抓捕对象不存在"

        target = self.global_data["users"][target_id]
        target_nick = target.get("nickname", "未知用户")
        stolen = target.get("oasis_coins", 0)

        if stolen == 0:
            return f"🕵️‍♂️ {target_nick} 并没有赃款。"

        # 默认行为参数
        jail_minutes = 60
        gain = 0
        result_text = ""

        # 各警种行为配置
        arrest_behaviors = {
            "巡逻警察": {
                "gain_pct": 0.5,
                "jail_minutes": 45,
                "to_self": False,
                "desc": f"🚨 你巡逻时逮住了 {target_nick}，没收了一半赃款！"
            },
            "刑警": {
                "gain_pct": 1.0,
                "jail_minutes": 60,
                "to_self": False,
                "desc": f"🕵️ 你顺利将 {target_nick} 抓捕归案，赃款全部充公！"
            },
            "特警": {
                "gain_pct": 1.0,
                "jail_minutes": 90,
                "to_self": False,
                "desc": f"🛡️ 你强力出击逮住了 {target_nick}，赃款全数上缴，监禁时间加长！"
            },
            "卧底警察": {
                "gain_pct": 1.0,
                "jail_minutes": 60,
                "to_self": False,
                "desc": f"🎭 卧底身份暴露！你将 {target_nick} 抓捕并上缴了全部赃款。",
                "require_criminal_flag": True  # 需要有罪犯标记才可行动
            },
            "黑警": {
                "gain_pct": 1.0,
                "jail_minutes": 60,
                "to_self": True,
                "desc": f"👿 你黑吃黑地将 {target_nick} 的赃款据为己有！"
            }
        }

        behavior = arrest_behaviors.get(police_role)

        if not behavior:
            return "❌ 你的警种暂不支持抓捕行为。"

        # 若为卧底警察，需判断玩家是否有罪犯标记
        if behavior.get("require_criminal_flag") and not target.get("criminal_flag"):
            return f"🎭 卧底行动失败，{target_nick} 并未显露犯罪行为。"

        # 计算没收金额
        gain = int(stolen * behavior["gain_pct"])
        target["oasis_coins"] -= gain

        if behavior["to_self"]:
            self.user_data["oasis_coins"] += gain

        # 设置监禁状态
        jail_minutes = behavior["jail_minutes"]
        jail_until = (datetime.now(tz) + timedelta(minutes=jail_minutes)).isoformat()
        target["prison"] = {
            "is_jailed": True,
            "release_time": jail_until,
            "reason": f"{police_role} 抓捕"
        }

        # 写入新闻记录
        self.global_data.setdefault("news_feed", []).append({
            "time": datetime.now(tz).isoformat(),
            "content": f"🔥 {self.nickname}（{police_role}）出手，将 {target_nick} 抓入监狱，赃款处理完毕。"
        })

        return f"{behavior['desc']}\n⛓️ {target_nick} 已被关入监狱，预计释放时间：{jail_until[11:16]}"

    # 判断玩家是否在监狱
    def is_in_jail(self):
        jail_until = self.user_data.get("status", {}).get("in_jailed")
        if not jail_until:
            return False
        return datetime.now(tz) < datetime.fromisoformat(jail_until)

    # --------------------小游戏-------------------

    # ✅ 披萨游戏支持玩家送给其他玩家
    def order_pizza(self, price=10, quantity=1):
        price = int(price)
        if price not in [5, 10, 20]:
            return "❌ 披萨价格只支持 5、10、20 绿洲币档位。"
        if quantity < 1 or quantity > 10:
            return "❌ 披萨数量必须在1到10之间。"
        self.user_data["pizza_order"] = {
            "price": price,
            "quantity": quantity,
            "received": 0
        }
        return f"✅ 你成功点了 {quantity} 份，每份 {price} 绿洲币的披萨，等待送达中..."

    def play_pizza_game(self, target_id=None):
        if "PIZZA" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        weather = random.choices(
            ["晴天", "小雨", "暴风雨"],
            weights=[0.7, 0.2, 0.1],
            k=1
        )[0]

        roll = random.randint(1, 20)

        # 获取当前玩家职业
        career = self.get_player_career()
        is_pizza_worker = (career == "Pizza外卖员")

        # 送给自己，模拟快速赚绿洲币
        if not target_id or target_id == self.user_id:
            # 职业加成倍率
            bonus_multiplier = 1.3 if is_pizza_worker else 1.0

            # 天气影响简单体现，暴风雨降低奖励
            if weather == "暴风雨" and roll <= 6:
                return "🌧️ 暴风雨中送餐失败，披萨被浇坏了，啥也没赚！"
            elif roll <= 6:
                return "🚧 路上遇阻，披萨送迟了，没赚到钱。"
            elif roll <= 12:
                base_reward = 5
                reward = int(base_reward * bonus_multiplier)
                return self.add_reward(reward, f"披萨准时送达，你获得{reward}绿洲币！")
            else:
                base_reward = 10
                reward = int(base_reward * bonus_multiplier)
                return self.add_reward(reward, f"披萨提前送达，你获得{reward}绿洲币！")

        # 送给别人，必须判断对方是否点了披萨
        target = self.find_user(target_id)
        if not target:
            return "❌ 找不到目标玩家。"

        target_data = self.global_data["users"][target["user_id"]]

        order = target_data.get("pizza_order")
        if not order or order["received"] >= order["quantity"]:
            return f"❌ {target['nickname']} 目前没有有效的披萨订单，无法送披萨。"

        price = order["price"]
        quantity = order["quantity"]
        received = order["received"]

        # 检查目标余额
        if target_data["oasis_coins"] < price:
            return f"💸 {target['nickname']} 余额不足，无法支付披萨费用。"

        # 天气对送披萨的影响
        if weather == "暴风雨" and roll <= 8:
            return f"🌩️ 暴风雨中披萨没送到，送餐失败！"

        # 职业加成倍率
        bonus_multiplier = 1.3 if is_pizza_worker else 1.0

        if roll <= 3:
            return f"🚧 路上爆胎了，披萨没送到，没赚到钱。"
        elif roll <= 8:
            tip = max(1, int(price // 5 * bonus_multiplier))
            self.add_reward(tip, f"披萨送达，获得小费 {tip} 绿洲币")
        elif roll <= 15:
            tip = int(price // 2 * bonus_multiplier)
            self.add_reward(tip, f"披萨送达，获得丰厚小费 {tip} 绿洲币")
        else:
            tip = int(price * bonus_multiplier)
            self.add_reward(tip, f"披萨准时送达，获得高额小费 {tip} 绿洲币")

        # 扣除目标余额，给送餐玩家加钱，给目标加披萨券（物品）
        target_data["oasis_coins"] -= price
        self.user_data["oasis_coins"] += price

        # 增加披萨券到目标物品栏
        self.add_simple_item("披萨券", 1, "用于披萨订单的奖励")

        # 更新订单
        target_data["pizza_order"]["received"] += 1

        return (f"🍕 你成功将披萨送给了 {target['nickname']}，获得 {int(price * bonus_multiplier)} 绿洲币！\n"
                f"🌦️ 当前天气：{weather}。\n"
                f"{target['nickname']} 获得一张披萨券。")

    # ✅ 出租车游戏支持玩家接其他玩家

    # 乘客下订单
    def order_taxi(self, price=15, destination="未知地点"):
        price = int(price)
        if price not in [10, 15, 20, 30]:
            return "❌ 车费只支持 10、15、20、30 绿洲币档位。"
        self.user_data["taxi_order"] = {
            "price": price,
            "destination": destination,
            "completed": False
        }
        return f"🚖 你成功叫车，目的地【{destination}】，车费 {price} 绿洲币，等待司机接单。"

    # 司机接单送客
    def play_taxi_game(self, target_id=None):
        if "TAXI" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        weather = random.choices(
            ["晴天", "小雨", "暴风雨", "堵车"],
            weights=[0.6, 0.2, 0.1, 0.1],
            k=1
        )[0]

        roll = random.randint(1, 20)

        # 获取职业，判断是否是Taxi司机
        career = self.get_player_career()
        is_taxi_driver = (career == "Taxi司机")
        bonus_multiplier = 1.3 if is_taxi_driver else 1.0

        # 无目标，随机载客（系统随机生成虚拟乘客）
        if not target_id:
            if roll <= 4:
                self.add_reward(-5, "👿 遇到酒醉流氓逃单，赔了5绿洲币！")
                return "👿 你载到一个喝醉的流氓，逃单砸车门，损失5绿洲币。"
            elif roll <= 8:
                reward = int(8 * bonus_multiplier)
                return self.add_reward(reward, f"普通乘客完成订单，赚了{reward}绿洲币。")
            elif roll <= 14:
                reward = int(15 * bonus_multiplier)
                return self.add_reward(reward, f"商务乘客满意，付了{reward}绿洲币。")
            elif roll <= 19:
                reward = int(20 * bonus_multiplier)
                return self.add_reward(reward, f"高端客户奖励你{reward}绿洲币！")
            else:
                reward = int(50 * bonus_multiplier)
                return self.add_reward(reward, f"一位富豪打赏你{reward}绿洲币！")

        # 目标乘客接单逻辑
        target = self.find_user(target_id)
        if not target:
            return "❌ 找不到目标乘客。"

        target_data = self.global_data["users"][target["user_id"]]
        order = target_data.get("taxi_order")

        if not order or order.get("completed"):
            return f"❌ {target['nickname']} 当前没有有效的叫车订单。"

        price = order["price"]
        destination = order["destination"]

        if target_data["oasis_coins"] < price:
            return f"💸 {target['nickname']} 余额不足，无法支付车费。"

        # 天气和事件影响
        if weather == "暴风雨" and roll <= 7:
            return f"🌩️ 暴风雨导致路线堵塞，送达失败！"
        if weather == "堵车" and roll <= 10:
            partial_fee = int(3 * bonus_multiplier)
            self.add_reward(partial_fee, f"堵车只收了部分车费，赚了{partial_fee}绿洲币。")
            target_data["oasis_coins"] -= partial_fee
            self.user_data["oasis_coins"] += partial_fee
            target_data["taxi_order"]["completed"] = True
            return f"🚗 路上堵车严重，最终只收了{partial_fee}绿洲币，订单完成。"

        # 正常送达，奖励乘以加成
        final_fee = int(price * bonus_multiplier)
        target_data["oasis_coins"] -= price
        self.user_data["oasis_coins"] += final_fee
        target_data["taxi_order"]["completed"] = True

        # 给乘客发个出租车券
        self.add_simple_item("出租车券", 1, "完成打车任务获得")

        return (f"🚖 你成功将 {target['nickname']} 送到【{destination}】，"
                f"赚了 {final_fee} 绿洲币！\n"
                f"🌦️ 当前天气：{weather}。\n"
                f"{target['nickname']} 获得一张出租车券。")

    #——————————————————————拔萝卜模块————————————————————————
    def is_carrot_clan(self):
        return self.user_data.get("career") == "胡萝卜族人"

    @staticmethod
    def carrot_farm_info():
        return (
            "🥕 欢迎来到【萝卜农场】！\n"
            "这里是绿洲最有趣的农场之一，你可以用‘拔萝卜’指令试试运气。\n"
            "说不定能拔到珍稀的金萝卜，或者奇怪的神秘种子！\n"
            "📌 指令提示：输入“拔萝卜”开始尝试拔萝卜。\n"
            "祝你好运，旅者！"
        )

    def sell_all_carrots(self):
        prices = {
            "萝卜": 10,
            "金萝卜": 200,
            "腐烂萝卜": 1,
            "神秘种子": 50,
            "萝卜雕像": 150,
            "断裂萝卜": 3,
            "迷你萝卜": 2,
            "巨型萝卜": 88,
            "老萝卜": 5
        }
        inventory = self.user_data.get("inventory", [])
        sold_items = []
        total_earned = 0

        for item in inventory[:]:  # 遍历副本以便安全删除
            item_id = item["id"]
            if item_id in prices:
                quantity = item.get("quantity", 0)
                if quantity > 0:
                    earned = prices[item_id] * quantity
                    total_earned += earned
                    sold_items.append(f"{item_id} x{quantity}（{earned}币）")
                    inventory.remove(item)

        if total_earned > 0:
            self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + total_earned
            summary = "\n".join(sold_items)
            return f"🥕 一键卖出萝卜成功！共获得 {total_earned} 绿洲币。\n📦 明细：\n{summary}"
        else:
            return "😢 你没有任何可出售的萝卜类物品。"


    def sell_carrot(self, item_id: str, quantity: int):
        prices = {
            "萝卜": 10,
            "金萝卜": 200,
            "腐烂萝卜": 1,
            "神秘种子": 50,
            "萝卜雕像": 150,
            "断裂萝卜": 3,
            "迷你萝卜": 2,
            "巨型萝卜": 88,
            "老萝卜": 5
        }
        inventory = self.user_data.get("inventory", [])
        for item in inventory:
            if item["id"] == item_id:
                if item["quantity"] < quantity:
                    return f"❌ 你没有足够的【{item_id}】。"
                item["quantity"] -= quantity
                if item["quantity"] == 0:
                    inventory.remove(item)
                total_price = prices.get(item_id, 0) * quantity
                self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + total_price
                return f"✅ 已出售 {item_id} x{quantity}，获得 {total_price} 绿洲币。"
        return f"❌ 你没有【{item_id}】。"

    def handle_carrot_command(self, parts: list):
        """
        处理萝卜相关指令：
        - 拔萝卜
        - 卖萝卜 all
        - 卖萝卜 金萝卜 2
        - 价格
        """
        if len(parts) == 1 or parts[1] in ["拔萝卜"]:
            return self.pull_carrot()
        elif parts[1] == "寻宝":
            return self.explore_treasure()
        elif parts[1] in ["帮助", "help"]:
            return self.carrot_help()
        elif parts[1] in ["价格", "price"]:
            return self.show_carrot_price_list()
        elif parts[1] in ["rank", "r", "排行榜"]:
            return self.show_carrot_leaderboard()
        elif len(parts) == 3 and parts[1] == "卖萝卜" and parts[2].lower() == "all":
            return self.sell_all_carrots()
        elif len(parts) == 4 and parts[1] == "卖萝卜":
            item_name = parts[2]
            try:
                quantity = int(parts[3])
            except ValueError:
                return "❌ 卖萝卜的数量必须是数字。"
            return self.sell_carrot(item_name, quantity)
        else:
            return "❌ 指令错误，可尝试：拔萝卜、卖萝卜 <名称> <数量>、卖萝卜 all、价格、萝卜帮助"

    def explore_treasure(self):
        if not self.user_data.get("rabbit_city_unlocked"):
            return "⚠️ 你还没有解锁兔子城，无法进行寻宝。提升声望后再试试吧！"

        treasure_events = [
            {"desc": "你在兔子城郊外找到一箱绿洲币！", "coin": random.randint(50, 150)},
            {"desc": "你发现了一件神秘的兔子遗物，提升声望！", "rep": 5},
            {"desc": "无意间挖到一个藏宝洞穴入口……（待开放）", "coin": 0},
        ]

        event = random.choice(treasure_events)
        msg = event["desc"]
        if "coin" in event and event["coin"] > 0:
            coin_msg = self._change_coin(event["coin"])
            msg += f"\n{coin_msg}"
        if "rep" in event and event["rep"] > 0:
            rep_msg = self._change_reputation(event["rep"])
            msg += f"\n{rep_msg}"

        return msg

    @staticmethod
    def show_carrot_price_list():
        prices = {
            "萝卜": 10,
            "金萝卜": 200,
            "腐烂萝卜": 1,
            "神秘种子": 50,
            "萝卜雕像": 150,
            "断裂萝卜": 3,
            "迷你萝卜": 2,
            "巨型萝卜": 88,
            "老萝卜": 5
        }
        msg = "📜【萝卜价格表】\n"
        for name, price in prices.items():
            msg += f"🔸 {name}：{price} 币\n"
        return msg

    @staticmethod
    def carrot_help():
        return (
            "🥕【萝卜农场指令说明】\n"
            "🔸 农场 拔萝卜                  - 随机获得一种萝卜类物品\n"
            "🔸 农场 卖萝卜 <名称> <数量>    - 出售指定萝卜\n"
            "🔸 农场 卖萝卜                  - 出售所有萝卜类物品\n"
            "🔸 农场 价格                  - 查看所有萝卜售价\n"
            "🌟 拔到金萝卜或雕像会有惊喜收益哦！"
        )

    def pull_carrot(self):
        if "CARROT" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        loot_pool = [
            {"id": "萝卜", "weight": 40, "description": "一根新鲜的脆甜萝卜，吃了精神百倍。"},
            {"id": "金萝卜", "weight": 6, "description": "闪闪发光的金萝卜，价值不菲，极具收藏价值！"},
            {"id": "腐烂萝卜", "weight": 10, "description": "发臭的腐烂萝卜，还是留着做肥料吧……"},
            {"id": "神秘种子", "weight": 3, "description": "不知名的神秘种子，或许能种出奇迹？"},
            {"id": "萝卜雕像", "weight": 1, "description": "奇形怪状的萝卜雕像，仿佛在诉说绿洲的传说。"},
            {"id": "土块", "weight": 10, "description": "嗯……这次拔到了块泥土，继续加油吧！"},
            {"id": "断裂萝卜", "weight": 8, "description": "萝卜断在地里，只剩上半截……太用力了！"},
            {"id": "迷你萝卜", "weight": 8, "description": "比大拇指还小，勉强算萝卜……"},
            {"id": "巨型萝卜", "weight": 4, "description": "足有半人高的巨型萝卜，惊艳全场！"},
            {"id": "老萝卜", "weight": 10, "description": "皱巴巴的老萝卜，咬一口可能会掉牙。"}
        ]

        # 胡萝卜族加成处理
        if self.is_carrot_clan():
            for item in loot_pool:
                if item["id"] in ["金萝卜", "萝卜雕像", "巨型萝卜"]:
                    item["weight"] *= 2  # 加倍稀有物品权重

        # 抽象拔萝卜过程描述
        steps = [
            "你走进田里，盯上了一根特别壮的萝卜……",
            "你握紧萝卜叶子，试图将它拔出来……",
            "你努力地拉啊拉，感觉手快抽筋了！",
            "突然！手感一轻，一阵泥土飞扬……"
        ]
        msg = "\n".join(random.sample(steps, k=3)) + "\n"

        # 随机选中物品
        choices = [item["id"] for item in loot_pool]
        weights = [item["weight"] for item in loot_pool]
        selected_id = random.choices(choices, weights=weights, k=1)[0]
        selected_item = next(item for item in loot_pool if item["id"] == selected_id)

        add_msg = self.add_simple_item(
            item_id=selected_item["id"],
            quantity=1,
            description=selected_item["description"]
        )

        result_commentary = {
            "萝卜": "你如愿以偿地拔出了它，清脆可口！",
            "金萝卜": "阳光照耀下，它闪闪发光，耀眼夺目！",
            "腐烂萝卜": "你犹豫了一下，还是决定用它做肥料。",
            "神秘种子": "这可不是普通萝卜，看起来像是异世界遗物！",
            "萝卜雕像": "你吓了一跳……这玩意居然还有眼睛！",
            "土块": "一脸尴尬地看着手里的泥块……",
            "断裂萝卜": "你低头望去，只剩一截断裂的萝卜在手里。",
            "迷你萝卜": "这也太小了吧？比你想象的袖珍多了点。",
            "巨型萝卜": "你几乎要用两只手才抱得住它，全村最壮！",
            "老萝卜": "它的皮比你的爷爷还老，咬不动系列。"
        }

        msg += f"🎉 你拔出了【{selected_item['id']}】！\n"
        msg += f"📦 描述：{selected_item['description']}\n"
        msg += f"📘 {result_commentary[selected_id]}\n"
        msg += add_msg + "\n"

        # 随机事件系统
        trigger_rate = 0.5 if self.is_carrot_clan() else 0.3
        # 兔子城额外事件触发率
        rabbit_city_bonus = 0.2 if self.user_data.get("rabbit_city_unlocked") else 0
        total_trigger_rate = trigger_rate + rabbit_city_bonus

        if random.random() < total_trigger_rate:
            event_msg = self._carrot_random_event()
            msg += f"\n🎲 随机事件！\n{event_msg}"

        if self.user_data.get("career") == "农民":
            bonus = random.randint(10, 30)
            coin_msg = self.change_coin(bonus, "👩‍🌾 农民拔萝卜加成")
            msg += f"\n👩‍🌾 由于你是农民，拔萝卜获得额外 {bonus} 绿洲币奖励！\n{coin_msg}"
        # 统计拔萝卜次数
        carrot_stats = self.user_data["carrot_stats"]
        carrot_stats["total"] = carrot_stats.get("total", 0) + 1

        # 统计金萝卜次数
        if selected_id == "金萝卜":
            carrot_stats["golden"] = carrot_stats.get("golden", 0) + 1

        return msg

    def show_carrot_leaderboard(self):
        """显示拔萝卜排行榜"""
        carrot_data = self.global_data.get("carrot_leaderboard", [])

        display = [
            "🥕 拔萝卜排行榜",
            "📊 榜单类型: 总榜（按金萝卜优先）",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        # 排名前10名
        sorted_board = sorted(carrot_data, key=lambda x: (x["golden"], x["total"]), reverse=True)
        for idx, entry in enumerate(sorted_board[:10], 1):
            display.append(
                f"{idx}. {entry['nickname']} - 金萝卜 {entry['golden']} 个 / 共拔 {entry['total']} 次"
            )

        # 当前用户是否在榜单中
        user_entry = next((e for e in sorted_board if e["user_id"] == self.user_id), None)
        if user_entry:
            rank = sorted_board.index(user_entry) + 1
            display.append(f"\n👤 你的排名: 第 {rank} 位（金萝卜: {user_entry['golden']}，总数: {user_entry['total']}）")
        else:
            display.append("\n⚠️ 你尚未拔过萝卜或数据未被记录")

        return "\n".join(display)

    def _carrot_random_event(self):
        event_pool = [
            {
                "type": "good",
                "desc": "你遇到一位兔子商人，他给了你一根【金萝卜】，说你看起来很有前途！",
                "effect": lambda: self.add_simple_item("金萝卜", 1, "兔子商人的赠礼") + "\n" + self._change_reputation(
                    2)
            },
            {
                "type": "good",
                "desc": "你在地里拔出一张【兔子藏宝图】，上面记着一些神秘坐标……",
                "effect": lambda: self.add_simple_item("兔子藏宝图", 1,
                                                       "标着坐标的老旧兔图") + "\n" + self._change_reputation(1)
            },
            {
                "type": "good",
                "desc": "你躺在草地上休息，发现四叶幸运草，获得额外绿洲币！",
                "effect": lambda: self._change_coin(88)
            },
            {
                "type": "neutral",
                "desc": "兔子隐士出现：“拔萝卜者，当学会选择之道。” 他留下一句谜语后离去。",
                "effect": lambda: self._change_reputation(1)
            },
            {
                "type": "bad",
                "desc": "一只兔子贼猛地从你背后扑来，抢走了一根【萝卜】！",
                "effect": lambda: self._remove_item("萝卜", 1) + "\n" + self._change_reputation(-2)
            },
            {
                "type": "bad",
                "desc": "你掉进了兔子挖的陷阱，被传送到了一个黑暗洞穴……（未开放）",
                "effect": lambda: self._change_coin(-20)
            },
            {
                "type": "bad",
                "desc": "兔子大妈拿着萝卜种强行推销，你勉为其难花了30币。",
                "effect": lambda: self._change_coin(-30) + "\n" + self._change_reputation(-1)
            },
            {
                "type": "egg",
                "desc": "你发现一个【发光的地穴】，里面有刻着“R.Z.W”的奇怪石板……",
                "effect": lambda: self.add_simple_item("R.Z.W石板", 1,
                                                       "刻着古兔文的石板，或许能翻译") + "\n" + self._change_reputation(
                    3)
            },
            {
                "type": "good",
                "desc": "兔子城守卫送你一份特别礼物：神秘的兔子徽章！",
                "effect": lambda: self.add_simple_item("兔子徽章", 1,
                                                       "兔子城专属徽章") + "\n" + self._change_reputation(3)
            },
            {
                "type": "neutral",
                "desc": "兔子城的传说激励了你，声望略微提升。",
                "effect": lambda: self._change_reputation(1)
            }
            ]


        event = random.choice(event_pool)
        msg = f"{event['desc']}"
        try:
            effect_result = event["effect"]()
            if effect_result:
                msg += f"\n💡 {effect_result}"
        except Exception as e:
            msg += f"\n⚠️ 事件异常：{e}"
        return msg

    def _change_coin(self, amount: int):
        old_coin = self.user_data.get("coin", 0)
        self.user_data["coin"] = old_coin + amount
        change_text = f"{'获得' if amount > 0 else '失去'}了 {abs(amount)} 绿洲币！"

        # 彩蛋：极低概率遇到神秘金币翻倍
        if amount > 0 and random.random() < 0.01:
            bonus = amount  # 翻倍
            self.user_data["coin"] += bonus
            change_text += f"\n🎉 幸运彩蛋！神秘金币力量加持，又获得了额外 {bonus} 币！"

        animation = "💰" + "⋯" * random.randint(1, 3)
        return f"{animation} {change_text}"

    def _remove_item(self, item_id: str, quantity: int):
        inventory = self.user_data.get("inventory", [])
        for item in inventory:
            if item["id"] == item_id:
                if item["quantity"] < quantity:
                    return f"❌ 背包中没有足够的【{item_id}】。"
                item["quantity"] -= quantity
                if item["quantity"] == 0:
                    inventory.remove(item)
                msg = f"🗑️ 失去了 {item_id} x{quantity}。"

                # 彩蛋：被偷走的萝卜突然又滚回来了（极小概率）
                if item_id == "萝卜" and random.random() < 0.005:
                    self.add_simple_item("萝卜", 1, "从地洞里滚回来的萝卜……")
                    msg += "\n🤯 彩蛋事件！被偷的萝卜自己滚了回来！"
                return msg
        return f"❌ 你没有【{item_id}】。"

    def _change_reputation(self, amount: int):
        self.user_data["reputation"] = self.user_data.get("reputation", 0) + amount
        return f"🐰兔子声望 {'提升' if amount > 0 else '下降'}了 {abs(amount)} 点！"

    def check_rabbit_city_unlock(self):
        rep = self.user_data.get("reputation", 0)

        # 判断是否解锁
        if rep >= 20 and not self.user_data.get("rabbit_city_unlocked"):
            self.user_data["rabbit_city_unlocked"] = True
            return "\n🏰 你的兔子声望已经引起了“萝卜议会”的注意，兔子城邦对你开放了！输入 `兔子城` 前往探访 🐰"

        if self.user_data.get("rabbit_city_unlocked"):
            return "\n🐰 兔子城邦已向你开放，输入 `兔子城` 前往探访！"
        else:
            return f"\n🐰 当前兔子声望：{rep}/20，声望达到 20 后将解锁兔子城邦！可通过参与农场活动或任务提升声望 📈"

    # 出海钓鱼模块
    def go_fishing(self):
        if "FISHING" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        is_fisherman = self.user_data.get("profession") == "渔民"
        is_engineer = self.user_data.get("profession") == "工程师"

        # 初始化小船耐久度，默认100
        if "boat_durability" not in self.user_data:
            self.user_data["boat_durability"] = 100

        # 小船已坏，必须修理
        if self.user_data["boat_durability"] <= 0:
            return "🚤 你的小船已经坏了，必须先修理才能继续出海。请使用 修理 或 fix 指令。"

        weather = random.choices(
            ["晴天", "阴天", "雷雨", "暴风雨"],
            weights=[50, 30, 15, 5], k=1
        )[0]

        weather_effect = f"🌤 当前天气：{weather}\n"

        dodge_rate = 0.3 if is_fisherman else 0

        # 极端天气扣钱事件（考虑渔民躲避加成）
        if weather == "暴风雨" and random.random() < 0.4 * (1 - dodge_rate):
            lost_coin = min(200, self.user_data.get("oasis_coins", 0))
            self.user_data["oasis_coins"] -= lost_coin
            return (
                weather_effect +
                "🌊 你刚一出海，狂风暴雨席卷而来！\n"
                "⛈️ 巨浪翻涌，小船被掀翻！\n"
                f"💸 你损失了 {lost_coin} 绿洲币修船……建议换个天气再来。"
            )
        if weather == "雷雨" and random.random() < 0.15 * (1 - dodge_rate):
            lost_coin = min(50, self.user_data.get("oasis_coins", 0))
            self.user_data["oasis_coins"] -= lost_coin
            return (
                weather_effect +
                "🌧 雷雨让海面十分危险，你的小船被海浪冲击！\n"
                f"💸 你损失了 {lost_coin} 绿洲币修复小船。小心安全！"
            )

        # 海盗事件（考虑躲避加成）
        if random.random() < 0.07 * (1 - dodge_rate):
            lost_coin = min(300, self.user_data.get("oasis_coins", 0))
            self.user_data["oasis_coins"] -= lost_coin
            flavor_text = self.get_fishing_flavor_event(weather, context="pirate")
            return weather_effect + flavor_text + f"\n💸 你损失了 {lost_coin} 绿洲币，赶紧躲开他们！"

        # 小船损坏事件 5%概率
        if random.random() < 0.05:
            damage = random.randint(10, 30)
            self.user_data["boat_durability"] -= damage
            if self.user_data["boat_durability"] < 0:
                self.user_data["boat_durability"] = 0
            return (
                weather_effect +
                f"💥 出海途中小船遭遇了损坏，耐久度下降了 {damage} 点。\n"
                f"🛠 当前耐久度：{self.user_data['boat_durability']}。\n"
                "🚨 耐久度为0时无法继续出海，需要工程师修理。"
            )

        # 检查藏宝图寻宝
        has_treasure_map = any(item["id"] == "藏宝图" for item in self.user_data.get("inventory", []))
        if has_treasure_map and random.random() < 0.2:
            treasure_items = [
                {"id": "海盗宝箱", "description": "古老的宝箱，装满了金币和珍宝！"},
                {"id": "古代金币", "description": "闪闪发光的金币，价值不菲。"},
                {"id": "神秘宝石", "description": "散发着幽光的宝石，传说能带来好运。"}
            ]
            treasure = random.choice(treasure_items)
            add_msg = self.add_simple_item(treasure["id"], 1, treasure["description"])
            return weather_effect + "💎 你发现了藏宝图指引的宝藏！\n" + f"📦 宝藏：【{treasure['id']}】\n" + add_msg

        # 钓鱼总体概率控制
        event_roll = random.random()

        big_fish_boost = 1.5 if is_fisherman else 1

        if event_roll < 0.3:
            no_fish_msgs = [
                "🎣 今天鱼儿不太给力，一条也没钓到……",
                "🌊 水面平静，鱼儿躲得远远的，你什么也没钓上来。",
                "😓 钓了一会儿，只有风和浪陪着你。",
                "🦢 远处有只天鹅掠过，却没带来鱼讯。",
                "🕊️ 海鸥在你头顶盘旋，却没发现什么好钓的。"
            ]
            return weather_effect + random.choice(no_fish_msgs)

        elif event_roll < 0.5:
            junk_pool = [
                {"id": "破桶", "description": "装满海水的破旧木桶，发出咕噜咕噜的声音。"},
                {"id": "铁罐", "description": "锈迹斑斑的铁罐，上面有字：‘去图书馆看看’。"},
                {"id": "浮游海草", "description": "一缕漂浮的海草，有点香。"},
                {"id": "塑料瓶", "description": "绿洲环保基金正在通缉这个瓶子。"},
                {"id": "海盗的靴子", "description": "一只破靴子，钓上来时你愣住了。"},
                {"id": "神秘漂流瓶", "description": "瓶子里藏着藏宝图的碎片……"},
                {"id": "古代鱼化石", "description": "这是一块古鱼化石，带点神秘气息。"},
                {"id": "藏宝图", "description": "这是一张藏宝图，可以带领你找到宝藏。"}
            ]
            item = random.choice(junk_pool)
            add_msg = self.add_simple_item(item["id"], 1, item["description"])
            return (
                weather_effect +
                f"🎣 你钓上来一个【{item['id']}】。\n📦 描述：{item['description']}\n" +
                add_msg
            )

        else:
            fish_pool = [
                {"id": "小黄鱼", "weight": 30, "description": "常见的淡水鱼，适合烤着吃。"},
                {"id": "蓝鳍金枪鱼", "weight": 5 * big_fish_boost, "description": "超大型鱼类，价值连城！"},
                {"id": "神秘鬼鱼", "weight": 3, "description": "全身透明，仿佛来自异世界。"},
                {"id": "毒河豚", "weight": 6, "description": "含剧毒，请立即送医处理。"},
                {"id": "超大金鱼", "weight": 1 * big_fish_boost, "description": "整条船都为它腾空间，超巨大金鱼！"},
                {"id": "黄金比目鱼", "weight": 2 * big_fish_boost, "description": "闪耀着金币光泽的传奇鱼类。"},
                {"id": "会说话的鱼", "weight": 1, "description": "它盯着你说：'把我放回去你会发财。'"},
                {"id": "星空小鱼", "weight": 10, "description": "在海底星光中闪烁的梦幻鱼类。"}
            ]
            weights = [f["weight"] for f in fish_pool]
            selected_fish = random.choices(fish_pool, weights=weights, k=1)[0]

            narration = ""
            if selected_fish["id"] in ["蓝鳍金枪鱼", "超大金鱼", "黄金比目鱼"]:
                narration = (
                    "🎣 你感到鱼竿一震，差点握不住！\n"
                    "🌀 鱼线被拉得笔直，小船开始左右摇晃！\n"
                    "💪 你咬紧牙关，全力拉扯……\n"
                    f"🎉 最终你钓上来一条【{selected_fish['id']}】！"
                )
            else:
                narrations = {
                    "雷雨": [
                        "⚡ 雷电交加，你仍坚定地守在钓竿旁……",
                        "🌧 雨幕中，你紧紧握住鱼竿不让它滑落……",
                        "⚡ 电光闪烁，你目不转睛盯着浮漂……"
                    ],
                    "暴风雨": [
                        "🌊 狂风暴雨中，你咬牙坚持钓鱼！",
                        "🌪️ 小船剧烈摇晃，你死死抓住鱼竿……",
                        "💥 在汹涌波涛中，你拼命与大鱼搏斗！"
                    ],
                    "阴天": [
                        "阴云密布，你默默等待鱼儿咬钩……",
                        "轻风吹拂，你感受到水下的动静……",
                        "海面平静，鱼群时隐时现……"
                    ],
                    "晴天": [
                        "阳光洒满海面，鱼儿活跃异常。",
                        "微风徐徐，鱼儿轻轻咬钩。",
                        "晴朗天气，钓鱼心情大好！"
                    ]
                }
                narration = random.choice(narrations.get(weather, ["你钓上了一条鱼！"])) + "\n" + f"🎉 钓到：【{selected_fish['id']}】"

            add_msg = self.add_simple_item(selected_fish["id"], 1, selected_fish["description"])
            flavor_text = self.get_fishing_flavor_event(weather)

            return weather_effect + narration + "\n" + add_msg + "\n" + flavor_text

    @staticmethod
    def get_fishing_flavor_event(weather, context=None):
        # 钓鱼随机事件补充描述，支持特殊情景 context
        if context == "pirate":
            pirate_texts = [
                "🏴‍☠️ 海面上一群海盗突然出现，他们的黑旗猎猎作响！",
                "⚔️ 海盗的船只迅速接近，你能听到他们的喊杀声。",
                "🛶 海盗们挥舞着刀剑，显然不欢迎你的出现。",
                "💀 海盗大喊：“把船开到码头，整点薯条吃吃！”",
                "⚓ 海盗船长吹起了吆喝声，像在招募新水手。",
                "🍺 远处海盗们正举杯庆祝，顺便警告你别靠近。"
            ]
            return random.choice(pirate_texts)

        base_events = {
            "晴天": [
                "🌞 温暖的阳光洒在脸上，海风轻轻拂过，心情格外愉悦。",
                "🐬 远处海豚跳跃，似乎在为你的好运喝彩。",
                "🦀 你看到小螃蟹在岩石上忙碌着，好一派生机盎然。",
                "🌅 夕阳染红了海面，天空美得让人忘记了时间。",
                "🍹 你感受到海风中夹杂着一丝热带果香，十分惬意。",
                "🎶 远处传来渔歌，仿佛在为你加油打气。"
            ],
            "阴天": [
                "☁️ 阴云密布，但风平浪静，适合耐心等待。",
                "🦢 远处天鹅安静地游弋，增添了几分宁静。",
                "🍃 轻风带来了海的气息，令人神清气爽。",
                "🌫 远方海面隐约有雾气升腾，神秘莫测。",
                "🕊️ 一只海鸥掠过头顶，叽叽喳喳地说：“去码头整点薯条吧！”",
                "🌾 海面泛起淡淡涟漪，如同画卷般柔和。"
            ],
            "雷雨": [
                "⚡ 雷声滚滚，偶尔闪电划破天际，气氛紧张刺激。",
                "🌧 雨滴打在海面上，泛起阵阵涟漪。",
                "🌩 雷雨交加，仿佛海神在发怒。",
                "💦 雷雨中你听见远处海浪轰鸣，心跳加速。",
                "🌨 闪电劈开天空，像银蛇划破夜幕。",
                "🌪 风暴中心的海水被卷起，形成漩涡般旋转。"
            ],
            "暴风雨": [
                "🌪️ 狂风怒吼，巨浪翻腾，海面一片混沌。",
                "💨 暴雨如注，海水打湿了你的衣服。",
                "🌊 小船剧烈摇晃，仿佛随时会被吞没。",
                "🌀 你紧握船舵，抵御着猛烈的风浪冲击。",
                "⚠️ 雷鸣电闪，海面上偶尔有巨浪拍击船身。",
                "🌩 暴风雨掀起的海水溅到你脸上，冰冷刺骨。"
            ]
        }
        return random.choice(base_events.get(weather, ["你静静享受着出海的时光。"]))

    # 工程师职业技能 修理船只
    def fix_boat(self, user_id=None):
        """
        修理指定玩家的船（或当前玩家自己），
        传入user_id修理指定玩家，否则修理自己。
        """
        # 如果未指定user_id，修理自己

        target_user_id = parse_mirai_at(user_id)
        target_user_data =  self.global_data["users"][str(target_user_id)]
        if target_user_data is None:
            return f"❌ 找不到用户ID为 {target_user_id} 的玩家数据。"

        # 只有职业为“工程师”的玩家才能修理（这里判断修理者的职业）
        if self.user_data.get("career") != "工程师":
            return "⚠️ 只有职业为工程师的玩家才能修理小船。"

        # 目标玩家的船耐久
        boat_durability = target_user_data.get("boat_durability", 100)
        if boat_durability >= 100:
            return "🛥 该玩家的小船耐久度已满，无需修理。"

        repair_cost = 100  # 修理费用
        coins = self.user_data.get("oasis_coins", 0)  # 修理者的钱

        if coins < repair_cost:
            return f"💰 你没有足够的绿洲币修理小船，需要 {repair_cost} 绿洲币。"

        # 扣钱，修理指定玩家的船
        self.user_data["oasis_coins"] -= repair_cost
        target_user_data["boat_durability"] = 100


        if target_user_id == self.user_data.get("user_id"):
            return "🛠 修理完成，你的小船耐久度恢复到100，祝你出海顺利！"
        else:
            return f"🛠 修理完成，玩家 {target_user_id} 的小船耐久度恢复到100。"

    # 潜水捕鱼模块
    def dive_fishing(self):
        if "DIVING" in self.disabled_modules:
            return "🚫 该游戏模块已被管理员禁用"

        # 潜水起始描述
        intro = random.choice([
            "你穿上潜水服，跃入神秘蓝色海底……",
            "水面波光粼粼，你缓缓下潜，鱼群环绕。",
            "你闭上眼，一头扎入冰冷的深海……",
            "氧气瓶冒出气泡，你开始探索深渊。"
        ])

        msg = f"🌊 【潜水探索中】\n{intro}\n"

        # 潜水掉落池
        loot_pool = [
            {"id": "珊瑚鱼", "weight": 30, "description": "色彩斑斓的珊瑚鱼，令人心情愉悦。"},
            {"id": "乌贼", "weight": 25, "description": "喷墨逃逸的大乌贼，小心它的伎俩。"},
            {"id": "深海怪鱼", "weight": 10, "description": "长着灯泡的怪鱼，充满深海压力感。"},
            {"id": "海底珍珠", "weight": 5, "description": "海底采集到的纯白珍珠，价值不菲。"},
            {"id": "神秘贝壳", "weight": 8, "description": "壳上刻着奇怪图案的贝壳。"},
            {"id": "星辰碎片", "weight": 2, "description": "星光洒落深海后凝结的结晶体。"},
            {"id": "有毒水母", "weight": 10, "description": "碰到后会引起强烈中毒反应，需要及时就医！"},
            {"id": "深海金币", "weight": 4, "description": "沉没船只留下的金币，有淡淡海腥味。"},
            {"id": "遗落的耳环", "weight": 2, "description": "一枚古老的海底首饰，也许藏着故事。"},
            {"id": "宝藏箱残片", "weight": 1, "description": "锈蚀的宝箱碎片，似乎曾封印着什么。"}
        ]

        # 高风险事件 - 遇到鲨鱼
        if random.random() < 0.08:
            coin_lost = min(self.user_data.get("oasis_coins", 0), random.randint(10, 100))
            self.user_data["oasis_coins"] -= coin_lost
            return (
                "🦈 你刚一入水，一只大鲨鱼向你游来！\n"
                "⚠️ 你慌乱中逃生，只带走了一枚金币。\n"
                f"💸 你失去了 {coin_lost} 绿洲币。建议换个海域。"
            )

        # 正常掉落流程
        choices = [i["id"] for i in loot_pool]
        weights = [i["weight"] for i in loot_pool]
        selected_id = random.choices(choices, weights=weights, k=1)[0]
        selected_item = next(i for i in loot_pool if i["id"] == selected_id)

        # 处理中毒

        if selected_id == "有毒水母":
            # 处理中毒
            self.user_data.setdefault("status", {})["poisoned"] = True
            msg += (
                "☠️ 你被【有毒水母】蜇伤，皮肤开始麻痹……\n"
                "🏥 状态：中毒，请尽快“去医院”解毒！\n"
            )
        else:
            # 统一调用，description 从字典里取
            desc = self.FISHES.get(selected_id, {}).get("description", selected_item["description"])
            self.add_simple_item(selected_id, 1, desc)
            msg += f"🐟 你发现了【{selected_id}】！\n📦 描述：{desc}\n"

        return msg

    def sell_all_fish(self):
        inventory = self.user_data.get("inventory", [])
        sold_items = []
        total_earned = 0
        qty_to_remove = {}

        for item in inventory[:]:  # 遍历副本
            item_id = item.get("id")
            if item_id in self.FISHES:
                quantity = item.get("quantity", 0)
                if quantity > 0:
                    price_per = self.FISHES[item_id]["price"]
                    earned = price_per * quantity
                    total_earned += earned
                    sold_items.append(f"{item_id} x{quantity}（{earned}币）")
                    inventory.remove(item)

        if total_earned > 0:
            self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + total_earned
            summary = "\n".join(sold_items)
            return f"🐟 一键卖鱼成功！共获得 {total_earned} 绿洲币。\n📦 明细：\n{summary}"
        else:
            return "😢 你没有任何可出售的鱼类。"

    def sell_fish(self, fish_name: str, quantity: int):
        fish_name = fish_name.strip()
        if quantity <= 0:
            return "❌ 卖鱼数量必须大于0。"

        if not self.has_item_in_inventory(fish_name):
            return f"❌ 你没有足够的【{fish_name}】，或者根本没有。"

        if fish_name not in self.FISHES:
            return f"❌ 【{fish_name}】不在可售鱼类列表中。"

        price_per = self.FISHES[fish_name]["price"]
        total_price = price_per * quantity

        # 扣除鱼 — 列表结构，需要遍历扣除对应数量
        inventory = self.user_data.get("inventory", [])
        qty_to_remove = quantity
        for item in inventory[:]:  # 遍历一份副本方便删除
            if item.get("id") == fish_name:
                item_qty = item.get("quantity", 0)
                if item_qty <= qty_to_remove:
                    qty_to_remove -= item_qty
                    inventory.remove(item)
                else:
                    item["quantity"] -= qty_to_remove
                    qty_to_remove = 0
                if qty_to_remove == 0:
                    break

        # 增加绿洲币
        self.user_data["oasis_coins"] = self.user_data.get("oasis_coins", 0) + total_price

        return f"💰 你卖出了 {fish_name} x{quantity}，获得 {total_price} 绿洲币。"

    @staticmethod
    def fishing_help():
        help_text = (
            "🌊 【潜水钓鱼帮助指南】 🌊\n\n"
            "🎣 如何钓鱼？\n"
            "- 使用指令 sail 或者 出海 开始潜水钓鱼，每次可获得随机鱼类或宝藏。\n"
            "- 钓到的鱼会加入你的【海底图鉴】，首次发现会有解锁提示。\n\n"
            "🐟 鱼类与价值\n"
            "- 钓鱼掉落多样鱼类，珍稀鱼价值更高，卖鱼可换绿洲币。\n"
            "- 使用 卖鱼 <鱼名> <数量> 来卖鱼，赚取绿洲币。\n\n"
            "⚠️ 特殊事件与风险\n"
            "- 鲨鱼袭击：小概率遇鲨鱼，会损失部分绿洲币，注意安全！\n"
            "- 有毒水母：被蜇会中毒，需尽快用“去医院”解毒。\n"
            "- 星空奖励：每日10:00-04:00间，钓鱼有概率额外获得星空小鱼。\n\n"
            "💰 卖鱼指南\n"
            "- 用 卖鱼 指令卖出背包中鱼类，支持批量卖出。\n"
            "- 价格根据鱼种不同，请用 价格表 查看最新卖价表。\n\n"
            "📊 钓鱼排行榜\n"
            "- 多钓鱼，多上榜！排行榜分日榜、月榜、总榜，自动更新。\n\n"
            "📝 小贴士\n"
            "- 合理安排每日钓鱼次数。\n"
            "- 遇到毒水母请及时治疗。\n"
            "- 集中卖鱼最大化收益。\n"
            "- 关注星空奖励时间段，收获更多惊喜！\n\n"
            "祝你钓鱼愉快，收获满满！🎣✨"
        )
        return help_text

    def show_fish_price_list(self):
        lines = ["🎣 当前可售鱼类价格表："]
        for fish_name, info in self.FISHES.items():
            price = info.get("price", "未知")
            description = info.get("description", "")
            lines.append(f"• {fish_name} — 价格：{price} 绿洲币 — {description}")
        return "\n".join(lines)

    def handle_fishing_command(self, parts: list):
        """
        处理钓鱼相关指令
        指令示例：
        - 钓鱼
        - 卖鱼 小黄鱼 3
        - 卖鱼 all
        - 鱼价
        """
        if parts is None:
            return self.fishing_help()

        if len(parts) == 2:
            if parts[1] in ["钓鱼", "fishing"]:
                return self.go_fishing()
            elif parts[1] in ["潜水", "diving", "dive"]:
                return self.dive_fishing()
            elif parts[1] in ("鱼价", "卖鱼表", "price"):
                return self.show_fish_price_list()
            elif parts[1] in ["help", "帮助"]:
                return self.fishing_help()

        elif len(parts) == 3 and parts[1] == "卖鱼" and parts[2].lower() == "all":
            return self.sell_all_fish()

        elif len(parts) == 4 and parts[1] == "卖鱼":
            fish_name = parts[2]
            try:
                quantity = int(parts[3])
            except ValueError:
                return "❌ 卖鱼数量必须是数字。"
            return self.sell_fish(fish_name, quantity)

        return "❌ 指令格式错误，正确格式：\n钓鱼\n卖鱼 <鱼名> <数量>\n卖鱼 all\n鱼价"

    def show_aquarium_log(self, page=1):
        """展示玩家海底图鉴"""
        log = self.user_data.get("aquarium_log", {})
        if not log:
            return (
                "📖 你的图鉴还空空如也……\n"
                "🎣 尝试出海钓鱼或潜水捕获水生生物以解锁图鉴！"
            )

        items = list(log.items())
        items.sort(key=lambda x: x[1]["discovered"])  # 按发现时间排序
        total = len(items)
        per_page = 5
        max_page = (total + per_page - 1) // per_page
        page = max(1, min(page, max_page))
        start = (page - 1) * per_page
        end = start + per_page

        display = [
            f"📚【OASIS 海底图鉴】第 {page}/{max_page} 页（共 {total} 种）",
            "━" * 30
        ]

        for name, info in items[start:end]:
            time_str = info["discovered"][11:16]  # 截取时分
            display.append(
                f"🐠 {name}\n📦 {info['description']}\n📅 首次发现时间: {time_str}\n"
            )

        display.append("📌 输入 `图鉴 2` 查看下一页")
        return "\n".join(display)

    # 医院治疗模块
    def go_hospital(self, cmd_parts):
        if "HOSPITAL" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        if cmd_parts[1] in ["rescue", "援助", "救"]:
            return self.rescue_from_hospital(cmd_parts[2])
        if not self.user_data["status"].get("poisoned", False):
            return "🏥 医生摇头：你目前身体健康，无需治疗。"

        cure_cost = 200
        if self.user_data["oasis_coins"] < cure_cost:
            return f"💸 治疗费用为 {cure_cost} 绿洲币，你的余额不足，无法解毒！"

        self.user_data["oasis_coins"] -= cure_cost
        self.user_data["status"]["poisoned"] = False

        return (
            f"🏥 你接受了解毒治疗，花费 {cure_cost} 绿洲币。\n"
            "💊 医生提醒你：下次别靠近那些透明的水母了！\n"
            f"💰 当前余额：{self.user_data['oasis_coins']}"
        )

    # 新闻模块
    def get_news_feed(self):
        if "NEWS" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        news_list = self.global_data.get("news_feed", [])
        if not news_list:
            return "📰 今日无重大新闻，一切如常。"

        # 获取当前日期字符串，例如 '2025-06-01'
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 过滤当天新闻，同时收集非当天新闻以备删除
        today_news = []
        old_news = []
        for news in news_list:
            news_date = news["time"][:10]
            if news_date == today_str:
                today_news.append(news)
            else:
                old_news.append(news)

        # 将昨天及更早新闻从 global_data 清除
        if old_news:
            self.global_data["news_feed"] = today_news

        if not today_news:
            return "📰 今日无重大新闻，一切如常。"

        # 按时间倒序，最多显示10条
        latest_news = sorted(today_news, key=lambda x: x["time"], reverse=True)[:10]

        return "🗞️ 今日新闻头条：\n" + "\n".join(
            [f"📅 {n['time'][11:16]} - {n['content']}" for n in latest_news]
        )
    # 摸摸头模块
    def touch_head(self, target_id=None):
        if "TOUCH" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"

        adult_mode = self.global_data["config"].get("adult_mode", False)

        if not target_id:
            return "❓ 你想摸谁的头？请提供玩家ID。"

        target = self.find_user(target_id)
        if not target:
            return "❌ 找不到目标玩家。"

        nickname = target["nickname"]

        messages = {
            "comfort": [
                f"🫂 你轻轻地摸了摸 {nickname} 的头：“别难过，一切都会好起来的。”",
                f"🤗 你拍拍 {nickname} 的脑袋：“乖，今天也要打起精神来！”",
                f"🍬 你摸了摸 {nickname} 的头发，还递上糖：“奖励给你，最棒的你。”"
            ],
            "cute_flirty": [
                f"🥺 你坏笑着揉了揉 {nickname} 的头：“这么可爱，拿来rua！”",
                f"😏 你悄悄靠近摸了下 {nickname} 的头：“摸一下不会怀孕吧？”",
                f"🧸 你像对待小猫一样揉乱了 {nickname} 的头发：“今天也很乖哦~”"
            ],
            "suggestive": [
                f"🔥 你一边摸着 {nickname} 的头，一边低声说：“再往下就要收费了哦。”",
                f"💋 你靠得很近地摸了摸 {nickname} 的头：“头发好软...想一直摸下去呢。”",
                f"💦 你用指尖绕着 {nickname} 的发丝：“摸着摸着...怎么就上头了呢？”"
            ]
        }

        if adult_mode:
            messages["adult"] = [
                f"💋 你轻柔地摸着 {nickname} 的头，手指不小心滑进了他/她的发根…气氛有点不对劲了。",
                f"👅 你凑近 {nickname} 耳边低语：“摸头只是前戏…你想不想来点更刺激的？”",
                f"🛏️ 你一边抚摸着 {nickname} 的头发，一边压低声音：“你是不是…在等我主动？”",
                f"💦 你摸着摸着忽然停了下来，笑着说：“再往下摸，你可要负责哦。”",
                f"🥵 你轻抚着 {nickname} 的头发，说：“你这副表情，真的好想把你…抱回家。”",
                f"🔥 你拨弄着 {nickname} 的发丝，眼神灼热：“乖一点…别动，让我摸久一点。”",
                f"👀 你摸着 {nickname} 的头，说：“怎么？下面也想被摸摸？”",
                f"🖤 你在 {nickname} 耳边轻声说：“头是给别人看的，那你…愿不愿意把别的地方给我摸？”",
                f"👄 你轻轻吻了下 {nickname} 的发顶，喃喃道：“这样摸着你，感觉整个人都要化了…”",
                f"💫 你指尖在 {nickname} 的发间游走，轻声问：“如果我继续，你会忍得住吗？”",
                f"🫦 你一边摸着 {nickname} 的头，一边暧昧地笑道：“怎么？害羞了？我还没碰到重点呢。”",
                f"🍷 你看着 {nickname} 的眼睛，慢慢抚摸着他说：“今晚…你不许逃。”",
                f"🛋️ 你坐在沙发上让 {nickname} 靠过来，轻柔地摸着他说：“这样乖乖的，真想一直宠着你…”",
                f"🕯️ 你把手放在 {nickname} 的脖颈后，说：“头摸完了，接下来……轮到哪儿好呢？”",
                f"💢 你低声在 {nickname} 耳边说：“别这样看着我…我可控制不住继续摸下去。”",
                f"💞 你边摸着 {nickname} 的发丝，边笑道：“你这样乖乖让我摸，是不是也在等我更进一步？”",
                f"🌙 你靠近 {nickname}，手指缓慢地滑过他的发根，说：“夜还长，我们慢慢来。”",
                f"🖤 你轻叹一声，说：“摸头只是借口，想要的是你整个人。”"
            ]

        # 权重分配
        types = list(messages.keys())
        weights = [0.4, 0.3, 0.2] + ([0.4] if adult_mode else [])
        category = random.choices(types, weights=weights, k=1)[0]
        line = random.choice(messages[category])

        return line

    # 幻想模块  xes

    def love_play_solo(self):
        if "XES" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        events = [
            "你闭上眼睛，幻想自己是绿洲集团CEO，身边七位AI女仆贴身服侍……\n结果AI女仆冷漠关机：『色欲过载，系统已自我保护。』💻",
            "你在脑内回味上次亲密互动，对方忽然问你：『你这么主动，是想让我叫你主人吗？』\n🥴 你瞬间破防。",
            "你正要解开梦中情人的衣领，画面突然扭曲——系统管理员冷着脸出现：『未成年模式未关闭，幻想强制中断。』⚠️",
            "你幻想着与某人赤足在沙滩纠缠，耳边传来喘息声……一只毒水母飞踹了你：『不许在海边开车。』🐙",
            "你刚沉浸在湿热的梦境中，一道提示弹出：『因你单身状态已持续过长，该幻想已锁定为“只可远观”。』🔒",
            "你梦见自己被围观：『绿洲最性感的Alpha！』结果睁眼发现是在澡堂被一群萝卜围住蹭腿。🥕",
            "你默默幻想着：‘我和 yaya 被困在一张床上……’啪！管理员一巴掌把你扇出梦境大厅。🛏️💢"
        ]

        msg = "💤 你闭上眼，进入幻想空间...\n\n" + "💭 " + random.choice(events)
        return msg

    def love_play_target(self, raw_target):
        if "XES" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"

        target_id = parse_mirai_at(raw_target)
        if not target_id or target_id not in self.global_data["users"]:
            return "❌ 无法找到该对象，你的爱毫无着落。"

        target = self.global_data["users"][target_id]
        target_name = target["nickname"]

        interactions = [
            f"你轻抚着 {target_name} 的脸低声说：『今晚…我们能不能不回主城？』\n💋 {target_name} 红着脸说：『你…你想做什么？』",
            f"你一边揉着 {target_name} 的肩膀一边说：『你知道我最喜欢的触感是什么吗？』\n🛏️ {target_name} 咽了口口水：『……我不敢问。』",
            f"你凑近 {target_name} 的耳边低语：『想不想体验一下……双人模式？』\n🔥 {target_name} 的脸瞬间烧红了。",
            f"你试图和 {target_name} 打情骂俏，对方忽然靠得更近：\n『你敢撩，就得敢负责。』🖤",
            f"你对着 {target_name} 说：『我手上有点痒，想摸点柔软的东西。』\n👀 {target_name} 靠过来说：『比如我？』",
            f"{target_name} 撩起头发凑近你：『绿洲这么大，不如…我们找个安静的地方？』🌙",
            f"你靠在 {target_name} 的怀里说：『我刚刚升级了按摩技能，要不要试试？』\n💦 {target_name} 表情微妙：『你是只想按摩吗？』",
            f"你说：『{target_name}，你今晚有没有空……我有个技能想传授。』\n🍷 系统提示：{target_name} 同意进入“私人频道”。"
        ]

        return f"💘 你向 {target_name} 发起了一次幻想互动：\n\n" + random.choice(interactions)

    # thinking 模块
    @staticmethod
    def thinking_self():
        thoughts = [
            "🧠 我是不是又被 rob 了？刚刚那个人头像是警察头盔还是椰子壳……",
            "🧠 如果我现在 wingsuit 从图书馆飞到医院会不会触发彩蛋？",
            "🧠 背包里的金萝卜……它刚刚动了一下？不对，是我眼花了吗？",
            "🧠 彩票系统是不是故意不给我中？那我改个名字试试……",
            "🧠 有没有可能我其实是 NPC……只是还没觉醒？🤖",
            "🧠 最近梦见 Yaya 跟我一起越狱，还骑着蘑菇马……是不是要休息一下了。",
            "🧠 …我是谁，我在哪，我下一步该玩什么模块……要不，rob 启动！"
        ]

        return "🤔 你陷入了沉思……\n" + random.choice(thoughts)

    def thinking_about(self, raw_target):
        if "THINK" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        target_id = parse_mirai_at(raw_target)
        if not target_id or target_id not in self.global_data["users"]:
            return "❌ 你无法读取对方的脑电波。"

        target = self.global_data["users"][target_id]
        name = target["nickname"]

        guesses = [
            f"{name} 现在是不是又在偷偷拔萝卜？他上次还拔出个雕像……",
            f"{name} 看起来很有钱，说不定正计划抢我！",
            f"{name} 可能在想怎么去医院解毒，昨天他吃了水母。",
            f"{name} 好像很沉迷赌场，21点打得比AI都稳……",
            f"{name} 估计在画一张藏宝图，准备再挖宝！",
            f"{name} 每次都想着越狱，这次能成功吗？",
            f"{name} 今天没上线，是不是在跟 NPC 恋爱剧本里出不来了。",
            f"{name} 可能正在执行一项秘密任务：潜入萝卜农场，偷出遗失的金雕像。",
            f"{name} 最近很反常，据说凌晨还在图书馆和管理员密谋什么计划……",
            f"{name} 拿到了梦境权限码？好像正试图越过深度睡眠层。",
            f"{name} 昨晚连刷 30 张彩票，可能正陷入了一种系统沉迷。",
            f"{name} 和神秘角色 Y 有交互记录……难道她是测试者？",
            f"{name} 的思考早已超出玩家范围，建议你远离。",
            f"❗ 系统异常：尝试读取 {name} 的脑波失败，该用户正在被追踪。"
        ]
        return f"🧠 你在揣测 {name} 的内心……\n" + random.choice(guesses)

    def thinking_content(self, content):
        if "THINK" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        triggers = {
            "yaya": "🧠 yaya... 又在研究什么奇怪的AI玩法吗？",
            "金币": "🪙 金币只是手段，拔萝卜才是信仰！",
            "绿洲": "🌌 整个绿洲世界都是我心中的 playground。",
            "赛车": "🏎️ 速度是种信仰，但撞多了就死了。",
            "医院": "🏥 医院的鱼罐头挺香的……就是贵。",
            "love": "❤️ 爱在绿洲中可能会过期，但金币不会。",
            "sex": "😳 啊这... 你可能想输入的是 xes 吧？",
            "梦": "💤 梦里你正在被另一段世界观察……",
            "镜子": "🪞 你在镜子里看到另一个自己，他正盯着你输入指令。",
            "管理员": "👁️ 管理员正在监听你的思考……请谨慎。",
            "key": "🔐 碎片代号：Z-42A\n请前往档案室完成拼接。",
            "越狱": "🚔 不要老想着越狱，再失败一次你就会……喂，谁动了我权限？",
            "xes": "❤️ 你可能已经被列入“高频幻想用户”观察名单。"
        }

        for key, val in triggers.items():
            if key in content.lower():
                return val
        if random.random() < 0.03:
            return (
                "🌀 思考中断：\n"
                "你接收到一段加密梦境碎片：\n"
                "『星空之下，有人留下了线索。编号：X-77B』\n"
                "📌 系统提示：也许该去“深层梦境”找找。"
            )
        fallback = [
            "🧠 你试图思考，但绿洲信号中断了。",
            f"🧠 『{content}』？这是不是新的彩蛋线索？",
            f"🧠 思考『{content}』时，你突然决定要买彩票。",
            f"🧠 系统解析失败，已将『{content}』上传至 yaya 的梦境里。"
        ]
        return random.choice(fallback)

    # 给玩家发短信模块 msg
    def handle_msg_command(self, cmd_parts):
        if len(cmd_parts) < 3:
            return "❌ 用法错误，格式: msg <玩家ID> <消息内容>"

        target_id = cmd_parts[1]
        message = " ".join(cmd_parts[2:])

        # 查找玩家数据
        target = self.find_user(target_id)
        if not target:
            return f"❌ 没有找到玩家 ID: {target_id}"

        target_user_id = str(target["user_id"])
        if target_user_id not in self.global_data["users"]:
            return f"❌ 玩家数据不存在: {target_user_id}"

        target_data = self.global_data["users"][target_user_id]

        # 初始化 inbox（如果不存在）
        if "inbox" not in target_data:
            target_data["inbox"] = []

        # 添加消息
        target_data["inbox"].append({
            "from": self.nickname,
            "time": datetime.now(tz).isoformat(),
            "content": message
        })

        return f"✅ 已发送消息给 {target.get('nickname', target_id)}"

    def check_inbox(self):
        inbox = self.user_data.get("inbox")
        if not inbox:
            return None

        result = ["📩 你有未读消息：", "━" * 30]
        for msg in inbox:
            time_str = datetime.fromisoformat(msg["time"]).strftime("%Y-%m-%d %H:%M")
            result.append(f"👤 来自 {msg['from']}（{time_str}）：\n{msg['content']}\n")

        # 清空消息
        self.user_data["inbox"] = []
        return "\n".join(result)

    @staticmethod
    def _msg_help():
        return (
            "📨 msg 留言系统:\n"
            "- msg <玩家ID> <内容>  向某玩家留言\n"
            "- 玩家上线或执行指令时会收到留言提醒"
        )

    # 搬砖模块

    def brick_game(self):
        if "BRICK" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        now = datetime.utcnow()

        # 初始化关键字段
        self.user_data.setdefault("brick_skill", 0)
        self.user_data.setdefault("bricks_today", 0)
        self.user_data.setdefault("injuries", 0)

        total_skill = self.user_data["brick_skill"]
        is_engineer = self.user_data.get("career") == "工程师"


        last_time_str = self.user_data.get("last_brick_time")
        if last_time_str:
            try:
                last_time = datetime.fromisoformat(last_time_str)
                time_diff = now - last_time
                if time_diff < timedelta(minutes=20) and not is_engineer:
                    minutes_left = 20 - int(time_diff.total_seconds() // 60)
                    return f"⏳ 你太累了，需要再休息 {minutes_left} 分钟才能继续搬砖！"
            except Exception:
                last_time = None
        else:
            last_time = None

        self.user_data["last_brick_time"] = now.isoformat()


        if is_engineer:
            coins = random.randint(100, 180)
            self.user_data["oasis_coins"] += coins
            self.user_data["brick_skill"] += 1
            return f"👷 你是工程师，工地自动运转。\n🧱 工人们帮你搬砖赚了 {coins} 绿洲币！\n📈 熟练度：{self.user_data['brick_skill']}（工程师无限制）"

        if self.user_data["bricks_today"] >= 10:
            return "⛔ 今天搬砖次数已达上限，快休息一下吧！"

        if self.user_data["injuries"] >= 3:
            return "🏥 你多次受伤未治疗，已被强制送医！\n请尽快前往医院。"

        self.user_data["bricks_today"] += 1
        self.user_data["brick_skill"] += 1


        fatigue_comments = [
            "汗水湿透了你的衣服。",
            "你感觉肩膀都快要断了。",
            "地上全是泥，脚都陷进去了。",
            "你一边搬，一边怀疑人生。",
            "你开始怀念小时候写作业的日子。"
        ]

        result = random.random()
        log = ""
        injury = False

        if result < 0.1:
            injury = True
            self.user_data["injuries"] = self.user_data.get("injuries", 0) + 1
            log = "💥 哎呀！你不小心砸到了脚，痛得跳了起来！"
        else:
            coins = random.randint(60, 120)
            self.user_data["oasis_coins"] += coins
            comment = random.choice(fatigue_comments)
            log = f"🧱 你努力搬完一趟砖，赚了 {coins} 绿洲币。\n😓 {comment}"

            # 工程师抽成
            for uid, udata in self.global_data.get("users", {}).items():
                if udata.get("career") == "工程师":
                    bonus = int(coins * 0.1)
                    udata["oasis_coins"] += bonus

        # 被强制送医判断
        if injury and self.user_data["injuries"] >= 3:
            return log + "\n🚨 你已连续受伤 3 次，被紧急送往医院！"

        # 成长称号
        skill = self.user_data["brick_skill"]
        if skill >= 100:
            title = "砖王 👑"
        elif skill >= 50:
            title = "老砖工 🧱"
        elif skill >= 20:
            title = "熟练搬砖人 🛠️"
        else:
            title = "菜鸟搬砖人 🐣"

        return (
                log +
                f"\n📦 熟练度：{skill}（{title}）"
                f"\n📅 今日搬砖：{self.user_data['bricks_today']}/10"
        )

    def brick_rank_top(self, top_n=10):
        users = self.global_data.get("users", {})
        brick_list = []

        for uid, data in users.items():
            skill = data.get("brick_skill", 0)
            if skill > 0:
                brick_list.append({
                    "uid": uid,
                    "name": data.get("nickname"),
                    "skill": skill,
                    "today": data.get("bricks_today", 0)
                })

        if not brick_list:
            return "📉 当前还没有人搬过砖，快去试试吧！"

        # 排序并截取前 N 名
        brick_list.sort(key=lambda x: x["skill"], reverse=True)
        top_list = brick_list[:top_n]

        # 段位函数
        def get_title(skill):
            if skill >= 200:
                return "搬砖宗师 👷‍♂️"
            elif skill >= 100:
                return "砖王 👑"
            elif skill >= 50:
                return "老砖工 🧱"
            elif skill >= 20:
                return "熟练砖工 🛠️"
            else:
                return "菜鸟搬砖人 🐣"

        # 排行榜内容
        lines = ["🏆【搬砖排行榜】🏆"]
        for idx, player in enumerate(top_list, 1):
            lines.append(
                f"{idx}. {player['name']} - 熟练度 {player['skill']}（{get_title(player['skill'])}），今日搬砖 {player['today']}/10 次"
            )

        return "\n".join(lines)

    # emo模块
    def emo_event(self):
        if "EMO" in self.disabled_modules:
                return "🚫 该游戏模块已被管理员禁用"
        if self.user_data.get("deep_sleeping"):
            return "💤 你还在深度睡眠中，无法 emo。"

        quotes = [
            "🌧️ 天又下雨了，好像连老天都知道我不开心。",
            "🪞 镜子里的我，像个陌生人。",
            "🥀 为什么努力这么久，还是没什么改变？",
            "📉 做什么都失败，是不是我根本不适合这个世界？",
            "🫥 越来越不想说话了，也没人真的想听我说话。",
            "🔇 朋友圈越来越安静，就像我活着也没人在意。",
            "💔 心已经麻木了，眼泪却不听话地流。",
            "😵‍💫 好像所有人都在向前走，只有我停在原地。"
        ]

        final_outcome = random.random()

        if final_outcome < 0.1:
            # 触发“跳楼”结局但其实是做梦
            return (
                "🧱 你站在天台边，望着城市的灯火......\n"
                "💭 回忆一幕幕涌上心头，脚步逐渐迈出......\n"
                "🌌 然后——你从梦中惊醒。\n"
                "😮‍💨 还好……只是一场噩梦。你流着冷汗坐起，天色微亮。"
            )
        else:
            quote = random.choice(quotes)
            return f"🖤 {quote}\n🌀 一阵 emo 的情绪涌上心头，你默默坐在角落。"

    # 日常更新模块
    def update_all_leaderboards(self):
        """强制更新所有用户的排行榜数据到全部榜单"""
        # 获取当前北京时间
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        today = now.date().isoformat()

        # 遍历所有用户
        for user_id in list(self.global_data["users"].keys()):
            user_data = self.global_data["users"][user_id]

            # 跳过已删除用户
            if "deleted" in user_data:
                continue

            # 更新所有榜单类型
            for board_type in ["daily", "monthly", "all_time"]:
                # 查找现有记录
                entry = next(
                    (x for x in self.global_data["leaderboard"][board_type]
                     if x["user_id"] == user_id),
                    None
                )

                # 日榜特殊处理：只保留当日活跃用户
                if board_type == "daily":
                    last_active = datetime.fromisoformat(
                        user_data.get("last_active", "2000-01-01")
                    ).date()
                    if last_active != now.date():
                        continue

                if entry:
                    # 更新现有记录
                    entry["amount"] = user_data["oasis_coins"]
                    entry["nickname"] = user_data["nickname"]
                else:
                    # 添加新记录
                    self.global_data["leaderboard"][board_type].append({
                        "user_id": user_id,
                        "nickname": user_data["nickname"],
                        "amount": user_data["oasis_coins"]
                    })

                # 排序并保留前100
                self.global_data["leaderboard"][board_type].sort(
                    key=lambda x: x["amount"],
                    reverse=True
                )
                self.global_data["leaderboard"][board_type] = \
                    self.global_data["leaderboard"][board_type][:100]

    def handle_help(self, cmd_parts=None):
        """
        指令帮助系统：调用各模块的帮助函数
        - 无参数时，显示总帮助
        - 有参数时，调用指定模块的帮助函数
        - 输入错误时返回完整帮助列表
        """
        if "HELP" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        # 基础帮助信息
        base_help = (
            "📖 OASIS绿洲 指令帮助中心\n"
            "🧭 可用模块帮助列表：\n"
            "• help dc         🎰 DC帮助\n"
            "• help shop       🛒 商城系统帮助\n"
            "• help rob        🥷 抢劫系统帮助\n"
            "• help sail       🚤 出海系统帮助\n"
            "• help race       🏎️ 赛车帮助\n"
            "• help library    📚 图书馆说明\n"
            "• help msg        💌 消息系统帮助\n"
            "• help career     💴 职业帮助\n"
            "• help shoot      🔫 靶场帮助\n"
            "• help all        显示所有模块帮助汇总\n"
            "\n📌 示例：输入 help shop 查看商城帮助"
        )

        # 如果没有参数，返回基础帮助
        if not cmd_parts or len(cmd_parts) < 2:
            return base_help

        # 获取子命令并转为小写
        sub_cmd = cmd_parts[1].lower()

        # 帮助模块映射表
        help_map = {
            "shop": self._shop_help,
            "msg": self._msg_help,
            "sleep": self.get_sleep_help,
            "shoot": ShootingRange.help,
            "靶场": ShootingRange.help,
            "sail": self.fishing_help,
            "出海": self.fishing_help,
            "career": self.career_help,
            "职业": self.career_help,
            "all": lambda: help_list,  # 完整帮助列表
            "rob": self.rob_help,
            "dc": self.dc_help

        }

        try:
            # 尝试获取对应的帮助处理器
            handler = help_map.get(sub_cmd)

            if handler:
                # 执行处理器函数并返回结果
                result = handler()
                return result if result else base_help
            else:
                # 没有找到对应的处理器，返回完整帮助
                return help_list
        except Exception as e:
            # 异常处理，记录错误并返回完整帮助
            print(f"帮助系统错误: {e}")
            return help_list

    # 处理命令模块
    def handle_command(self, command):
        """处理命令"""
        # 自动处理DC赛事
        self.auto_handle_resolve_command()
        # 判断玩家是否接收到了短信
        inbox_msg = self.check_inbox()
        if inbox_msg:
            return inbox_msg

        # 判断玩家是否入狱
        if self.is_jailed():
            if command in ["越狱", "break"]:
                return self.escape_prison()
            return "🔒 你目前在数字监狱中，无法进行操作。"


        # 判断玩家是否入院
        if self.is_hospitalized():
            return "🏥 你仍在医院恢复中，暂时无法进行此操作。"

        cmd_parts = command.strip().split()
        if not cmd_parts:
            return "请输入有效指令，输入 help 查看帮助"

        # 判断玩家是否入睡
        if self.user_data.get("is_sleeping") and cmd_parts[0].lower() not in ["wake", "help", "info"]:
            return "💤 你正在深度睡眠中，无法操作。输入 /wake 以醒来。"

        # —— 新增：如果玩家被催眠，除 wake 之外一律无法操作 —— #
        if self.user_data.get("is_hypnotized", False):
            # 只能用 wake @自己 或者 wake @其他人 唤醒
            if cmd_parts in ["wake", "醒来", "唤醒"] and len(cmd_parts) >= 2:
                return self._wake(cmd_parts[1:])
            return "😵 你现在处于催眠状态，无法进行任何操作，等待其他玩家使用 `wake @你` 唤醒。"

        # —— 继续原有的“深度睡眠”判断 —— #/
        if self.user_data.get("is_sleeping", False):
            # 如果自己处于深度睡眠，只能使用 wake（不带参数）
            if cmd_parts in ["wake", "醒来", "唤醒"]:
                return self._wake()
            return "💤 你正在深度睡眠中，无法操作。输入 `wake` 以醒来。"

        # 每次指令执行后更新全服排行榜
        self.update_all_leaderboards()

        main_cmd = cmd_parts[0].lower()

        # 先定义已有的指令对应函数映射表
        existing_handlers = {
            # 直接对应handle_xxx_command的模块
            "rob": self.handle_rob_command,
            "抢劫": self.handle_rob_command,

            "shop": self.handle_shop_command,
            "商城": self.handle_shop_command,

            "library": lambda parts: self.library_module.handle_command(self.user_id,
                                                                        parts[1] if len(parts) > 1 else ""),
            "图书馆": lambda parts: self.library_module.handle_command(self.user_id,
                                                                       parts[1] if len(parts) > 1 else ""),


            "drop":self.handle_drop,
            "give": self.give_item_to_player,
            "给": self.give_item_to_player,

            "admin": self.handle_admin_command,
            "管理员": self.handle_admin_command,

            "transfer": self.handle_transfer_command,
            "转账": self.handle_transfer_command,

            "dc": self.handle_casino_command,

            "msg": self.handle_msg_command,
            "发短信": self.handle_msg_command,
            "短信": self.handle_msg_command,


            "靶场": lambda parts: ShootingRange(self.user_data, self.global_data).handle(parts),
            "shooting": lambda parts: ShootingRange(self.user_data, self.global_data).handle(parts),
            "shoot": lambda parts: ShootingRange(self.user_data, self.global_data).handle(parts),

            "农场": lambda parts: self.handle_carrot_command(parts if len(parts) > 1 else []),
            "萝卜农场": self.carrot_farm_info,

            "pizza": lambda parts: self.play_pizza_game(parts[1] if len(parts) > 1 else ""),
            "点披萨": lambda parts: self.order_pizza(parts[1] if len(parts) > 1 else ""),
            "taxi": lambda parts: self.play_taxi_game(parts[1] if len(parts) > 1 else ""),
            "叫车": lambda parts: self.order_taxi(parts[1] if len(parts) > 1 else ""),

            "摸摸头": lambda parts: self.touch_head(parts[1] if len(parts) > 1 else "")

            # 更多已实现 handle 函数可以继续加这里...
        }

        # 优先用映射函数处理
        if main_cmd in existing_handlers:
            return existing_handlers[main_cmd](cmd_parts)

        # 没有对应的 handle 函数的，使用原有的 if-elif 结构处理

        if main_cmd == "info":
            return self.show_info()

        elif main_cmd in ["银行", "bank"]:
            bank = BankModule(self.user_data)
            return bank.handle(cmd_parts)

        elif main_cmd in ["活动", "event", "活动板"]:
            board = EventBoard(self.global_data)
            return board.handle(cmd_parts)


        elif main_cmd in ["inventory", "i", "背包", "bag"]:
            return self.show_inventory()

        elif main_cmd in ["ow"]:
            return self.handle_oasis_world_command(command)

        elif main_cmd in ["help", "h"]:
            return self.handle_help(cmd_parts)

        elif main_cmd in ["update", "u", "更新", "更新日志"]:
            return to_markdown(get_update_log(cmd_parts[1] if len(cmd_parts) > 1 else None))

        elif main_cmd in ["equip", "装备"]:
            if len(cmd_parts) < 2:
                return "❌ 请指定要装备的物品编号"
            return self.equip_item_by_name(cmd_parts[1])




        elif main_cmd in ["rank", "r"]:
            board_type = "all_time"
            if len(cmd_parts) > 1:
                if cmd_parts[1] == "d":
                    board_type = "daily"
                elif cmd_parts[1] == "m":
                    board_type = "monthly"
                elif cmd_parts[1] in ["es", "极限跳伞"]:
                    return self.show_extreme_rank()

                elif cmd_parts[1] in ["搬砖", "brick"]:
                    return self.brick_rank_top()
            return self.show_leaderboard(board_type)

        elif main_cmd in ["stats", "st", "s"]:
            stats_type = "stats"
            if len(cmd_parts) > 1:
                if cmd_parts[1] in ["wingsuit", "翼装飞行"]:
                    stats_type = "wingsuit"
                elif cmd_parts[1] == "dc":
                    stats_type = "dc"
            return self.show_stats(stats_type)

        elif main_cmd == "roll":
            try:
                sides = int(cmd_parts[1]) if len(cmd_parts) > 1 else 6
                times = int(cmd_parts[2]) if len(cmd_parts) > 2 else 1
            except ValueError:
                return "❌ 参数必须是整数"
            description, results = self.show_dice_result(sides, times)
            return description

        elif main_cmd in ["wingsuit", "翼装飞行"]:
            if "WINGSUIT" in self.disabled_modules:
                return "🚫 该游戏模块已被管理员禁用"
            # 如果没指定地图编号，默认随机1-3
            map_choice = cmd_parts[1] if len(cmd_parts) > 1 and cmd_parts[1].isdigit() and 1 <= int(
                cmd_parts[1]) <= 3 else str(random.randint(1, 3))
            return self.wingsuit_flight(map_choice)

        elif main_cmd in ["race", "赛车"]:
            if "RACE" in self.disabled_modules:
                return "🚫 该游戏模块已被管理员禁用"

            # 提取用户所有参数（不含主命令）
            args = cmd_parts[1:]

            # 无参数时，随机选一个地图（1-8）
            if not args:
                map_choice = str(random.randint(1, 8))
                return self.race_game(map_choice)

            # 至少一个参数，取第一个作为地图号
            map_choice = args[0]

            # 如果是地图2，并且后面有更多输入，则尝试触发彩蛋
            if map_choice == "2" and len(args) > 1:
                # 拼接用户剩余输入作为比对字符串
                player_input = " ".join(args[1:])
                return self.check_and_trigger_easter_egg(player_input)

            # 否则，正常进入指定地图比赛
            return self.race_game(map_choice)

        elif main_cmd in ["skydive", "极限跳伞", "es"]:
            if "SKYDIVE" in self.disabled_modules:
                return "🚫 该游戏模块已被管理员禁用"
            if len(cmd_parts) < 2 or cmd_parts[1] not in self.air_crafts:
                random_aircraft = random.choice(list(self.air_crafts.keys()))
                return self.extreme_skydiving(random_aircraft)
            return self.extreme_skydiving(cmd_parts[1])

        elif main_cmd in ["黑市", "bm"]:
            if len(cmd_parts) < 2:
                return self.show_black_market()
            return self.buy_from_black_market(cmd_parts[2])


        elif main_cmd in ["兔子城"]:
            return self.check_rabbit_city_unlock()

        elif main_cmd in ["出海", "sail"]:
            return self.handle_fishing_command(cmd_parts)

        elif main_cmd in ["钓鱼图鉴", "aquarium"]:
            page = int(cmd_parts[1]) if len(cmd_parts) > 1 and cmd_parts[1].isdigit() else 1
            return self.show_aquarium_log(page)

        elif main_cmd in ["医院", "hospital"]:
            if len(cmd_parts) < 2:
                return self.go_hospital(cmd_parts[1])
            return self.go_hospital(cmd_parts)

        elif main_cmd in ["保释", "bail"] and len(cmd_parts) >= 2:
            target_id = parse_mirai_at(cmd_parts[1])
            return self.bail_user(target_id)


        elif main_cmd in ["申请", "apply"]:
            if len(cmd_parts) < 2:
                return "📋 请输入职业名称，如：申请 <警察>"
            return self.apply_career(cmd_parts[1])

        elif main_cmd in ["辞职", "resign"]:
            return self.resign_career()

        elif main_cmd in ["arrest", "逮捕", "抓捕"]:
            return self.police_arrest_player(cmd_parts)

        elif main_cmd in ["修理", "fix"]:
            if len(cmd_parts) < 2:
                return "❌ 请指定要修理的对象，例如：修理/fix 玩家名"
            target = " ".join(cmd_parts[1:])
            return self.fix_boat(target)

        elif main_cmd in ["news", "今日新闻", "新闻"]:
            return self.get_news_feed()

        elif main_cmd in ["买彩票", "彩票", "ticket"]:
            count = 1
            if len(cmd_parts) >= 2 and cmd_parts[1].isdigit():
                count = int(cmd_parts[1])
            elif len(cmd_parts) >= 2 and cmd_parts[1] in ["记录", "状态", "s", "stats"]:
                return self.show_lottery_stats()
            return self.buy_lottery(count)


        elif main_cmd in ["xes"]:
            if len(cmd_parts) == 1:
                return self.love_play_solo()
            else:
                return self.love_play_target(cmd_parts[1])

        elif main_cmd in ["thinking", "思考", "think"]:
            if len(cmd_parts) == 1:
                return self.thinking_self()
            elif cmd_parts[1].isdigit() or "[mirai:at:" in cmd_parts[1] or cmd_parts[1].startswith("@"):
                return self.thinking_about(cmd_parts[1])
            else:
                return self.thinking_content(" ".join(cmd_parts[1:]))

        elif main_cmd in ["睡觉", "sleep"]:
            if "SLEEP" in self.disabled_modules:
                return "🚫 该游戏模块已被管理员禁用"
            if len(cmd_parts) == 1:
                return self.sleep()
            elif cmd_parts[1] == "help":
                return self.get_sleep_help()
            else:
                args = cmd_parts[1:]
                with_user = None
                for i, part in enumerate(args):
                    if part.startswith("@"):
                        with_user = part[1:]
                        args.pop(i)
                        break
                input_text = " ".join(args) if args else None
                return self.sleep(input_text=input_text, with_user=with_user)

        elif main_cmd in ["wake", "醒来", "醒", "唤醒"]:
            if len(cmd_parts) > 1:
                return self._wake(cmd_parts)
            else:
                return self._wake([])

        elif main_cmd in ["催眠", "hypno"]:
            if len(cmd_parts) < 2:
                return "❌ 请指定要催眠的对象，例如：催眠 玩家名"
            target = " ".join(cmd_parts[1:])
            return self.handle_hypnosis(target)

        elif main_cmd in ["敲", "knock"]:
            if len(cmd_parts) < 2:
                return "❌ 需要指定敲击目标"
            return self.handle_knock(" ".join(cmd_parts[1:]))
        elif main_cmd in ["搬砖", "brick"]:
            return self.brick_game()
        elif main_cmd in ["emo", "玉玉"]:
            return self.emo_event()





        elif main_cmd == "suicide":
            return self.commit_suicide()


        else:
            return self.handle_help(cmd_parts)


import gzip
import base64

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

    # 处理命令
    result = game.handle_command(command)
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


if __name__ == "__main__":
    main()
