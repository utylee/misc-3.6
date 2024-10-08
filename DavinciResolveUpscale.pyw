import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
fusion = resolve.Fusion()
prjManager = resolve.GetProjectManager()
# print(projectManager)
prj = prjManager.LoadProject('Upscaling_1440')
print(prj)
# prj = prjManager.GetCurrentProject()

print(prj)
prelist = prj.GetRenderPresetList()
print(prelist)
ret = prj.LoadRenderPreset("Upscale_1440")
print(ret)
rf = prj.GetCurrentRenderFormatAndCodec()
print(rf)

# prj.SetSetting("timelineResolutionWidth", "2560")
# prj.SetSetting("timelineResolutionHeight", "1440")
# prj.SetSetting("timelineFrameRate", "60")


mediapool = prj.GetMediaPool()
print(mediapool)
# items = mediapool.ImportMedia(
#     "d:\\Videos\\The Finals 2024.02.02 - 21.18.56.19.mp4")
items = mediapool.ImportMedia(
    "d:\\Videos\\Test.mp4")
print(items)

timeline_count = prj.GetTimelineCount()
print(timeline_count)
if timeline_count > 0:
    for i in range(timeline_count):
        b = mediapool.DeleteTimelines(prj.GetTimelineByIndex(i+1))
        print('deleted timeline:', i + 1, ' result: ', b)

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

# print(media)
