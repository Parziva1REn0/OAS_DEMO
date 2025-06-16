from library_module import LibraryModule
import json
import random
from collections import Counter
from datetime import datetime, timedelta, time
import pytz
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
    match = re.search(r'\[mirai:at:(\d+)]', message)
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




tz = pytz.timezone('Asia/Shanghai')

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


        # 摸摸头成人模块
        self.global_data.setdefault("config", {}).setdefault("adult_mode", False)


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
        self.user_data["status"].setdefault("poison", False)
        self.user_data["status"].setdefault("in_jailed", None)  # None 表示未入狱


        # 商城售卖系统初始化
        if "marketplace" not in self.global_data:
            self.global_data["marketplace"] = {
                "items": [],  # 所有在售物品
                "transactions": []  # 交易记录
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

    # ————————————————————管理员 功能模块————————————————————

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



    # 医院治疗模块
    def go_hospital(self, cmd_parts):
        if "HOSPITAL" in self.disabled_modules:
            return "🚫 该模块已被管理员禁用"
        if cmd_parts[1] in ["rescue", "援助", "救"]:
            return self.rescue_from_hospital(cmd_parts[2])
        if not self.user_data["status"].get("poison", False):
            return "🏥 医生摇头：你目前身体健康，无需治疗。"

        cure_cost = 200
        if self.user_data["oasis_coins"] < cure_cost:
            return f"💸 治疗费用为 {cure_cost} 绿洲币，你的余额不足，无法解毒！"

        self.user_data["oasis_coins"] -= cure_cost
        self.user_data["status"]["poison"] = False

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

            "msg": self._msg_help,
            "sleep": self.get_sleep_help,
            "career": self.career_help,
            "职业": self.career_help,
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
                return None
        except Exception as e:
            return None

