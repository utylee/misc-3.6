import psutil
import time

for proc in psutil.process_iter():
    try:
        # print(proc.name())
        if proc.name().lower() == 'resolve':
            ret = proc.kill()
            print(f'resolve killed ret: {ret}')

    except:
        pass


# f = 'c:\\Users\\utylee\\davinci_proc_kill_result.txt'
# # f = './kill.txt'

# with open(f, 'w') as f:
#     # for proc in sorted(psutil.process_iter()):
#     # names = []
#     names = {} 
#     names_after = {} 
#     for proc in psutil.process_iter():
#         names.update({proc.name(): proc })
#         # names.append(proc.name())
#     # for proc in psutil.process_iter():
#     for name in sorted(names):
#         print(name)
#         f.write(f'{name}\n')
#         if name.lower() == 'resolve.exe':
#             f.write(f'{name}\n')
#             print(name)
#             ret = names[name].kill()
#             print(f'resolve.exe killed')
#             print(f'ret: {ret}')
    
    
#     print('\n\nafter killed')
#     f.write('\n\nafter killed\n')
#     time.sleep(5)
#     for proc in psutil.process_iter():
#         names_after.update({proc.name(): proc })
#     for name in sorted(names_after):
#         f.write(f'{name}\n')
#         print(name)

#     # for proc in psutil.process_iter():
#     #     print(proc.name())
#     #     f.write(f'{proc.name()}\n')
#     #     if proc.name().lower() == 'resolve.exe':
#     #         f.write(f'{proc.name()}\n')
#     #         print(proc.name())
#     #         # ret = proc.kill()
#     #         # print(f'ret: {ret}')
