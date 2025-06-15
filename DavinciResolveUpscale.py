import sys
import time
import psutil
import asyncio
import aiohttp
import json
import DaVinciResolveScript as dvr_script
import logging
import logging.handlers

REPORT_URL = 'http://localhost:8007/report_upscale'     # capture_watcher에게 보내는 겁니다

async def upscale(path, res):
    log.info('came into upscale()')
    resolve = dvr_script.scriptapp("Resolve")
    fusion = resolve.Fusion()
    prjManager = resolve.GetProjectManager()
    log.info(f'prjManager is {prjManager}')
    # prj = prjManager.LoadProject('Upscaling_1440')
    # prj = prjManager.LoadProject('Upscaling')
    prj = prjManager.LoadProject('Upscaling_2160') \
            if res=="2160" else prjManager.LoadProject('Upscaling_1440')
    log.info(f'prj is {prj}')
    # log.info(prj)
    log.info(f'res:{res}')
    # prj = prjManager.GetCurrentProject()

    prelist = prj.GetRenderPresetList()
    log.info(f'RenderPresetList:{prelist}')
    ret = prj.LoadRenderPreset('Upscaling_2160') \
            if res=="2160" else prj.LoadRenderPreset('Upscaling_1440')
    # ret = prj.LoadRenderPreset("Upscale_1440")
    log.info(f'ret is {ret}')
    # rf = prj.GetCurrentRenderFormatAndCodec()
    # print(rf)

    # prj.SetSetting("timelineResolutionWidth", "2560")
    # prj.SetSetting("timelineResolutionHeight", "1440")
    # prj.SetSetting("timelineFrameRate", "60")

    mediapool = prj.GetMediaPool()
    log.info(f'mediapool: {mediapool}')
    # items = mediapool.ImportMedia(
    #     "d:\\Videos\\The Finals 2024.02.02 - 21.18.56.19.mp4")
    log.info(f'path: {path}')
    item = mediapool.ImportMedia(
        path)
    # "d:\\Videos\\Test.mp4")
    log.info(f'importeditem: {item}')

    timeline_count = prj.GetTimelineCount()
    log.info(f'timeline_count: {timeline_count}')
    if timeline_count > 0:
        for i in range(timeline_count):
            b = mediapool.DeleteTimelines(prj.GetTimelineByIndex(i+1))
            # log.info('deleted timeline:', i + 1, ' result: ', b)
            log.info(f'deleted timeline:{i+1}, result: {b}')

    try:
        ret = mediapool.CreateTimelineFromClips(
            "MainTimeline", item)
        log.info(f'CreateTimelineFromClips: {ret}')
    except:
        pass

    timeline = prj.GetCurrentTimeline()

    # GetMediaPoolItem()                              --> MediaPoolItem      # Returns the media pool item corresponding to the timeline item if one exists.
    log.info(f'cur_timeline: {timeline}')

    # count = timeline.GetTrackCount("video")
    # print('count:', count)
    clips = timeline.GetItemListInTrack("video", 1)
    log.info(f'clips: {clips}')
    # ApplyGradeFromDRX(path, gradeMode, item1, item2, ...)--> Bool          # Loads a still from given file path (string) and applies grade to Timeline Items with gradeMode (int): 0 - "No keyframes", 1 - "Source Timecode aligned", 2 - "Start Frames aligned".
    ret = timeline.ApplyGradeFromDRX(
        "c:\\Users\\utylee\\Davinci Resolve Projects\\Blur_48_1.1.2.dpx", 0, clips)
        # "c:\\Users\\utylee\\Davinci Resolve Projects\\Blur_48_1.1.1.dpx", 0, clips)
    # "c:\\Users\\utylee\\Davinci Resolve Projects\\Blur_47_1.1.1.dpx", 0, clips)
    log.info(f'ApplyGradeFromDRX:{ret}:')
    render_id = prj.AddRenderJob()
    log.info(f'render_id: {render_id}')
    ret_start = prj.StartRendering(render_id)
    log.info(f'ret_renderstart: {ret_start}')

    # 시작되었음을 보고합니다
    status = {'JobStatus': 'Started', 'CompletionPercentage': 0}
    async with aiohttp.ClientSession() as sess:
        await sess.post(REPORT_URL, json=json.dumps(status))

    even = 0
    #{'JobStatus': Complete'', 'CompletionPercentage': 100, 'TimeTakenToRenderInMs': 17243}
    while True:
        status = prj.GetRenderJobStatus(render_id)
        log.info(f'renderJobStatus:{status}')
        time.sleep(2)
        if status['JobStatus'] == 'Complete':
            log.info('Completed!!')
            # 완료시에도 post하기로 합니다
            async with aiohttp.ClientSession() as sess:
                await sess.post(REPORT_URL, json=json.dumps(status))
            break
        if(even >= 5):          # 2*5초에 한번씩 퍼센테이지를 보고합니다
            even = 0
            async with aiohttp.ClientSession() as sess:
                await sess.post(REPORT_URL, json=json.dumps(status))
        even += 1

    #타임라인과 모든클립을 삭제합니다
    b = mediapool.DeleteTimelines(prj.GetTimelineByIndex(1))
    log.info(f'delete timeline result : {b}')


    mediapool_currentfolder = mediapool.GetCurrentFolder()
    log.info(f'media pool current folder: {mediapool_currentfolder}')
    mediapool_folder_clip_list = mediapool_currentfolder.GetClipList()
    log.info(f'mediapool_folder_clip_list: {mediapool_folder_clip_list}')
    
    ret = mediapool.DeleteClips(mediapool_folder_clip_list)
    log.info(f'delete ret: {ret}')

    # # mediapool.DeleteClips([item])
    # mediapool.DeleteClips(item)
    # print(f'delete clips result : {b}')

    # 프로젝트를 닫습니다
    # prjManager.CloseProject(prj)

async def main():
    log.info(f'this is DavinciResolveUpscale.py')

    if len(sys.argv) > 1:
        log.info(f'args: {sys.argv[1]}, {sys.argv[2]}')
        # Resolve.exe가 완전히 실행될 때까지(fuscript.exe 가 확인될 때까지)기다립니다
        while True:
            bFound = 0
            for proc in psutil.process_iter():
                # log.info(proc.name())
                if proc.name().lower() == 'fuscript.exe':
                    log.info(f'found fuscript.exe!')
                    bFound = 1
                    break
            if bFound == 1:
                break

            time.sleep(2)

        # fuscript.exe 가 확인됐어도 cpu load가 높을 경우 바로 준비가 안되기도 합니다
        time.sleep(4)
        await upscale(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    log_path = f'/home/utylee/davinci.log'
    # log_path = f'c:/Users/utylee/davinci.log'
    handler = logging.handlers.RotatingFileHandler(filename=log_path,
                                                   maxBytes=10*1024*1024,
                                                   backupCount=10)
    # handler.setFormatter(logging.Formatter('%[(asctime)s]-%(name)s-%(message)s'))
    # logging.Formatter.default_msec_format = '%s.%03d'
    formatter = logging.Formatter(
        '[%(asctime)s.%(msecs)03d]-%(message)s', "%y%m%d %H:%M:%S")
    # formatter.default_msec_format = '%s.%03d'
    handler.setFormatter(formatter)
    # handler.setFormatter(logging.Formatter(
    # '[%(asctime)s]-%(message)s', "%y-%m-%d %H:%M:%S:%f").default_msec_format('%s.%03d')))
    log = logging.getLogger('log')
    log.addHandler(handler)
    # log.terminator = ''
    log.setLevel(logging.DEBUG)

    asyncio.run(main())

# if __name__ == "__main__":
#     # path를 넘겨받습니다
#     if len(sys.argv) > 1:
#         print(sys.argv[1])
#         # Resolve.exe가 완전히 실행될 때까지(fuscript.exe 가 확인될 때까지)기다립니다
#         while True:
#             bFound = 0
#             for proc in psutil.process_iter():
#                 print(proc.name())
#                 if proc.name().lower() == 'fuscript.exe':
#                     print(f'found fuscript.exe!')
#                     bFound = 1
#                     break
#             if bFound == 1:
#                 break

#             time.sleep(2)

#         upscale(sys.argv[1])

