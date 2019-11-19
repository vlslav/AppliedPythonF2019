#!/usr/bin/env python
# coding: utf-8
from time import sleep
from multiprocessing import Process, Queue
from threading import Thread
import os


class Task:
    """
    Задача, которую надо выполнить.
    В идеале, должно быть реализовано на достаточном уровне абстракции,
    чтобы можно было выполнять "неоднотипные" задачи
    """
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def perform(self):
        """
        Старт выполнения задачи
        """
        self._func(*self._args, **self._kwargs)


class TaskProcessor:
    """
    Воркер-процесс. Достает из очереди тасок таску и делает ее
    """
    def __init__(self, tasks_queue, timeout):
        """
        :param tasks_queue: Manager.Queue с объектами класса Task
        """
        self._tasks_queue = tasks_queue
        self._timeout = timeout

    def run(self):
        """
        Старт работы воркера
        """
        while not self._tasks_queue.empty():
            task = self._tasks_queue.get()
            thread = Thread(target=task.perform())
            thread.start()
            thread.join(self._timeout)


class TaskManager:
    """
    Мастер-процесс, который управляет воркерами
    """
    def __init__(self, tasks_queue, n_workers, timeout):
        """
        :param tasks_queue: Manager.Queue с объектами класса Task
        :param n_workers: кол-во воркеров
        :param timeout: таймаут в секундах, воркер не может работать дольше, чем timeout секунд
        """
        cpu_cnt = os.cpu_count()
        if (n_workers != cpu_cnt):
            print(f'Friend! This cnt of workers not optimal. Please try {cpu_cnt}')
        self._tasks_queue = tasks_queue
        self._n_workers = n_workers
        self._timeout = timeout
        self._run_processes = []

    def run(self):
        workers = [TaskProcessor(self._tasks_queue, self._timeout) for _ in range(self._n_workers)]
        for worker in workers:
            proc = Process(target=worker.run)
            self._run_processes.append(proc)
            proc.start()
        while not self._tasks_queue.empty():
            for i, proc in enumerate(self._run_processes):
                if not proc.is_alive():
                    proc = Process(target=workers[i].run)
                    proc.start()
