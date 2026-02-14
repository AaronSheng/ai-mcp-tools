import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.mcp import mcp
from app.common.logging import logger

@mcp.tool()
async def search_knowledge_content(
    file_names: List[str],
    keywords: str,
    context_lines: int = 3,
    case_sensitive: bool = False,
    max_results_per_file: int = 10
) -> Dict[str, Any]:
    """深度检索知识库文件内容 ⭐ 智能内容提取工具

    从指定的知识库文件中智能提取包含关键词的内容片段。
    专注于文件内容检索，提供上下文和相关性分析。

    适用场景：
    - 从多个文档中精准提取相关信息
    - 知识点深度挖掘和整理
    - 文档内容智能摘要生成
    - 学习资料重点内容提取
    - 技术文档关键信息检索

    Args:
        file_names: 文件名列表（支持部分匹配和通配符）
        keywords: 搜索关键词（支持多个关键词，用空格分隔）
        context_lines: 上下文行数，默认3行（关键词前后各3行）
        case_sensitive: 是否区分大小写，默认False
        max_results_per_file: 每个文件最多返回的结果数，默认10

    Returns:
        深度提取结果:
        {
            "success": True,
            "query": {
                "keywords": ["关键词1", "关键词2"],
                "file_patterns": ["文件名1", "文件名2"],
                "directory": "/path/to/knowledge/base",
                "context_lines": 3
            },
            "statistics": {
                "total_files_scanned": 15,
                "files_with_matches": 8,
                "total_matches_found": 42,
                "unique_keywords_matched": ["关键词1", "关键词2"]
            },
            "results": [
                {
                    "file_info": {
                        "name": "example.md",
                        "path": "/path/to/example.md",
                        "size": 2048,
                        "modified_time": "2024-01-01 10:00:00",
                        "file_type": ".md"
                    },
                    "content_matches": [
                        {
                            "keyword": "关键词1",
                            "line_number": 15,
                            "exact_match": "这是包含关键词的完整句子",
                            "context": {
                                "before": ["前一行内容", "前二行内容"],
                                "matched_line": "这是包含关键词的完整句子",
                                "after": ["后一行内容", "后二行内容"]
                            },
                            "relevance": {
                                "score": 0.95,
                                "position_bonus": 0.2,
                                "context_bonus": 0.15,
                                "length_bonus": 0.05
                            },
                            "metadata": {
                                "match_type": "whole_word",  // whole_word, partial, phrase
                                "occurrences_in_line": 2
                            }
                        }
                    ],
                    "summary": {
                        "total_matches": 5,
                        "unique_keywords": ["关键词1", "关键词2"],
                        "avg_relevance_score": 0.87
                    }
                }
            ],
            "recommendations": [
                "建议查看 example.md 文件获取更多相关信息",
                "关键词'机器学习'在多个文件中频繁出现"
            ],
            "message": "从8个文件中深度提取到42个高质量内容片段"
        }

    Examples:
        # 基础内容检索
        result = await search_knowledge_content(
            file_names=["学习笔记", "教程"],
            keywords="机器学习 算法"
        )
        
        # 精确匹配检索
        result = await search_knowledge_content(
            file_names=["技术文档*"],
            keywords="Python 数据库",
            case_sensitive=True,
            context_lines=5
        )
        
        # 限制结果数量
        result = await search_knowledge_content(
            file_names=["项目文档"],
            keywords="API 接口",
            max_results_per_file=5
        )
        
        # 指定不同知识库目录
        result = await search_knowledge_content(
            file_names=["README", "文档"],
            keywords="部署 配置",
            directory_path="/Users/username/Projects/my_project"
        )
    """
    try:
        logger.info(f"MCP Tool called: search_knowledge_content (files={len(file_names)}, keywords={keywords})")
        
        # 验证输入参数
        if not file_names or not any(fn.strip() for fn in file_names):
            return {
                "success": False,
                "error": "文件名列表不能为空",
                "message": "请提供有效的文件名列表"
            }
        
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
        
        # 清理文件名列表
        clean_file_names = [fn.strip() for fn in file_names if fn.strip()]
        
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
        
        # 准备搜索模式
        search_patterns = []
        for keyword in keyword_list:
            if case_sensitive:
                pattern = re.compile(re.escape(keyword))
            else:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            search_patterns.append((keyword, pattern))
        
        # 查找匹配的文件
        matching_files = _find_matching_files(target_path, clean_file_names)
        logger.info(f"Find matching files: {matching_files}")

        if not matching_files:
            return {
                "success": True,
                "query": {
                    "keywords": keyword_list,
                    "file_patterns": clean_file_names,
                    "directory": str(target_path),
                    "context_lines": context_lines
                },
                "statistics": {
                    "total_files_scanned": 0,
                    "files_with_matches": 0,
                    "total_matches_found": 0,
                    "unique_keywords_matched": []
                },
                "results": [],
                "recommendations": ["未找到匹配的文件，请检查文件名模式"],
                "message": f"未找到匹配的文件（搜索模式: {clean_file_names}）"
            }
        
        # 深度提取文件内容
        results = []
        total_matches_found = 0
        unique_keywords_matched = set()
        files_with_matches = 0
        
        for file_path in matching_files:
            try:
                file_matches = _deep_extract_content(
                    file_path, search_patterns, context_lines, 
                    case_sensitive, max_results_per_file
                )
                
                if file_matches:
                    files_with_matches += 1
                    file_total_matches = len(file_matches)
                    total_matches_found += file_total_matches
                    
                    # 收集找到的关键词
                    for match in file_matches:
                        unique_keywords_matched.add(match['keyword'])
                    
                    # 获取文件详细信息
                    file_info = _get_file_detailed_info(file_path)
                    
                    # 计算文件级别统计
                    file_unique_keywords = list(set(match['keyword'] for match in file_matches))
                    avg_relevance = sum(match['relevance']['score'] for match in file_matches) / len(file_matches)
                    
                    results.append({
                        "file_info": file_info,
                        "content_matches": file_matches,
                        "summary": {
                            "total_matches": file_total_matches,
                            "unique_keywords": file_unique_keywords,
                            "avg_relevance_score": round(avg_relevance, 3)
                        }
                    })
                    
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {e}")
                continue
        
        # 生成推荐建议
        recommendations = _generate_recommendations(
            results, keyword_list, unique_keywords_matched
        )
        
        result = {
            "success": True,
            "query": {
                "keywords": keyword_list,
                "file_patterns": clean_file_names,
                "directory": str(target_path),
                "context_lines": context_lines
            },
            "statistics": {
                "total_files_scanned": len(matching_files),
                "files_with_matches": files_with_matches,
                "total_matches_found": total_matches_found,
                "unique_keywords_matched": sorted(list(unique_keywords_matched))
            },
            "results": results,
            "recommendations": recommendations,
            "message": f"从{files_with_matches}个文件中深度提取到{total_matches_found}个高质量内容片段"
        }
        
        logger.info(f"Deep knowledge content search completed: {total_matches_found} matches from {files_with_matches} files")
        return result
        
    except Exception as e:
        logger.error(f"search_knowledge_content failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "知识库内容深度检索失败"
        }


def _find_matching_files(directory_path: Path, file_patterns: List[str]) -> List[Path]:
    """智能查找匹配的文件（支持通配符）"""
    matching_files = []
    
    def search_directory(current_path: Path):
        try:
            items = list(current_path.iterdir())
        except PermissionError:
            logger.warning(f"Permission denied: {current_path}")
            return
        
        for item in items:
            try:
                if item.is_file():
                    # 检查文件名是否匹配任一模式（支持通配符）
                    filename = item.name.lower()
                    for pattern in file_patterns:
                        pattern_lower = pattern.lower()
                        # 简单的通配符支持
                        if '*' in pattern_lower:
                            regex_pattern = pattern_lower.replace('*', '.*')
                            if re.match(regex_pattern, filename):
                                matching_files.append(item)
                                break
                        elif pattern_lower in filename:
                            matching_files.append(item)
                            break
                elif item.is_dir():
                    # 递归搜索子目录
                    search_directory(item)
            except Exception as e:
                logger.warning(f"Error checking item {item}: {e}")
                continue
    
    search_directory(directory_path)
    return matching_files


def _deep_extract_content(
    file_path: Path, 
    patterns: List[tuple], 
    context_lines: int, 
    case_sensitive: bool,
    max_results: int
) -> List[Dict[str, Any]]:
    """深度提取文件内容（增强版，支持PDF文件）"""
    matches = []
    
    try:
        # 根据文件类型选择不同的处理方式
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            # 处理PDF文件
            lines = _extract_pdf_content(file_path)
        else:
            # 处理文本文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        if not lines:
            return []
        
        # 为每行创建索引并搜索
        for line_num, line in enumerate(lines, 1):
            line_to_search = line if case_sensitive else line.lower()
            
            # 检查每种模式
            for keyword, pattern in patterns:
                pattern_matches = list(pattern.finditer(line_to_search))
                
                for match_obj in pattern_matches:
                    # 提取上下文
                    start_line = max(0, line_num - context_lines - 1)
                    end_line = min(len(lines), line_num + context_lines)
                    
                    context_before = [
                        lines[i].rstrip() for i in range(start_line, line_num - 1)
                    ] if start_line < line_num - 1 else []
                    
                    context_after = [
                        lines[i].rstrip() for i in range(line_num, end_line)
                    ] if line_num < end_line else []
                    
                    # 深度分析匹配信息
                    match_analysis = _analyze_match(
                        match_obj, line, keyword, len(context_before), len(context_after)
                    )
                    
                    matches.append({
                        "keyword": keyword,
                        "line_number": line_num,
                        "exact_match": match_obj.group(),
                        "context": {
                            "before": context_before,
                            "matched_line": line.rstrip(),
                            "after": context_after
                        },
                        "relevance": match_analysis['relevance'],
                        "metadata": match_analysis['metadata']
                    })
        
        # 按相关性评分排序并限制结果数量
        matches.sort(key=lambda x: x['relevance']['score'], reverse=True)
        return matches[:max_results]
        
    except Exception as e:
        logger.warning(f"Error deep extracting content from {file_path}: {e}")
        return []


def _extract_pdf_content(pdf_path: Path) -> List[str]:
    """提取PDF文件内容并转换为行列表"""
    try:
        # 尝试使用 PyPDF2
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
                full_text = '\n'.join(text_content)
        except ImportError:
            # 如果 PyPDF2 不可用，尝试使用 pdfplumber
            try:
                import pdfplumber
                text_content = []
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text_content.append(page.extract_text() or "")
                full_text = '\n'.join(text_content)
            except ImportError:
                # 如果都没有，尝试使用 pymupdf (fitz)
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(pdf_path)
                    text_content = []
                    for page in doc:
                        text_content.append(page.get_text())
                    full_text = '\n'.join(text_content)
                    doc.close()
                except ImportError:
                    logger.warning(f"No PDF processing library available for {pdf_path}")
                    return []
        
        # 将文本分割成行
        lines = full_text.split('\n')
        # 过滤掉空行和只包含空白字符的行
        lines = [line for line in lines if line.strip()]
        
        logger.info(f"Successfully extracted {len(lines)} lines from PDF: {pdf_path.name}")
        return lines
        
    except Exception as e:
        logger.error(f"Error extracting PDF content from {pdf_path}: {e}")
        return []


def _analyze_match(
    match_obj, 
    line_content: str, 
    keyword: str,
    context_before_count: int, 
    context_after_count: int
) -> Dict[str, Any]:
    """深度分析匹配信息"""
    
    # 计算基础相关性评分
    base_score = 0.4
    
    # 位置奖励
    position_bonus = 0.0
    match_position = match_obj.start()
    line_length = len(line_content)
    
    if match_position == 0:
        position_bonus = 0.2  # 行首匹配最高奖励
    elif match_position < line_length * 0.3:
        position_bonus = 0.1  # 前30%位置中等奖励
    elif match_position > line_length * 0.7:
        position_bonus = 0.05  # 后30%位置小奖励
    
    # 上下文奖励
    context_bonus = min((context_before_count + context_after_count) * 0.05, 0.2)
    
    # 长度奖励
    length_bonus = min(len(line_content) * 0.001, 0.1)
    
    # 关键词密度奖励（在同一行中出现次数）
    keyword_count = line_content.lower().count(keyword.lower())
    density_bonus = min((keyword_count - 1) * 0.05, 0.15) if keyword_count > 1 else 0.0
    
    total_score = base_score + position_bonus + context_bonus + length_bonus + density_bonus
    
    return {
        "relevance": {
            "score": min(total_score, 1.0),
            "position_bonus": position_bonus,
            "context_bonus": context_bonus,
            "length_bonus": length_bonus,
            "density_bonus": density_bonus
        },
        "metadata": {
            "match_type": "whole_word" if match_obj.group() == keyword else "partial",
            "occurrences_in_line": keyword_count,
            "match_start": match_obj.start(),
            "match_end": match_obj.end()
        }
    }


def _get_file_detailed_info(file_path: Path) -> Dict[str, Any]:
    """获取文件详细信息"""
    try:
        stat_info = file_path.stat()
        import datetime
        modified_time = datetime.datetime.fromtimestamp(
            stat_info.st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat_info.st_size,
            "modified_time": modified_time,
            "file_type": file_path.suffix.lower() or "unknown"
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": 0,
            "modified_time": "Unknown",
            "file_type": "unknown"
        }


def _generate_recommendations(
    results: List[Dict], 
    searched_keywords: List[str], 
    found_keywords: set
) -> List[str]:
    """生成智能推荐建议"""
    recommendations = []
    
    if not results:
        return ["未找到相关内容，请尝试调整关键词或文件名模式"]
    
    # 基于结果生成推荐
    total_files = len(results)
    high_relevance_files = [r for r in results if r['summary']['avg_relevance_score'] > 0.8]
    
    if high_relevance_files:
        best_file = max(high_relevance_files, key=lambda x: x['summary']['avg_relevance_score'])
        recommendations.append(f"推荐优先查看 '{best_file['file_info']['name']}' 文件")
    
    # 关键词覆盖分析
    missing_keywords = set(searched_keywords) - found_keywords
    if missing_keywords:
        recommendations.append(f"以下关键词未找到匹配内容: {', '.join(missing_keywords)}")
    
    # 文件多样性建议
    if total_files > 1:
        recommendations.append(f"相关内容分布在 {total_files} 个文件中，建议综合参考")
    
    return recommendations