import sys
import time
import psutil
import asyncio
import aiohttp
import json
import DaVinciResolveScript as dvr_script

REPORT_URL = 'http://localhost:8007/report_upscale'

async def upscale(path, res):
    resolve = dvr_script.scriptapp("Resolve")
    fusion = resolve.Fusion()
    prjManager = resolve.GetProjectManager()
    # print(projectManager)
    # prj = prjManager.LoadProject('Upscaling_1440')
    # prj = prjManager.LoadProject('Upscaling')
    prj = prjManager.LoadProject('Upscaling_2160') \
            if res=="2160" else prjManager.LoadProject('Upscaling_1440')
    print(prj)
    print(f'res:{res}')
    # prj = prjManager.GetCurrentProject()

    print(prj)
    prelist = prj.GetRenderPresetList()
    print(prelist)
    ret = prj.LoadRenderPreset('Upscaling_2160') \
            if res=="2160" else prj.LoadRenderPreset('Upscaling_1440')
    # ret = prj.LoadRenderPreset("Upscale_1440")
    print(ret)
    # rf = prj.GetCurrentRenderFormatAndCodec()
    # print(rf)

    # prj.SetSetting("timelineResolutionWidth", "2560")
    # prj.SetSetting("timelineResolutionHeight", "1440")
    # prj.SetSetting("timelineFrameRate", "60")

    mediapool = prj.GetMediaPool()
    print(f'mediapool: {mediapool}')
    # items = mediapool.ImportMedia(
    #     "d:\\Videos\\The Finals 2024.02.02 - 21.18.56.19.mp4")
    item = mediapool.ImportMedia(
        path)
    # "d:\\Videos\\Test.mp4")
    print(f'importeditem: {item}')

    timeline_count = prj.GetTimelineCount()
    print(f'timeline_count: {timeline_count}')
    if timeline_count > 0:
        for i in range(timeline_count):
            b = mediapool.DeleteTimelines(prj.GetTimelineByIndex(i+1))
            print('deleted timeline:', i + 1, ' result: ', b)

    try:
        ret = mediapool.CreateTimelineFromClips(
            "MainTimeline", item)
        print('CreateTimelineFromClips: {ret}')
    except:
        pass

    timeline = prj.GetCurrentTimeline()

    # GetMediaPoolItem()                              --> MediaPoolItem      # Returns the media pool item corresponding to the timeline item if one exists.
    print('cur_timeline: ', timeline)

    # count = timeline.GetTrackCount("video")
    # print('count:', count)
    clips = timeline.GetItemListInTrack("video", 1)
    print('clips:', clips)
    # ApplyGradeFromDRX(path, gradeMode, item1, item2, ...)--> Bool          # Loads a still from given file path (string) and applies grade to Timeline Items with gradeMode (int): 0 - "No keyframes", 1 - "Source Timecode aligned", 2 - "Start Frames aligned".
    ret = timeline.ApplyGradeFromDRX(
        "c:\\Users\\utylee\\Davinci Resolve Projects\\Blur_48_1.1.1.dpx", 0, clips)
    # "c:\\Users\\utylee\\Davinci Resolve Projects\\Blur_47_1.1.1.dpx", 0, clips)
    print('ApplyGradeFromDRX:ret:', ret)
    render_id = prj.AddRenderJob()
    print('render_id' + render_id)
    prj.StartRendering(render_id)


    even = 0
    #{'JobStatus': Complete'', 'CompletionPercentage': 100, 'TimeTakenToRenderInMs': 17243}
    while True:
        status = prj.GetRenderJobStatus(render_id)
        print(status)
        time.sleep(2)
        if status['JobStatus'] == 'Complete':
            print('Completed!!')
            # 완료시에도 post하기로 합니다
            async with aiohttp.ClientSession() as sess:
                await sess.post(REPORT_URL, json=json.dumps(status))
            break
        if(even >= 5):          # 2*5초에 한번씩 퍼센테이지를 보고합니다
            even = 0
            async with aiohttp.ClientSession() as sess:
                await sess.post(REPORT_URL, json=json.dumps(status))
        even += 1

    #타임라인과 클립을 모두 삭제합니다
    b = mediapool.DeleteTimelines(prj.GetTimelineByIndex(1))
    print(f'delete timeline result : {b}')
    # mediapool.DeleteClips([item])
    mediapool.DeleteClips(item)
    print(f'delete clips result : {b}')

    # 프로젝트를 닫습니다
    # prjManager.CloseProject(prj)

async def main():
    if len(sys.argv) > 1:
        print(f'args: {sys.argv[1]}, {sys.argv[2]}')
        # Resolve.exe가 완전히 실행될 때까지(fuscript.exe 가 확인될 때까지)기다립니다
        while True:
            bFound = 0
            for proc in psutil.process_iter():
                # print(proc.name())
                if proc.name().lower() == 'fuscript.exe':
                    print(f'found fuscript.exe!')
                    bFound = 1
                    break
            if bFound == 1:
                break

            time.sleep(2)

        await upscale(sys.argv[1], sys.argv[2])

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

