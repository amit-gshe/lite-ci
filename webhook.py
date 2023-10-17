from flask import Flask
from flask import request
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor
from dingtalkchatbot.chatbot import DingtalkChatbot

app = Flask(__name__)
executor = ThreadPoolExecutor()
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
build_script = '/home/jack/.bin/build'
project_dir = '/home/jack/build'

dingding = DingtalkChatbot(webhook)


def handle(params):
    project = params['repository']['name']
    ref = params['ref']
    result = subprocess.run(
        [build_script, ref], cwd=project_dir + project, capture_output= True, timeout=3600)
    author = params['user_name']
    commit_message = ''
    title = '任务执行成功'
    error = ''
    if len(params['commits']) > 0:
        author = params['commits'][-1]['author']['name']
        commit_message = params['commits'][-1]['message']
    if result.returncode != 0:
        title = "任务执行失败"
        error = result.stderr.decode('utf-8')
    content = "#### **{}**\n\n".format(title)
    content += "**项目:** {}\n\n".format(project)
    content += "**触发分支:** {}\n\n".format(ref)
    content += "**开发者:** {}\n\n".format(author)
    if commit_message:
        content += "**提交:** {}\n\n".format(commit_message)
    if error:
        content += "**失败详情:** \n> {}\n".format(error)
    dingding.send_markdown(title, content)
    print(result.stdout.decode('utf-8'))
    print(result.stderr.decode('utf-8'))

@app.route('/game/build', methods=['POST'])
def build():
    params = json.loads(request.data)
    executor.submit(handle, params)
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
