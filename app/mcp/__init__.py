"""MCP Package - MCP 适配器包

统一创建和管理 MCP 服务器实例。
所有 MCP 工具文件应从此处导入 mcp 实例。
"""

def get_mcp():
    """获取 MCP 服务器实例，只在需要时创建"""
    if not hasattr(get_mcp, '_instance'):
        from app.common.app import create_mcp
        get_mcp._instance = create_mcp()
    return get_mcp._instance


# 创建一个代理对象，仅在访问属性时才获取真实实例
class MCPLazyProxy:
    """延迟加载 MCP 实例的代理"""
    
    def __init__(self):
        self._instance = None
    
    def _get_instance(self):
        if self._instance is None:
            self._instance = get_mcp()
        return self._instance
    
    def __getattr__(self, name):
        # 当访问属性时，获取真实实例并返回相应属性
        instance = self._get_instance()
        return getattr(instance, name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            # 内部属性直接设置
            super().__setattr__(name, value)
        else:
            # 其他属性设置到真实实例上
            instance = self._get_instance()
            setattr(instance, name, value)
    
    def __call__(self, *args, **kwargs):
        # 如果 proxy 被调用，返回实例
        return self._get_instance()


# 创建延迟代理实例
mcp = MCPLazyProxy()

# 导入工具模块以确保它们被注册
try:
    import app.mcp.stock_outstage_tool
    import app.mcp.get_current_time
except ImportError as e:
    # 如果工具模块不存在，不抛出错误，让它们在需要时单独导入
    pass

__all__ = ["mcp", "get_mcp"]