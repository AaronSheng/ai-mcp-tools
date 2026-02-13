import subprocess
from typing import Dict, Any, Optional

from app.mcp import mcp
from app.common.logging import logger

@mcp.tool()
async def add_apple_notes(
    title: str,
    content: str,
    folder_name: Optional[str] = None
) -> Dict[str, Any]:
    """写入苹果备忘录 ⭐ 系统集成工具

    将指定内容写入苹果备忘录应用。
    支持自定义标题和指定文件夹。

    适用场景：
    - 快速记录重要信息
    - AI助手生成的内容保存
    - 自动化笔记创建
    - 任务提醒设置

    Args:
        title: 备忘录标题
        content: 备忘录内容（支持多行文本）
        folder_name: 目标文件夹名称（可选），如果不指定则使用默认文件夹

    Returns:
        操作结果:
        {
            "success": True,                   # 操作是否成功
            "note_id": "unique_identifier",    # 备忘录唯一标识符（如果有）
            "title": "备忘录标题",
            "folder": "文件夹名称",             # 实际使用的文件夹
            "created_at": "2024-01-01 10:00:00",
            "message": "备忘录创建成功"
        }

    Examples:
        # 创建简单备忘录
        result = await write_to_apple_notes(
            title="会议要点",
            content="今天讨论了项目进度和下一步计划"
        )
        
        # 指定文件夹创建备忘录
        result = await write_to_apple_notes(
            title="购物清单",
            content="- 牛奶\\n- 面包\\n- 水果",
            folder_name="个人"
        )
        
        # 创建多段落备忘录
        result = await write_to_apple_notes(
            title="学习笔记",
            content="今天学习了MCP协议\\n\\n主要内容：\\n1. 协议基础\\n2. 工具注册\\n3. 数据传输"
        )
    """
    try:
        logger.info(f"MCP Tool called: write_to_apple_notes (title={title})")
        
        # 验证输入参数
        if not title or not title.strip():
            return {
                "success": False,
                "error": "标题不能为空",
                "message": "请提供有效的备忘录标题"
            }
        
        if not content or not content.strip():
            return {
                "success": False,
                "error": "内容不能为空",
                "message": "请提供有效的备忘录内容"
            }
        
        # 构造AppleScript命令
        # 使用osascript来与Notes应用交互
        applescript_commands = []
        
        # 基础命令：激活Notes应用并创建新笔记
        applescript_commands.append('tell application "Notes"')
        applescript_commands.append('    activate')
        
        # 如果指定了文件夹，先切换到该文件夹
        if folder_name and folder_name.strip():
            applescript_commands.append(f'    tell account 1')
            applescript_commands.append(f'        set targetFolder to folder "{folder_name.strip()}"')
            applescript_commands.append('    end tell')
            folder_used = folder_name.strip()
        else:
            # 使用默认文件夹
            applescript_commands.append('    tell account 1')
            applescript_commands.append('        set targetFolder to folder "Notes"')
            applescript_commands.append('    end tell')
            folder_used = "Notes"
        
        # 创建新笔记
        escaped_title = title.replace('"', '\\"')
        escaped_content = content.replace('"', '\\"').replace('\n', '\\n')
        
        applescript_commands.append('    tell targetFolder')
        applescript_commands.append(f'        set newNote to make new note with properties {{name:"{escaped_title}", body:"{escaped_content}"}}')
        applescript_commands.append('    end tell')
        applescript_commands.append('end tell')
        
        # 组合完整的AppleScript
        full_script = '\n'.join(applescript_commands)
        
        logger.debug(f"Executing AppleScript: {full_script}")
        
        # 执行AppleScript
        try:
            result = subprocess.run(
                ['osascript', '-e', full_script],
                capture_output=True,
                text=True,
                timeout=30  # 30秒超时
            )
            
            if result.returncode == 0:
                # 成功创建备忘录
                import datetime
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    "success": True,
                    "title": title,
                    "folder": folder_used,
                    "created_at": current_time,
                    "message": f"备忘录 '{title}' 已成功创建到 '{folder_used}' 文件夹"
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                logger.error(f"AppleScript execution failed: {error_msg}")
                
                # 尝试更简单的备选方案
                return await _fallback_create_note(title, content, folder_used)
                
        except subprocess.TimeoutExpired:
            logger.error("AppleScript execution timed out")
            return {
                "success": False,
                "error": "操作超时",
                "message": "创建备忘录超时，请稍后重试"
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
        logger.error(f"write_to_apple_notes failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "写入苹果备忘录失败"
        }


async def _fallback_create_note(title: str, content: str, folder_name: str) -> Dict[str, Any]:
    """备选方案：使用更简单的AppleScript命令"""
    try:
        # 更简单的备选脚本
        fallback_script = f'''
        tell application "Notes"
            activate
            tell account 1
                set newNote to make new note with properties {{name:"{title.replace('"', '\\"')}", body:"{content.replace('"', '\\"').replace(chr(10), "\\n")}"}}
            end tell
        end tell
        '''
        
        result = subprocess.run(
            ['osascript', '-e', fallback_script],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if result.returncode == 0:
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "success": True,
                "title": title,
                "folder": "默认文件夹",
                "created_at": current_time,
                "message": f"备忘录 '{title}' 已创建（使用默认文件夹）"
            }
        else:
            error_detail = result.stderr.strip() if result.stderr else "备选方案也失败"
            return {
                "success": False,
                "error": "创建失败",
                "message": f"无法创建备忘录: {error_detail}",
                "details": "请确保Notes应用已安装并可访问"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "备选方案执行失败"
        }