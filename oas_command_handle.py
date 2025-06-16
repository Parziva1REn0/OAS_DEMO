from oas import OASISGame
from oas import parse_mirai_at

class OasisCommandDispatcher(OASISGame):


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


            "library": lambda parts: self.library_module.handle_command(self.user_id,
                                                                        parts[1] if len(parts) > 1 else ""),
            "图书馆": lambda parts: self.library_module.handle_command(self.user_id,
                                                                       parts[1] if len(parts) > 1 else ""),

            "drop": self.handle_drop,
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



        elif main_cmd in ["inventory", "i", "背包", "bag"]:
            return self.show_inventory()


        elif main_cmd in ["help", "h"]:
            return self.handle_help(cmd_parts)


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




        elif main_cmd in ["黑市", "bm"]:
            if len(cmd_parts) < 2:
                return self.show_black_market()
            return self.buy_from_black_market(cmd_parts[2])



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


        elif main_cmd in ["搬砖", "brick"]:
            return self.brick_game()
        elif main_cmd in ["emo", "玉玉"]:
            return self.emo_event()


        elif main_cmd == "suicide":
            return self.commit_suicide()


        else:
            return self.handle_help(cmd_parts)
