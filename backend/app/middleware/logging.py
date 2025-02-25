from fastapi import Request, Response
from sqlalchemy.orm import Session
from typing import Callable, Awaitable
import json
from datetime import datetime

from ..models.operation_log import OperationLog
from ..database import get_db
from ..auth.jwt import get_current_user

class LoggingMiddleware:
    """操作日志中间件"""
    
    def __init__(
        self,
        app,
        db: Session,
        exclude_paths: list[str] = None
    ):
        self.app = app
        self.db = db
        self.exclude_paths = exclude_paths or ["/api/health"]

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # 跳过不需要记录的路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # 记录请求开始时间
        start_time = datetime.utcnow()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # 获取请求体
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                body = await request.body()

        try:
            # 获取当前用户
            user = await get_current_user(request)
            
            # 执行请求
            response = await call_next(request)
            
            # 记录响应时间
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # 确定操作类型
            action_map = {
                "GET": "read",
                "POST": "create",
                "PUT": "update",
                "PATCH": "update",
                "DELETE": "delete"
            }
            action = action_map.get(method, "other")
            
            # 确定模块
            path_parts = path.strip("/").split("/")
            module = path_parts[1] if len(path_parts) > 1 else "system"
            
            # 创建日志记录
            log = OperationLog(
                user_id=user.id,
                username=user.username,
                module=module,
                action=action,
                description=f"{user.username} 执行了 {module} 模块的 {action} 操作",
                details={
                    "method": method,
                    "path": path,
                    "query_params": query_params,
                    "body": body,
                    "duration": duration,
                    "status_code": response.status_code
                },
                ip=client_ip,
                user_agent=user_agent,
                status="success" if response.status_code < 400 else "failure"
            )
            
            # 保存日志
            self.db.add(log)
            self.db.commit()
            
            return response
            
        except Exception as e:
            # 记录错误日志
            log = OperationLog(
                user_id=getattr(user, "id", None),
                username=getattr(user, "username", "anonymous"),
                module=module,
                action=action,
                description=f"操作失败: {str(e)}",
                details={
                    "method": method,
                    "path": path,
                    "query_params": query_params,
                    "body": body,
                    "error": str(e)
                },
                ip=client_ip,
                user_agent=user_agent,
                status="failure"
            )
            
            self.db.add(log)
            self.db.commit()
            
            raise 