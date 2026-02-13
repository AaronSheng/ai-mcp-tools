import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

from app.mcp import mcp
from app.common.logging import logger

@mcp.tool()
async def add_apple_calendar_event(
    title: str,
    start_date: str,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    calendar_name: Optional[str] = None,
    all_day: bool = False
) -> Dict[str, Any]:
    """添加苹果日历事件 ⭐ 日程管理工具

    在苹果日历中创建新的日程事件。
    支持设置标题、时间、地点、备注等详细信息。

    适用场景：
    - AI助手自动创建会议安排
    - 任务提醒设置
    - 重要日期记录
    - 日程自动化管理

    Args:
        title: 事件标题（必需）
        start_date: 开始时间，格式："YYYY-MM-DD HH:MM" 或 "YYYY-MM-DD"（全天事件）
        end_date: 结束时间，格式同start_date（可选，如不提供则为1小时事件）
        location: 事件地点（可选）
        notes: 事件备注/描述（可选）
        calendar_name: 目标日历名称（可选），如不指定则使用默认日历
        all_day: 是否为全天事件，默认False

    Returns:
        操作结果:
        {
            "success": True,                   # 操作是否成功
            "event_id": "unique_identifier",   # 事件唯一标识符（如果有）
            "title": "事件标题",
            "start_time": "2024-01-01 10:00:00",
            "end_time": "2024-01-01 11:00:00",
            "calendar": "日历名称",
            "created_at": "2024-01-01 10:00:00",
            "message": "日程事件创建成功"
        }

    Examples:
        # 创建简单会议
        result = await add_apple_calendar_event(
            title="团队周会",
            start_date="2024-01-15 14:00",
            end_date="2024-01-15 15:00"
        )
        
        # 创建全天事件
        result = await add_apple_calendar_event(
            title="项目截止日期",
            start_date="2024-01-20",
            all_day=True,
            notes="重要项目交付 deadline"
        )
        
        # 指定日历和详细信息
        result = await add_apple_calendar_event(
            title="客户拜访",
            start_date="2024-01-16 09:30",
            end_date="2024-01-16 11:30",
            location="客户公司地址",
            notes="准备产品演示材料",
            calendar_name="工作"
        )
        
        # 只指定开始时间（默认1小时）
        result = await add_apple_calendar_event(
            title="代码审查",
            start_date="2024-01-17 16:00"
        )
    """
    try:
        logger.info(f"MCP Tool called: add_apple_calendar_event (title={title})")
        
        # 验证必要参数
        if not title or not title.strip():
            return {
                "success": False,
                "error": "标题不能为空",
                "message": "请提供有效的事件标题"
            }
        
        if not start_date or not start_date.strip():
            return {
                "success": False,
                "error": "开始时间不能为空",
                "message": "请提供有效的开始时间"
            }
        
        # 解析时间格式
        try:
            if all_day or len(start_date.strip()) <= 10:  # YYYY-MM-DD 格式
                # 全天事件处理
                start_dt = datetime.strptime(start_date.strip()[:10], "%Y-%m-%d")
                start_formatted = start_dt.strftime("%Y-%m-%d")
                
                if end_date and end_date.strip():
                    end_dt = datetime.strptime(end_date.strip()[:10], "%Y-%m-%d")
                    end_formatted = end_dt.strftime("%Y-%m-%d")
                else:
                    # 全天事件默认结束时间为同一天
                    end_formatted = start_formatted
                    
                is_all_day = True
            else:
                # 普通事件处理
                start_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d %H:%M")
                start_formatted = start_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                if end_date and end_date.strip():
                    if len(end_date.strip()) <= 10:
                        # 结束日期格式为 YYYY-MM-DD
                        end_dt = datetime.strptime(end_date.strip()[:10], "%Y-%m-%d")
                        # 设置为当天结束时间
                        end_formatted = end_dt.strftime("%Y-%m-%d 23:59:59")
                    else:
                        # 完整时间格式
                        end_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d %H:%M")
                        end_formatted = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # 默认1小时事件
                    end_dt = start_dt.replace(hour=start_dt.hour + 1)
                    end_formatted = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                is_all_day = False
                
        except ValueError as e:
            return {
                "success": False,
                "error": "时间格式错误",
                "message": f"请使用正确的日期时间格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM。错误详情：{str(e)}"
            }
        
        # 构造AppleScript命令
        applescript_commands = []
        applescript_commands.append('tell application "Calendar"')
        applescript_commands.append('    activate')
        
        # 选择日历
        if calendar_name and calendar_name.strip():
            applescript_commands.append(f'    set targetCalendar to calendar "{calendar_name.strip()}"')
            calendar_used = calendar_name.strip()
        else:
            applescript_commands.append('    set targetCalendar to first calendar')
            calendar_used = "默认日历"
        
        # 转义特殊字符
        escaped_title = title.replace('"', '\\"')
        escaped_location = location.replace('"', '\\"') if location else ""
        escaped_notes = notes.replace('"', '\\"') if notes else ""
        
        # 创建事件命令
        if is_all_day:
            applescript_commands.append(f'    make new event at end of events of targetCalendar with properties {{summary:"{escaped_title}", start date:date "{start_formatted}", end date:date "{end_formatted}", allday event:true')
        else:
            applescript_commands.append(f'    make new event at end of events of targetCalendar with properties {{summary:"{escaped_title}", start date:date "{start_formatted}", end date:date "{end_formatted}"')
        
        # 添加可选属性
        if location and location.strip():
            applescript_commands.append(f', location:"{escaped_location}"')
        if notes and notes.strip():
            applescript_commands.append(f', description:"{escaped_notes}"')
            
        applescript_commands.append('}')
        applescript_commands.append('end tell')
        
        # 组合完整的AppleScript
        full_script = '\n'.join(applescript_commands)
        
        logger.debug(f"Executing AppleScript for Calendar: {full_script}")
        
        # 执行AppleScript
        try:
            result = subprocess.run(
                ['osascript', '-e', full_script],
                capture_output=True,
                text=True,
                timeout=30  # 30秒超时
            )
            
            if result.returncode == 0:
                # 成功创建日历事件
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    "success": True,
                    "title": title,
                    "start_time": start_formatted,
                    "end_time": end_formatted,
                    "calendar": calendar_used,
                    "all_day": is_all_day,
                    "created_at": current_time,
                    "message": f"日程事件 '{title}' 已成功创建到 '{calendar_used}'"
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                logger.error(f"AppleScript execution failed: {error_msg}")
                
                # 尝试备选方案
                return await _fallback_create_event(
                    title, start_formatted, end_formatted, 
                    location, notes, calendar_used, is_all_day
                )
                
        except subprocess.TimeoutExpired:
            logger.error("AppleScript execution timed out")
            return {
                "success": False,
                "error": "操作超时",
                "message": "创建日历事件超时，请稍后重试"
            }
        except FileNotFoundError:
            logger.error("osascript command not found")
            return {
                "success": False,
                "error": "系统不支持",
                "message": "当前系统不支持AppleScript（仅macOS可用）"
            }
        except Exception as e:
            logger.error(f"Subprocess error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "执行系统命令时发生错误"
            }
            
    except Exception as e:
        logger.error(f"add_apple_calendar_event failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "添加苹果日历事件失败"
        }


async def _fallback_create_event(
    title: str, 
    start_time: str, 
    end_time: str,
    location: Optional[str],
    notes: Optional[str],
    calendar_name: str,
    all_day: bool
) -> Dict[str, Any]:
    """备选方案：使用简化版AppleScript"""
    try:
        # 构造简化的AppleScript
        escaped_title = title.replace('"', '\\"')
        script_parts = [
            'tell application "Calendar"',
            '    activate',
            f'    make new event at end of events of first calendar with properties {{summary:"{escaped_title}"'
        ]
        
        # 添加时间信息
        if all_day:
            script_parts.append(f', start date:date "{start_time}", end date:date "{end_time}", allday event:true')
        else:
            script_parts.append(f', start date:date "{start_time}", end date:date "{end_time}"')
        
        # 添加可选信息
        if location:
            escaped_location = location.replace('"', '\\"')
            script_parts.append(f', location:"{escaped_location}"')
        if notes:
            escaped_notes = notes.replace('"', '\\"')
            script_parts.append(f', description:"{escaped_notes}"')
            
        script_parts.append('}')
        script_parts.append('end tell')
        
        fallback_script = '\n'.join(script_parts)
        
        result = subprocess.run(
            ['osascript', '-e', fallback_script],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if result.returncode == 0:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "success": True,
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "calendar": "默认日历",
                "all_day": all_day,
                "created_at": current_time,
                "message": f"日程事件 '{title}' 已创建（使用默认日历）"
            }
        else:
            error_detail = result.stderr.strip() if result.stderr else "备选方案也失败"
            return {
                "success": False,
                "error": "创建失败",
                "message": f"无法创建日历事件: {error_detail}",
                "details": "请确保日历应用已安装并可访问"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "备选方案执行失败"
        }