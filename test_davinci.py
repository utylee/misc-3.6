import asyncio
# import uvloop
import DaVinciResolveScript as dvr_script
import time

SUDO = 'sudo'
DAVINCI_PATH = '/mnt/c/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe'
PYTHONW_PATH = '/mnt/c/Program Files/Python36/python.exe'
KILL_PY = './win32_proc_kill.py'


async def test():
    resolve = dvr_script.scriptapp("Resolve")
    fusion = resolve.Fusion()
    prjManager = resolve.GetProjectManager()
    # print(projectManager)
    prj = prjManager.LoadProject('Upscaling_1440')
    print(prj)
    # prj = prjManager.GetCurrentProject()

    # print(prj)
    prelist = prj.GetRenderPresetList()
    # print(prelist)
    ret = prj.LoadRenderPreset("Upscale_1440")
    # print(ret)
    # rf = prj.GetCurrentRenderFormatAndCodec()
    # print(rf)

    # prj.SetSetting("timelineResolutionWidth", "2560")
    # prj.SetSetting("timelineResolutionHeight", "1440")
    # prj.SetSetting("timelineFrameRate", "60")


    mediapool = prj.GetMediaPool()
    print(f'mediapool: {mediapool}')
    mediapool_rootfolder = mediapool.GetRootFolder()
    print(f'media pool root folder: {mediapool_rootfolder}')
    mediapool_currentfolder = mediapool.GetCurrentFolder()
    print(f'media pool current folder: {mediapool_currentfolder}')
    mediapool_folder_clip_list = mediapool_currentfolder.GetClipList()
    print(f'mediapool_folder_clip_list: {mediapool_folder_clip_list}')
    # items = mediapool.ImportMedia(
    #     "d:\\Videos\\The Finals 2024.02.02 - 21.18.56.19.mp4")
    items = mediapool.ImportMedia(
        "d:\\Videos\\Test.mp4")
    print(items)
    
    ret = mediapool.DeleteClips(mediapool_folder_clip_list)
    print(f'delete ret: {ret}')

    # timeline_count = prj.GetTimelineCount()
    # print(timeline_count)
    # if timeline_count > 0:
    #     for i in range(timeline_count):
    #         b = mediapool.DeleteTimelines(prj.GetTimelineByIndex(i+1))
    #         print('deleted timeline:', i + 1, ' result: ', b)


    # ret = mediapool.DeleteFolders([mediapool_currentfolder])
    # print(f'delete ret: {ret}')

    '''

    try:
        ret = mediapool.CreateTimelineFromClips(
            "MainTimeline", items)
        print(ret)
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
        "c:\\Users\\utylee\\Davinci Resolve Projects\\Blur_47_1.1.1.dpx", 0, clips)
    print('ApplyGradeFromDRX:ret:', ret)
    render_id = prj.AddRenderJob()
    print('render_id' + render_id)
    prj.StartRendering(render_id)

    while True:
        status = prj.GetRenderJobStatus(render_id)
        print(status)
        time.sleep(2)
        if status['JobStatus'] == 'Complete':
            print('Completed!!')
            break


    prjManager.CloseProject(prj)

    # print(media)
    '''


async def main():

    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH)
    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH, '  -nogui')
    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH, stdout=asyncio.subprocess.PIPE)
    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH, stdout=asyncio.subprocess.DEVNULL)
    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=asyncio.subprocess.DEVNULL)
    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=asyncio.subprocess.PIPE)
    process = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=None)
    # process = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=None)
    # process = await asyncio.create_subprocess_exec(SUDO, DAVINCI_PATH)
    # process = await asyncio.create_subprocess_exec(SUDO, DAVINCI_PATH, '-nogui', stdout=None)
    # process = await asyncio.create_subprocess_exec(SUDO, '-S', DAVINCI_PATH, '-nogui', stdout=asyncio.subprocess.DEVNULL)
    # process = await asyncio.create_subprocess_exec(SUDO, '-S', DAVINCI_PATH, '-nogui', stdout=asyncio.subprocess.PIPE)
    # await process.wait()
    # print(f'process is {process}')
    await asyncio.sleep(30)
    process = await asyncio.create_subprocess_exec(PYTHONW_PATH, KILL_PY, stdout=None)
    # process = await asyncio.create_subprocess_exec(PYTHONW_PATH, KILL_PY, stdout=asyncio.subprocess.DEVNULL)
    # process.terminate()
    await asyncio.sleep(3)
    # print('aa')


asyncio.run(test())
# uvloop.run(main())
