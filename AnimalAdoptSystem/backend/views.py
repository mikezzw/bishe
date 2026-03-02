from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import os
from django.conf import settings

@csrf_exempt
def frontend_index(request):
    """
    服务前端单页应用的主页面
    """
    # 如果是 API 请求，返回 404
    if request.path.startswith('/api/'):
        return HttpResponse('API endpoint not found', status=404)
    
    # 对于所有其他路径，返回前端应用的 index.html
    # 这样可以让前端路由处理所有非 API 请求
    frontend_index_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'dist', 'index.html')
    
    if os.path.exists(frontend_index_path):
        with open(frontend_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        # 开发环境下返回简单的 HTML
        return HttpResponse('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>动物领养系统</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>动物领养系统</h1>
            <p>前端应用正在运行中...</p>
            <p>请确保前端开发服务器已在运行</p>
        </body>
        </html>
        ''', content_type='text/html')
