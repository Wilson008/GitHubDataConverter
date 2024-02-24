import requests
import datetime
import json
import os

def search_github_repositories():
    headers = {
        'Authorization': 'token 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'
    }
    # 获取当前日期
    stop_date = datetime.datetime(2017, 12, 31).isoformat()
    # 获取2019年1月1日的日期
    since_date = datetime.datetime(2000, 1, 1).isoformat()

    repositories = []

    # 初始化页码
    page = 1

    while True:
        # API 请求的 URL，设置每页显示100个结果
        url = f'https://api.github.com/search/repositories?q=.xtext+created:{since_date}..{stop_date}+fork:false&page={page}&per_page=100'

        try:
            # 发送 GET 请求
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查是否有错误发生

            data = response.json()
            repositories.extend(data['items'])

            # 如果当前页没有结果了，则结束循环
            if len(data['items']) == 0:
                break

            # 打印当前页数
            print(f"Page {page} retrieved.")

            # 将当前页的结果写入到对应的文件中
            write_to_file(data, page)

            # 下载当前页存储库的 ZIP 归档
            download_repository_zips(data)

            # 前往下一页
            page += 1

        except requests.exceptions.RequestException as e:
            print('Error:', e)
            break

    return repositories

def write_to_file(data, page):
    # 将结果写入到对应的文件中
    filename = f'search_results/Python_search_results_{page+5}.txt'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, indent=4))  # 将整个响应内容写入文件

def download_repository_zips(data):
    count = 0
    for item in data['items']:
        owner = item['owner']['login']
        repo = item['name']
        count = count + 1
        download_repository_zip(owner, repo, count)

def download_repository_zip(owner, repo, count):
    headers = {
        'Authorization': 'token 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',
        'Accept': 'application/vnd.github.v3+json'
    }

    # 构造下载存储库 ZIP 归档的 API 请求
    url = f'https://api.github.com/repos/{owner}/{repo}/zipball'

    try:
        # 发送 GET 请求
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查是否有错误发生

        # 创建输出目录（如果不存在）
        output_dir = 'E:/xtext_repositories'  # 输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 将响应内容写入文件
        file_path = os.path.join(output_dir, f'{repo}.zip')
        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f"{count}: Repository {owner}/{repo} Zip archive is downloaded successfully.")

    except requests.exceptions.RequestException as e:
        print('Error:', e)

def main():
    # 调用函数搜索GitHub存储库
    search_github_repositories()
    print("All search results have been written to separate files.")

if __name__ == "__main__":
    main()
