import csv
import re
import os
import git

def get_commit_count(file_path):
    try:
        repo = git.Repo(file_path, search_parent_directories=True)
        return len(list(repo.iter_commits(paths=file_path)))
    except Exception as e:
        print(f"Error getting commit count for {file_path}: {e}")
        return 0

def get_xtext_file_content(repo, file_path, commit_sha):
    try:
        # 获取相对路径
        git_root = repo.working_dir.replace('\\', '/') + '/'
        rel_file_path = file_path.replace('\\', '/').replace(git_root, '')
        file_content = repo.git.show(f"{commit_sha}:{rel_file_path}")
        return file_content
    except Exception as e:
        print(f"Error getting file content for {file_path} ({commit_sha}): {e}")
        return ""

def find_xtext_files(root_dir):
    xtext_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".xtext"):
                file_path = os.path.join(root, file)
                commit_count = get_commit_count(file_path)
                xtext_files.append((file_path, commit_count))
    return xtext_files

def does_string_exist(str_input, str_regex):
    pattern = re.compile(str_regex)
    return bool(pattern.search(str_input))

def is_first_line_of_grammar_rule(s):
    return does_string_exist(s, r"\w+\s*\:") and not does_string_exist(s, r"\w+\s*\+*=")

def count_grammar_rule(str_raw):
    # Split the contents of Xtext file (i.e. string) into lines
    lines = str_raw.split("\n")

    count = 0
    for line in lines:
        if is_first_line_of_grammar_rule(line) and not does_string_exist(line, r"import.*http"):
            count += 1

    return count

# 读取 CSV 文件获取 owner 和 repo 信息
csv_file_path = r'D:\02.Git Repository\XtextRepoSurvey\manual_analysis_results\mwe2_and_extensions.csv'
output_csv_file = 'count_changed_rule.csv'

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file, \
        open(output_csv_file, mode='w', newline='', encoding='utf-8') as output_csv:
    reader = csv.reader(csv_file)
    writer = csv.writer(output_csv)

    # 写入 CSV 文件的 header
    writer.writerow(['owner', 'repo', 'average_count_diff'])

    next(reader)  # 跳过header行
    for row in reader:
        owner = row[0]
        repo_name = row[1]
        root_folder = f'E:\\xtext_repos_clone_new\\{owner}_{repo_name}'

        print(f"Analyzing {owner} | {repo_name}")

        # 查找所有扩展名为.xtext的文件并获取其commit次数
        xtext_files_list = find_xtext_files(root_folder)
        total_count_diff = 0
        file_count = len(xtext_files_list)

        # 处理每个文件的commit次数和文本，并计算差异
        for file_path, commit_count in xtext_files_list:
            print(f"File: {file_path} | Commit Count: {commit_count}")

            try:
                # 获取该文件最近两次commit的文本并传递给count_grammar_rule函数
                repo = git.Repo(file_path, search_parent_directories=True)
                commits = list(repo.iter_commits(paths=file_path))[:2]
                commit_texts = [get_xtext_file_content(repo, file_path, commit.hexsha) for commit in commits]
                
                if len(commit_texts) == 2:
                    result_before = count_grammar_rule(commit_texts[0])
                    print(f"Count of rules in first commit: {result_before}")
                    result_after = count_grammar_rule(commit_texts[1])
                    print(f"Count of rules in last commit: {result_after}")
                    count_diff = result_after - result_before
                    print(f"Grammar rules added/removed: {count_diff}")
                    total_count_diff += count_diff
                else:
                    print("Grammar rules added/removed: 0")
            except Exception as e:
                print(f"Error occurred while reading file {file_path}: {e}")
                result_before = 0
                result_after = 0
                count_diff = 0
            
        
        average_count_diff = total_count_diff / file_count if file_count > 0 else 0
        print(f"Average Grammar rules added/removed: {average_count_diff:.2f}")

        # 将部分结果写入CSV文件
        writer = csv.writer(output_csv)
        writer.writerow([owner, repo_name, f"{average_count_diff:.2f}"])

        print(f"Results written to {csv_file}")