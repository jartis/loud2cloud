import os
from os import path
from wordcloud import WordCloud
import json
from icecream import ic

words = ''
layouts = {}
maxframe = 0
minframe = None
# times = []
with open('asrOutput.json') as f:
    transcript = json.load(f)

def tween(start, end, t):
    return start + (t * (end - start))

for item in transcript['results']['items']:
    if item['type'] == 'pronunciation':
        w = item['alternatives'][0]['content'] + ' '
        ic(f'New Word: {w}')
        # It's a word! Add it to the list and build a cloud
        words += w + ' '
        frame = int(float(item['start_time']) * 30)  # Frame number at 30fps
        # times.append(frame)
        try:
            wordcloud = WordCloud(
                width=960,
                height=540,
                scale=2,
                color_func=lambda *args, **kwargs: "white",
                font_path='./dunkin.otf',
                random_state=1781,
                prefer_horizontal=1
            ).generate(words)
        except:
            continue
        layouts[frame] = wordcloud.layout_
        if minframe == None:
            minframe = frame
        maxframe = frame
        # image = wordcloud.to_file(str(frame) + '.png')

ic('Done with words')

for fr in range(0, maxframe):
    ic('New Frame')
    wordcloud = WordCloud(
        width=960,
        height=540,
        scale=2,
        color_func=lambda *args, **kwargs: "white",
        font_path='./dunkin.otf',
        random_state=1781,
        prefer_horizontal=1
    )
    if (fr < minframe):
        wordcloud.layout_ = layouts[minframe]
    elif fr == maxframe:
        wordcloud.layout_ = layouts[maxframe]
    else:
        oldLayout = []
        newLayout = []
        oldfr = -1
        newfr = -1
        for ofi in range(fr, 0, -1):
            if ofi in layouts.keys():
                if isinstance(layouts[ofi], list):
                    oldLayout = layouts[ofi]
                else:
                    oldLayout = [layouts[ofi]]
                oldfr = ofi
                break
        for nfi in range(fr+1, maxframe, 1):
            if nfi in layouts.keys():
                if isinstance(layouts[nfi], list):
                    newLayout = layouts[nfi]
                else:
                    newLayout = [layouts[nfi]]
                newfr = nfi
                break
        # tween the list here
        oldLayout.sort(key=lambda tup: tup[0])
        newLayout.sort(key=lambda tup: tup[0])
        tLayout = []
        t = fr - oldfr
        if t < 0:
            wordcloud.layout = oldLayout
            # Before the first word
        elif t >= maxframe:
            wordcloud.layout = newLayout
            # At or after the last frame
        else:
            frange = newfr - oldfr
            t = t / frange
            for i in range(0, len(oldLayout)):
                # j for new, i for old
                j = i
                if (oldLayout[i][0] != newLayout[i][0]):
                    j = i+1
                wordtup = (
                    oldLayout[i][0],
                    tween(oldLayout[i][1], newLayout[j][1], t),
                    (
                        tween(oldLayout[i][2][0], newLayout[j][2][0], t),
                        tween(oldLayout[i][2][1], newLayout[j][2][1], t),
                    ),
                    None,
                    'white'
                )
                tLayout.append(wordtup)
                wordcloud.layout_ = tLayout
    image = wordcloud.to_file(str(fr) + '.png')

