import uvicorn
import os
import sys

def main():
    # 检查必需的环境变量
    if not os.getenv("ALIYUN_API_KEY"):
        print("错误: 请设置 ALIYUN_API_KEY 环境变量")
        print("Windows: set ALIYUN_API_KEY=你的阿里云API Key")
        print("Linux/Mac: export ALIYUN_API_KEY=你的阿里云API Key")
        sys.exit(1)
    
    if not os.getenv("ALIYUN_WORKSPACE_ID") or os.getenv("ALIYUN_WORKSPACE_ID") == "your-workspace-id":
        print("错误: 请设置 ALIYUN_WORKSPACE_ID 环境变量")
        print("Windows: set ALIYUN_WORKSPACE_ID=你的工作空间ID")
        print("Linux/Mac: export ALIYUN_WORKSPACE_ID=你的工作空间ID")
        sys.exit(1)
    
    if not os.getenv("ALIYUN_APP_ID") or os.getenv("ALIYUN_APP_ID") == "your-app-id":
        print("错误: 请设置 ALIYUN_APP_ID 环境变量")
        print("Windows: set ALIYUN_APP_ID=你的应用ID")
        print("Linux/Mac: export ALIYUN_APP_ID=你的应用ID")
        sys.exit(1)

    print("启动MCP阿里云适配器服务...")
    print("服务将在 http://localhost:8000/mcp/multimodal 上运行")

    # 启动服务器
    uvicorn.run(
        "mcp_aliyun_adapter:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False  # 生产环境关闭热重载
    )

if __name__ == "__main__":
    main()