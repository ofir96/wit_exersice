import datetime
from distutils.dir_util import copy_tree
from filecmp import cmp
import os
import random
from shutil import copyfile
import sys

import matplotlib.pyplot as plt


class WitException(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return 'Your wit command are failed- check with status command.'


def init():
    wit_path = os.path.join(os.getcwd(), '.wit')
    os.mkdir(wit_path)
    os.mkdir(os.path.join(wit_path, 'image'))
    os.mkdir(os.path.join(wit_path, 'staging_area'))
    with open(os.path.join(os.getcwd(), '.wit', 'activated.txt'), 'w') as activated_file:
        activated_file.write('master')


def add(file_path):
    wit_path = os.path.join(os.getcwd(), '.wit', 'staging_area')
    if os.path.isdir(wit_path):
        prime_path = os.path.join(os.getcwd(), file_path)
        if os.path.isfile(file_path):
            staged_copy_file = os.path.join(wit_path, os.path.basename(file_path))
            copyfile(prime_path, staged_copy_file)
        elif os.path.isfile(prime_path):
            copy_file = os.path.join(wit_path, file_path)
            copyfile(prime_path, copy_file)
        elif os.path.isdir(prime_path):
            copy_directory = os.path.join(wit_path, file_path)
            os.mkdir(copy_directory)
            files_names = os.listdir(prime_path)
            for file in files_names:
                prime = os.path.join(prime_path, file)
                if os.path.isdir(prime):
                    for subfile in os.listdir(prime):
                        copy_sub_directory = os.path.join(copy_directory, file)
                        if not os.path.isdir(copy_sub_directory):
                            os.mkdir(copy_sub_directory)
                        prime_subfile = os.path.join(prime, subfile)
                        copy_subfile = os.path.join(copy_sub_directory, subfile)
                        copyfile(prime_subfile, copy_subfile)
                else:
                    copy = os.path.join(copy_directory, file)
                    print(prime, copy)
                    copyfile(prime, copy)
    else:
        raise OSError


def commit(message):
    activated_file = os.path.join(os.getcwd(), '.wit', 'activated.txt')
    if os.path.getsize(activated_file) > 0:
        with open(activated_file, 'r') as activated:
            read_active_branch = activated.read()
    reference_file = open(os.path.join(os.getcwd(), '.wit', 'references.txt'), 'a+')
    reference_file.close()
    chars = '123456789abcdef'
    commit_id = ''.join([random.choice(chars) for _ in range(40)])
    image_directory = os.path.join(os.getcwd(), '.wit', 'image')
    commit_file = os.path.join(image_directory, commit_id)
    os.mkdir(commit_file)
    text_commit = os.path.join(commit_file, commit_file + '.txt')
    staging_area = (os.path.join(os.getcwd(), '.wit', 'staging_area'))
    for file in os.listdir(staging_area):
        prime_file = os.path.join(staging_area, file)
        copy_file = os.path.join(commit_file, file)
        if os.path.isdir(prime_file):
            copy_tree(prime_file, copy_file)
        else:
            copyfile(prime_file, copy_file)
    with open(text_commit, 'w') as txt_id_commit_file:
        if os.path.getsize(os.path.join(os.getcwd(), '.wit', 'references.txt')) == 0:
            txt_id_commit_file.write(
                f'''parent=None
        date= {datetime.datetime.now()}
        message= {message}'''
            )
        else:
            with open(os.path.join(os.getcwd(), '.wit', 'references.txt'), 'r') as reference_file:
                read_reference_file = reference_file.read().split('\n')
                read_head = read_reference_file[0].split('HEAD=')[1]
                try:
                    read_branch_name = read_reference_file[2].split('=')[0]
                    read_branch_id = read_reference_file[2].split('=')[1]
                    read_master = read_reference_file[1]
                except IndexError:
                    pass
            txt_id_commit_file.write(
                f'''parent={read_head}
            date= {datetime.datetime.now()}
            message= {message}''')
    if read_active_branch == 'master':
        with open((os.path.join(os.getcwd(), '.wit', 'references.txt')), 'w') as refer_file:
            refer_file.write(f'HEAD={commit_id} \n')
            refer_file.write(f'master={commit_id}')
    else:
        with open(os.path.join(os.getcwd(), '.wit', 'references.txt'), 'w') as reference_file:
            if read_active_branch == read_branch_name:
                if read_head == read_branch_id:
                    reference_file.write(f'HEAD={commit_id} \n')
                    if activated_file == 'master':
                        reference_file.write(f'master={commit_id} \n')
                    else:
                        reference_file.write(f'{read_master} \n')
                    reference_file.write(f'{read_branch_name}={commit_id}')
                else:
                    reference_file.write(f'HEAD={commit_id} \n')
                    if activated_file == 'master':
                        reference_file.write(f'master={commit_id} \n')
                    else:
                        reference_file.write(f'{read_master} \n')


def status():
    refer_file = os.path.join(os.getcwd(), '.wit', 'references.txt')
    with open(refer_file, 'r') as file:
        commit_id_file = file.readline().split('HEAD=')[1]
    staging_area_directory = os.path.join(os.getcwd(), '.wit', 'staging_area')
    changes_to_be_committed = changes_to_be_commited(staging_area_directory)
    changes_not_staged_for_commit_list = changes_not_staged_for_commit(staging_area_directory)
    print(f'commit-id - {commit_id_file} \n'
          f'{"_" * 20} \n'
          f'Changes to be committed:')
    for i in changes_to_be_committed:
        print(i)
    print(f'{"_" * 20}')
    print('Changes not staged for commit:')
    for i in changes_not_staged_for_commit_list:
        print(i)
    print(f'{"_" * 20}')
    print('Untracked files')
    for file in os.listdir(os.getcwd()):
        if file not in os.listdir(staging_area_directory) and file != '.wit' and file != 'wit.py':
            print(file)


def changes_to_be_commited(staging_path):
    list_of_added_file = []
    with open(os.path.join(os.getcwd(), '.wit', 'references.txt')) as ref_f:
        read_last_commit = ref_f.readline().split('HEAD=')[1].strip('\n ')
    for file in os.listdir(staging_path):
        if file not in os.listdir(
                os.path.join(os.getcwd(), '.wit', 'image', read_last_commit)) and file != '.wit' and file != 'wit.py':
            list_of_added_file.append(file)
    return list_of_added_file


def changes_not_staged_for_commit(saved_path):
    list_of_not_staged_file = []
    for original_dir in os.listdir(os.getcwd()):
        for saved_dir in os.listdir(saved_path):
            if original_dir == saved_dir and os.path.isdir(original_dir):
                for f1 in os.listdir(os.path.join(os.getcwd(), original_dir)):
                    for f2 in os.listdir(os.path.join(saved_path, saved_dir)):
                        if f1 == f2:
                            f1_path = os.path.join(os.getcwd(), original_dir, f1)
                            f2_path = os.path.join(saved_path, saved_dir, f2)
                            if os.path.isdir(f1_path) and os.path.isdir(f2_path):
                                for original_sub_file in os.listdir(f1_path):
                                    for saved_sub_file in os.listdir(f2_path):
                                        if not (cmp(os.path.join(f1_path, saved_sub_file),
                                                    os.path.join(f2_path, original_sub_file))):
                                            list_of_not_staged_file.append(saved_sub_file)
                            else:
                                if not cmp(f1_path, f2_path):
                                    print(f2)
                                    list_of_not_staged_file.append(f2)
            elif original_dir == saved_dir and os.path.isfile(original_dir):
                if not cmp(original_dir, saved_dir):
                    list_of_not_staged_file.append(original_dir)
    return list_of_not_staged_file


def checkout(commit_id):
    with open((os.path.join(os.getcwd(), '.wit', 'references.txt')), 'r+') as refer_file:
        read_file = refer_file.read().split('\n')
        read_master = read_file[1].split('master=')[1].strip(' ')
        try:
            read_branch = read_file[2].split('=')[0].strip(' ')
        except IndexError:
            print('Your branch his master')
        if commit_id == 'master':
            commit_id = read_master
        elif commit_id == read_branch:
            commit_id = read_file[2].split('=')[1].strip(' ')
            try:
                with open(os.path.join(os.getcwd(), '.wit', 'activated.txt'), 'w') as actv_file:
                    actv_file.write(read_branch)
            except UnboundLocalError:
                pass
    staging_area = (os.path.join(os.getcwd(), '.wit', 'staging_area'))
    if len(changes_not_staged_for_commit(staging_area)) == 0 and len(changes_to_be_commited(staging_area)) == 0:
        for file in os.listdir(os.path.join(os.getcwd(), '.wit', 'image', commit_id)):
            for working_file in os.listdir(os.getcwd()):
                if file == working_file:
                    src = os.path.join(os.getcwd(), '.wit', 'image', commit_id, file)
                    dst = os.path.join(os.getcwd(), working_file)
                    if os.path.isdir(file):
                        copy_tree(src, dst)
                    elif os.path.isfile(file):
                        copyfile(src, dst)
        for file in os.listdir(os.path.join(os.getcwd(), '.wit', 'image', commit_id)):
            for staging_file in os.listdir(os.path.join(os.getcwd(), '.wit', 'staging_area')):
                if file == staging_file:
                    src = os.path.join(os.getcwd(), '.wit', 'image', commit_id, file)
                    dst = os.path.join(os.getcwd(), '.wit', 'staging_area', staging_file)
                    if os.path.isdir(file):
                        copy_tree(src, dst)
                    elif os.path.isfile(file):
                        copyfile(src, dst)
    else:
        raise WitException


def graph():
    x, y = 1, 1
    with open(os.path.join(os.getcwd(), '.wit', 'references.txt'), 'r') as r_file:
        read_r_file = r_file.readline().split('HEAD=')[1]
    circle1 = plt.Circle((x, y), 1)
    ax = plt.gca()
    ax.add_patch(circle1)
    ax.annotate(read_r_file, (x, y), fontsize=4, ha="center")
    image_dir = os.path.join(os.getcwd(), '.wit', 'image')
    plt.arrow(x, y, x + 2, y + 2)
    for file in os.listdir(image_dir):
        if os.path.isfile(image_dir + '\\' + file):
            if read_r_file.strip() == file.replace('.txt', ''):
                with open((image_dir + '\\' + file), 'r') as head_file:
                    x, y = x + 3, y + 3
                    read_head_file = head_file.readline().split('parent=')[1].strip('\n')
                    print(read_head_file)
                    circle2 = plt.Circle((x, y), 1)
                    ax.add_patch(circle2)
                    ax.annotate(read_head_file, (x, y), fontsize=4, ha="center")
                    read_r_file = read_head_file
                    if read_head_file is not None:
                        plt.arrow(x, y, x + 2, y + 2)
    plt.show()


def branch(NAME):
    reference_file = os.path.join(os.getcwd(), '.wit', 'references.txt')
    with open(reference_file, 'r') as open_reference_file:
        read_head = open_reference_file.readline().split('HEAD=')[1].strip('\n')
    print(read_head)
    with open(os.path.join(os.getcwd(), '.wit', 'references.txt'), 'a') as r_f:
        r_f.write(f' \n{NAME}={read_head}')


def merge(BRANCH_NAME):
    with open(os.path.join(os.getcwd(), '.wit', 'activated.txt'), 'r') as activated:
        read_active_branch = activated.read()
    chars = '123456789abcdef'
    commit_id_by_merge = ''.join([random.choice(chars) for _ in range(40)])
    image_path = os.path.join(os.getcwd(), '.wit', 'image')
    merge_file = os.path.join(image_path, commit_id_by_merge)
    text_commit = os.path.join(image_path, commit_id_by_merge + '.txt')
    os.mkdir(merge_file)
    with open((os.path.join(os.getcwd(), '.wit', 'references.txt')), 'r') as references_file:
        read_reference_file = references_file.read().split('\n')
        head_id = read_reference_file[0].split('HEAD=')[1].strip('\n ')
        read_master = read_reference_file[1]
        print(head_id)
        for i in read_reference_file:
            if BRANCH_NAME in i:
                branch_id = i.split('=')[1].strip()
                print(branch_id)
        with open(os.path.join(image_path, head_id + '.txt'), 'r') as doc_txt:
            parent_id = doc_txt.readline().split('parent=')[1].strip()
            if branch_id == head_id:
                with open(text_commit, 'w') as txt_id_commit_file:
                    txt_id_commit_file.write(
                        f'''parent={branch_id}
                    date= {datetime.datetime.now()}
                    message= merge command'''
                    )
                for staged_file in os.listdir(os.path.join(os.getcwd(), '.wit', 'staging_area')):
                    for commited_file in os.listdir(os.path.join(os.getcwd(), '.wit', 'image', branch_id)):
                        if staged_file == commited_file:
                            src = os.path.join(os.getcwd(), '.wit', 'image', branch_id, commited_file)
                            dst = os.path.join(os.getcwd(), '.wit', 'staging_area', staged_file)
                            if os.path.isdir(staged_file):
                                copy_tree(src, dst)
                            elif os.path.isfile(staged_file):
                                copyfile(src, dst)
            elif parent_id == head_id:
                with open(text_commit, 'w') as txt_id_commit_file:
                    txt_id_commit_file.write(
                        f'''parent={parent_id},{branch_id}
                    date= {datetime.datetime.now()}
                    message= merge'''
                    )
                for staged_file in os.listdir(os.path.join(os.getcwd(), '.wit', 'staging_area')):
                    for commited_file in os.listdir(os.path.join(os.getcwd(), '.wit', 'image', branch_id)):
                        if staged_file == commited_file:
                            src = os.path.join(os.getcwd(), '.wit', 'image', parent_id, commited_file)
                            dst = os.path.join(os.getcwd(), '.wit', 'staging_area', staged_file)
                            if os.path.isdir(staged_file):
                                copy_tree(src, dst)
                            elif os.path.isfile(staged_file):
                                copyfile(src, dst)
    with open((os.path.join(os.getcwd(), '.wit', 'references.txt')), 'w') as references_file:
        references_file.write(f'HEAD={commit_id_by_merge} \n')
        if BRANCH_NAME == read_active_branch:
            references_file.write(f'master={commit_id_by_merge} \n')
        else:
            references_file.write(f'{read_master} \n')
        references_file.write(f'{read_active_branch}={commit_id_by_merge}')


try:
    if sys.argv[1] == 'init':
        init()
except IndexError:
    pass

try:
    if sys.argv[1] == 'add':
        add(sys.argv[2])
except IndexError:
    pass

try:
    if sys.argv[1] == 'commit':
        commit(sys.argv[2])
except IndexError:
    pass

try:
    if sys.argv[1] == 'status':
        status()
except IndexError:
    pass

try:
    if sys.argv[1] == 'checkout':
        checkout(sys.argv[2])
except IndexError:
    pass

try:
    if sys.argv[1] == 'graph':
        graph()
except IndexError:
    pass

try:
    if sys.argv[1] == 'branch':
        branch(sys.argv[2])
except IndexError:
    pass


try:
    if sys.argv[1] == 'merge':
        merge(sys.argv[2])
except IndexError:
    pass
