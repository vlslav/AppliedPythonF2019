#!/usr/bin/env python
# coding: utf-8

from multiprocessing import Manager, Pool
import os


def word_count_inference(path_to_dir):
    '''
    Метод, считающий количество слов в каждом файле из директории
    и суммарное количество слов.
    Слово - все, что угодно через пробел, пустая строка "" словом не считается,
    пробельный символ " " словом не считается. Все остальное считается.
    Решение должно быть многопроцессным. Общение через очереди.
    :param path_to_dir: путь до директории с файлами
    :return: словарь, где ключ - имя файла, значение - число слов +
        специальный ключ "total" для суммы слов во всех файлах
    '''
    manager = Manager()
    result = manager.dict()
    files = os.listdir(path_to_dir)
    optimal_proc_cnt = len(files) if (os.cpu_count() > len(files)) else os.cpu_count()
    pool = Pool(optimal_proc_cnt)
    args_for_map = map(lambda x: {'path_to_dir': path_to_dir, 'file': x, 'result': result}, files)
    pool.map(worker, args_for_map)
    result['total'] = sum(result.values())
    return result


def worker(params):
    with open(os.path.join(params['path_to_dir'], params['file'])) as f:
        count = 0
        for line in f.readlines():
            count += len(line.split())
        params['result'][params['file']] = count
