import shutil
import subprocess
import os, sys, re
from os.path import *
import javalang
from javalang.ast import Node
from pathlib import Path

def get_sample_ids(mutants_root_dir:str, projs:list):
    sample_ids = []
    for proj in projs:
        #  Todo: collections-25f?
        proj_dir = join(mutant_root_dir, proj + '-1f')
        sample_id_file = join(proj_dir, 'sampledMutIds.txt')
        with open(sample_id_file) as f:
            lines = f.readlines()
        for line in lines:
            sample_ids.append(proj + line.strip())
    return sample_ids

def load_mutants(proj:str):
    mutant_dir = join(mutant_root_dir, proj + '-1f', 'mutants')
    mutants_log_path = join(mutant_root_dir, proj + '-1f', 'mutants.log')
    mutants = {}
    with open(mutants_log_path) as f:
        lines = f.readlines()
        for line in lines:            
            # match line number
            line = line.strip()
            count = 0
            for match in re.finditer(r":[0-9]+:", line):
                count += 1
                line_no = int(match.group()[1:-1])
                start = match.start()
                end = match.end()
            assert count >= 1, mutants_log_path + '\t' + line
            
            line_head = line[:start]
            line_tail = line[end:]
            try:
                # [mid, operator, ori_symbol, rep_symbol, method_full_name] = line_head.strip().split(':')
                items = line_head.strip().split(':')
                [mid, operator] = items[:2]
                [rep_symbol, method_full_name] = items[-2:]
                ori_symbol = ':'.join(items[2:-2])
            except:
                print(line_head)
                raise Exception
            change = line_tail
            
            # # Currently we skip deletion mutation
            # if operator == 'STD': continue

            class_name = method_full_name.split('@')[0]
            if '$' in class_name:
                class_name = class_name.split('$')[0]
            mutated_file_path = class_name.replace('.', '/') + '.java'
            mutants[mid] = dict()
            mutants[mid]['operator'] = operator
            mutants[mid]['ori_symbol'] = ori_symbol
            mutants[mid]['rep_symbol'] = rep_symbol
            mutants[mid]['method_full_name'] = method_full_name
            mutants[mid]['line_no'] = line_no
            mutants[mid]['change'] = change
            mutants[mid]['path'] = mutated_file_path
    
    return mutants

def extract_method(src_code:str, method_lineno:int):
    lines = src_code.split('\n')
    start = method_lineno
    end = start + 1
    while (end <= len(lines) + 1):
        content = '\n'.join(lines[start - 1 : end - 1])
        if content.strip().endswith('}') and content.count('{') == content.count('}'):
            return content
        else:
            end += 1

    raise Exception

def extract_buggy_method_line(src_code:str, lineno:int, need_offset=False):
    # lineno starts from 1
    
    # javalang bug for chart31999
    print('line number: ' + str(lineno))
    tree = javalang.parse.parse(src_code)
    for decl in [javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration]:
        for _, node in tree.filter(decl):
            for _, child in node:
                start = node.position[0]
                if child.position != None:
                    end = child.position[0]
                    # print('start: {}'.format(start))
                    # print('end: {}'.format(end))
                    if need_offset:
                        start = start - 1
                        end = end - 1
                    if start <= lineno and end >= lineno:
                    # if child.position[0] == lineno:
                        return start
    
    raise Exception

def get_buggy_file(dir_path):
    return subprocess.run(['find', dir_path, '-name', '*.java'], stdout=subprocess.PIPE).stdout.decode().strip()

def get_line(file:str, lineno:int):
    with open(file) as f:
        lines = f.readlines()
    return lines[lineno - 1]

def file_to_str(file:str):
    with open(file) as f:
        content = f.read()
    return content

def make_ids(proj:str, mutants_dir:str):
    assert isdir(mutants_dir), mutants_dir
    ids_path = join(ids_info_dir, all_ids)
    mutants = load_mutants(proj)

    for i in mutants.keys():
        id = proj + str(i)
        if not id in sample_ids: continue
        method_full_name = mutants[str(i)]['method_full_name']
        buggy_line_no = int(mutants[str(i)]['line_no'])
        # recoder can not take care of bugs in fields so we should exclude them
        if ('@' not in method_full_name):
            print('bug not in method: ' + id)
            continue

        if isfile(join(ids_info_dir, 'buggy_methods', id + '.txt')): continue
                  
        buggy_class_file = get_buggy_file(join(mutants_dir, str(i)))
        assert isfile(buggy_class_file), mutants_dir + '\t' + buggy_class_file
        fixed_class_file = join(mutant_root_dir, proj + '-1f', src_rela_dir[proj], \
            relpath(buggy_class_file, join(mutants_dir, str(i))))
        assert isfile(fixed_class_file), mutants_dir + '\t' + fixed_class_file
        with open(ids_path, 'a') as f:
            f.write(id + '\n')

        shutil.copy(buggy_class_file, join(ids_info_dir, 'buggy_classes', id + '.java'))
        shutil.copyfile(fixed_class_file, join(ids_info_dir, 'fix_classes', id + '.java'))
        
        with open(join(ids_info_dir, 'buggy_lines', id + '.txt'), 'w') as f:
            f.write(get_line(buggy_class_file, buggy_line_no) + '\n')
        with open(join(ids_info_dir, 'fix_lines', id + '.txt'), 'w') as f:
            f.write(get_line(fixed_class_file, buggy_line_no) + '\n')

        buggy_class_content = file_to_str(buggy_class_file)
        fixed_class_content = file_to_str(fixed_class_file)
        print(id)
        print(buggy_class_file)
        print(fixed_class_file)
        # buggy_method_line_no = extract_buggy_method_line(buggy_class_content, buggy_line_no)
        if proj == 'lang' and i == '4661':
            buggy_method_line_no = extract_buggy_method_line(fixed_class_content, buggy_line_no, need_offset=True)
        else:
            buggy_method_line_no = extract_buggy_method_line(fixed_class_content, buggy_line_no)
        assert buggy_method_line_no <= buggy_line_no, mutants_dir + '\t' + id
        rel_line_no = buggy_line_no - buggy_method_line_no
        rel_line_range = '[' + str(rel_line_no) + ':' + str(rel_line_no + 1) + ']'
        buggy_method = extract_method(buggy_class_content, buggy_method_line_no)
        buggy_line = get_line(fixed_class_file, buggy_line_no)
        buggy_method_lines = buggy_method.split('\n')
        # fixed_method = '\n'.join(buggy_method_lines[:rel_line_no] + [buggy_line.replace('\n', '')] + buggy_method_lines[rel_line_no + 1:])
        fixed_method = extract_method(fixed_class_content, buggy_method_line_no)

        with open(join(ids_info_dir, 'buggy_methods', id + '.txt'), 'w') as f:
            f.write(buggy_method)
        with open(join(ids_info_dir, 'fix_methods', id + '.txt'), 'w') as f:
            f.write(fixed_method)
        
        meta_content = '<sep>'.join(['mutapr', id, rel_line_range, rel_line_range, 
        buggy_class_file + '@' + buggy_method_lines[0].strip().replace('{', '').replace('}', '')])
        with open(join(ids_info_dir, 'metas', id + '.txt'), 'w') as f:
            f.write(meta_content)

if __name__ == '__main__':
    # proj = sys.argv[1]
    # src_rela_dir = {"chart": "source", "cli": "src/java", "codec": "src/java", "compress": "src/main/java", "csv": "src/main/java",\
    # "gson": "gson/src/main/java", "jacksoncore": "src/main/java", "jacksondatabind": "src/main/java", "jacksonxml": "src/main/java", \
    #     "jsoup": "src/main/java", "jxpath": "src/java", "lang": "src/main/java", "time": "src/main/java"}
    src_rela_dir = {"cli": "src/java", "codec": "src/java", "compress": "src/main/java", "csv": "src/main/java",\
    "gson": "gson/src/main/java", "jacksoncore": "src/main/java", "jacksonxml": "src/main/java", \
        "jsoup": "src/main/java", "jxpath": "src/java", "lang": "src/main/java", "time": "src/main/java"}
    mutant_root_dir = '../dataset/d4jProj/'
    projects = src_rela_dir.keys()
    sample_ids_file = 'ids_all_info/sample_1100.ids'
    Path("ids_all_info").mkdir(exist_ok=True)
    sample_ids = get_sample_ids(mutant_root_dir, projects)
    with open(sample_ids_file, 'w') as f:
        for id in sample_ids:
            f.write(id + '\n')
    all_ids = 'all.ids'
    ids_info_dir = 'ids_all_info'
    
    (Path(ids_info_dir) / "buggy_classes").mkdir(exist_ok=True)
    (Path(ids_info_dir) / "fix_classes").mkdir(exist_ok=True)
    (Path(ids_info_dir) / "buggy_lines").mkdir(exist_ok=True)
    (Path(ids_info_dir) / "fix_lines").mkdir(exist_ok=True)
    (Path(ids_info_dir) / "buggy_methods").mkdir(exist_ok=True)
    (Path(ids_info_dir) / "fix_methods").mkdir(exist_ok=True)
    (Path(ids_info_dir) / "metas").mkdir(exist_ok=True)

    for proj in projects:
        mutants_dir = join(mutant_root_dir, proj + '-1f', 'mutants')
        log_file = join(mutant_root_dir, proj + '-1f', 'mutants.log')
        make_ids(proj, mutants_dir)