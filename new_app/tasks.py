# from celery import shared_task
# import time
#
#
# @shared_task
# def add(x, y):
#     time.sleep(10)
#     return x + y
#
#
# @shared_task
# def mult(x, y):
#     time.sleep(13)
#     return x * y
#
#
# @shared_task
# def dev(x, y):
#     time.sleep(17)
#     return x / y
#
#
# def supertask(x=34, y=7):
#     funcs = [add, mult, dev]
#     tasks = []
#     for f in funcs:
#         tasks.append(f.delay(x, y))
#
#     ready = True
#     while ready:
#         for task in tasks:
#             if task.status == 'SUCCESS':
#                 print(f"Task completed. Result: {task.result}")
#                 tasks.remove(task)
#         if not tasks:
#             ready = False
#         else:
#             print('Tasks are in process. Waiting for 1 second')
#             time.sleep(1)
#     print('All tasks are finished')
