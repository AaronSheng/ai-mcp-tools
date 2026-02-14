import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.mcp import mcp
from app.common.logging import logger

@mcp.tool()
async def search_knowledge_file(
    keywords: str,
    file_types: Optional[List[str]] = None,
    max_results: int = 20,
    search_content: bool = True,
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """查询本地知识库文件 ⭐ 知识检索工具

    在指定的知识库目录中搜索包含关键词的文件。
    支持文件名搜索和文件内容搜索，可按文件类型过滤。

    适用场景：
    - 知识库内容检索
    - 文档查找
    - 学习资料搜索
    - 项目文档定位

    Args:
        keywords: 搜索关键词（支持多个关键词，用空格分隔）
        file_types: 文件类型过滤列表，如 ['.md', '.txt', '.pdf']，默认None表示不限制
        max_results: 最大返回结果数，默认20
        search_content: 是否搜索文件内容，默认True
        case_sensitive: 是否区分大小写，默认False

    Returns:
        搜索结果:
        {
            "success": True,
            "query": "搜索关键词",
            "directory": "/path/to/knowledge/base",
            "total_files_scanned": 150,
            "matching_files": 12,
            "results": [
                {
                    "file_name": "example.md",
                    "file_path": "/path/to/example.md",
                    "file_size": 2048,
                    "file_type": ".md",
                    "modified_time": "2024-01-01 10:00:00",
                    "match_type": "filename_and_content",  # filename, content, both
                    "relevance_score": 0.85,  # 相关性评分 0.0-1.0
                    "matches": [
                        {
                            "type": "filename",
                            "matched_text": "example",
                            "position": 0
                        },
                        {
                            "type": "content",
                            "matched_text": "相关关键词",
                            "line_number": 15,
                            "context": "这是包含关键词的相关内容..."
                        }
                    ]
                }
            ],
            "message": "找到12个匹配文件"
        }

    Examples:
        # 基础搜索
        result = await search_knowledge_file("机器学习")
        
        # 指定文件类型搜索
        result = await search_knowledge_file(
            keywords="Python 编程",
            file_types=['.md', '.txt'],
            max_results=10
        )
        
        # 只搜索文件名（不搜索内容）
        result = await search_knowledge_file(
            keywords="教程",
            search_content=False
        )
        
        # 使用默认目录搜索
        result = await search_knowledge_file("项目文档")
    """
    try:
        logger.info(f"MCP Tool called: search_knowledge_file (keywords={keywords})")
        
        # 验证输入参数
        if not keywords or not keywords.strip():
            return {
                "success": False,
                "error": "关键词不能为空",
                "message": "请提供有效的搜索关键词"
            }
        
        # 解析关键词
        keyword_list = [kw.strip() for kw in keywords.split() if kw.strip()]
        if not keyword_list:
            return {
                "success": False,
                "error": "无效的关键词",
                "message": "请提供有效的搜索关键词"
            }
        
        # 检查目录是否存在
        directory_path = "/Users/bingosheng/Desktop/知识库"
        target_path = Path(directory_path).resolve()
        if not target_path.exists():
            return {
                "success": False,
                "error": "目录不存在",
                "message": f"指定的知识库目录不存在: {directory_path}"
            }
        
        if not target_path.is_dir():
            return {
                "success": False,
                "error": "路径不是目录",
                "message": f"指定路径不是目录: {directory_path}"
            }
        
        # 处理文件类型过滤
        if file_types:
            # 标准化文件扩展名
            normalized_types = []
            for ft in file_types:
                if not ft.startswith('.'):
                    ft = '.' + ft
                normalized_types.append(ft.lower())
            file_types = normalized_types
        
        # 准备搜索模式
        search_patterns = []
        for keyword in keyword_list:
            if case_sensitive:
                pattern = re.compile(re.escape(keyword))
            else:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            search_patterns.append((keyword, pattern))
        
        # 收集匹配的文件
        matching_files = []
        total_files_scanned = 0
        
        def scan_directory(current_path: Path, depth: int = 0):
            nonlocal total_files_scanned
            
            try:
                items = list(current_path.iterdir())
            except PermissionError:
                logger.warning(f"Permission denied: {current_path}")
                return
            
            for item in items:
                # 检查是否超出最大结果限制
                if len(matching_files) >= max_results:
                    return
                
                try:
                    # 跳过隐藏文件和目录
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        total_files_scanned += 1
                        
                        # 文件类型过滤
                        if file_types and item.suffix.lower() not in file_types:
                            continue
                        
                        # 检查文件是否匹配
                        file_matches = _check_file_matches(
                            item, keyword_list, search_patterns, 
                            search_content, case_sensitive
                        )
                        
                        if file_matches:
                            file_info = _get_file_info(item, file_matches)
                            matching_files.append(file_info)
                    
                    elif item.is_dir():
                        # 递归搜索子目录
                        scan_directory(item, depth + 1)
                        
                except Exception as e:
                    logger.warning(f"Error processing item {item}: {e}")
                    continue
        
        # 开始搜索
        scan_directory(target_path)
        logger.info(f"Total files scanned: {total_files_scanned}, Matching files: {matching_files}")
        
        # 按相关性评分排序
        matching_files.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # 限制结果数量
        final_results = matching_files[:max_results]
        
        result = {
            "success": True,
            "query": keywords,
            "directory": str(target_path),
            "total_files_scanned": total_files_scanned,
            "matching_files": len(final_results),
            "results": final_results,
            "message": f"在 {total_files_scanned} 个文件中找到 {len(final_results)} 个匹配文件"
        }
        
        logger.info(f"Knowledge base search completed: {len(final_results)} matches found")
        return result
        
    except Exception as e:
        logger.error(f"search_knowledge_base failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "知识库搜索失败"
        }


def _check_file_matches(file_path: Path, keywords: List[str], patterns: List[tuple], 
                       search_content: bool, case_sensitive: bool) -> List[Dict[str, Any]]:
    """检查文件是否匹配搜索条件"""
    matches = []
    
    # 检查文件名
    filename = file_path.name
    filename_to_search = filename if case_sensitive else filename.lower()
    
    filename_matches = []
    for keyword, pattern in patterns:
        for match in pattern.finditer(filename_to_search):
            filename_matches.append({
                "type": "filename",
                "matched_text": match.group(),
                "position": match.start(),
                "keyword": keyword
            })
    
    if filename_matches:
        matches.extend(filename_matches)
    
    # 检查文件内容（如果启用）
    if search_content and file_path.suffix.lower() in ['.txt', '.md', '.pdf', '.rst', '.py', '.js', '.html', '.css']:
        try:
            content_matches = _search_file_content(file_path, patterns, case_sensitive)
            matches.extend(content_matches)
        except Exception as e:
            logger.debug(f"Could not read file content {file_path}: {e}")
    
    return matches


def _search_file_content(file_path: Path, patterns: List[tuple], case_sensitive: bool) -> List[Dict[str, Any]]:
    """搜索文件内容中的关键词"""
    matches = []
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 搜索每一行
        for line_num, line in enumerate(lines, 1):
            line_to_search = line if case_sensitive else line.lower()
            
            for keyword, pattern in patterns:
                for match in pattern.finditer(line_to_search):
                    # 提取上下文
                    start_pos = max(0, match.start() - 20)
                    end_pos = min(len(line), match.end() + 20)
                    context = line[start_pos:end_pos].strip()
                    
                    matches.append({
                        "type": "content",
                        "matched_text": match.group(),
                        "line_number": line_num,
                        "context": context,
                        "keyword": keyword
                    })
                    
                    # 限制每文件的内容匹配数量以提高性能
                    if len(matches) > 10:
                        return matches
                        
    except Exception as e:
        logger.debug(f"Error reading file content: {e}")
    
    return matches


def _get_file_info(file_path: Path, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """获取文件详细信息"""
    try:
        stat_info = file_path.stat()
        
        # 计算相关性评分
        relevance_score = _calculate_relevance_score(matches)
        
        # 确定匹配类型
        match_types = set(match['type'] for match in matches)
        if 'filename' in match_types and 'content' in match_types:
            match_type = "filename_and_content"
        elif 'filename' in match_types:
            match_type = "filename"
        else:
            match_type = "content"
        
        # 格式化修改时间
        import datetime
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_size": stat_info.st_size,
            "file_type": file_path.suffix.lower(),
            "modified_time": modified_time,
            "match_type": match_type,
            "relevance_score": relevance_score,
            "matches": matches
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {}


def _calculate_relevance_score(matches: List[Dict[str, Any]]) -> float:
    """计算文件的相关性评分"""
    if not matches:
        return 0.0
    
    score = 0.0
    filename_matches = 0
    content_matches = 0
    
    for match in matches:
        if match['type'] == 'filename':
            filename_matches += 1
            score += 0.5  # 文件名匹配权重较高
        else:
            content_matches += 1
            score += 0.2  # 内容匹配权重较低
    
    # 根据匹配数量调整评分
    if filename_matches > 0:
        score += min(filename_matches * 0.1, 0.3)
    if content_matches > 0:
        score += min(content_matches * 0.05, 0.2)
    
    # 确保评分在0-1范围内
    return min(score, 1.0)