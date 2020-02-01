# coding: utf-8

from datetime import datetime

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from leancloud import Object
from leancloud import Query
from leancloud.errors import LeanCloudError
import requests,time,os,json
import leancloud

# 需要提交的网址
BAIDU_URLS = os.environ['BAIDU_URLS']
# 百度站长提交地址
STATIONMASTER = os.environ['STATIONMASTER']
# 百度熊掌号提交地址
try:
    BEARPAW = os.environ['BEARPAW']
except:
    BEARPAW=None
print("BEARPAW=",BEARPAW)
class Todo(Object):
    pass
user = leancloud.User()
def login(request):
    if request.method == 'GET':
        current_user = leancloud.User.get_current()
        if current_user is not None:
            # 跳到首页
            return index(request)
        else:
            # 显示注册或登录页面
            return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password,666)
        try:
            user.login(email=username, password=password)
        except:
            return render(request, 'login.html',{"sign":'登录失败，账号或密码错误'})
        return index(request)
#注销登录
def logout(request):
    user.logout()
    return redirect('/')
#主页，显示提交数据
def index(request):
    dic = []
    # email = request.POST.get("")
    try:
        todos = Query(Todo).descending('createdAt').find()
        for i in todos:
            temp = {
                'id': i.get('objectId'),
                'content': i.get('content'),
                'time': i.get('createdAt').strftime('%Y-%m-%d %H:%M:%S'),
                'master_remain': i.get('master_remain'),
                'master_success': i.get('master_success'),
                'paw_remain': i.get('paw_remain'),
                'paw_success': i.get('paw_success'),

            }
            dic.append(temp)
    except LeanCloudError as e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            dic = []
        else:
            raise e
    return render(request, 'index.html', {
        'content': dic,
    })
#提交
def baidu_push(url,header,data):
    text = requests.post(url, headers=header, data=data)
    return json.loads(text.text)
def push():
    headers = {
        "User-Agent": "curl/7.12.1",
        "Host": "data.zz.baidu.com",
        "Content-Type": "text/plain"
    }
    # 需要提交的数据
    urls_list = requests.get(BAIDU_URLS).text
    #百度站长提交
    result_master =baidu_push(STATIONMASTER,headers,urls_list)
    #熊掌号提交
    if BEARPAW==None:
        result_paw = {
            'remain':0,
            'success':0,
            'success_batch':0,
            'remain_batch':0,
        }
    else:
        result_paw = baidu_push(BEARPAW, headers, urls_list)
    print(result_paw)
    result = {
        'master_remain':result_master['remain'],
        'master_success':result_master['success'],
        'paw_remain':result_paw['remain'],
        'paw_success':result_paw['success'],
        'paw_success_batch':result_paw['success_batch'],
        'paw_remain_batch':result_paw['remain_batch'],
    }
    todo = Todo(content=str(result),
                master_remain=result['master_remain'],
                master_success=result["master_success"],
                paw_remain=result["paw_remain"],
                paw_success=result["paw_success"],
                paw_success_batch=result["paw_success_batch"],
                paw_remain_batch=result["paw_remain_batch"],)
    try:
        todo.save()
    except LeanCloudError as e:
        return HttpResponseServerError(e.error)
    return HttpResponse(str(result))

def repush(request):
    result = push()
    return redirect('/')




class TodoView(View):
    def get(self, request):
        try:
            todos = Query(Todo).descending('createdAt').find()
        except LeanCloudError as e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                todos = []
            else:
                raise e
        return render(request, 'todos.html', {
            'todos': [x.get('content') for x in todos],
        })

    def post(self, request):
        content = request.POST.get('content')
        todo = Todo(content=content)
        try:
            todo.save()
        except LeanCloudError as e:
            return HttpResponseServerError(e.error)
        return HttpResponseRedirect(reverse('todo_list'))
