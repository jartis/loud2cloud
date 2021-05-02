import os
from os import path
from wordcloud import WordCloud, ImageColorGenerator
import json
from icecream import ic
import math
import numpy as np
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from PIL import *

def tween(start, end, t):
    xv = (1 - math.cos(t * 3.1415927)) / 2
    return start + ((end - start) * xv)

def main():
    words = ''
    layouts = {}
    maxframe = 0
    minframe = None
    lastframe = 0
    rScaling = 0.5
    fontpath = './per.ttf'
    # Load file
    with open('alanwatts.json') as f:
        transcript = json.load(f)

    alan_coloring = np.array(Image.open('a.png'))

    # Build the layouts
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
                    width=1920,
                    height=1080,
                    scale=1,
                    font_path=fontpath,
                    #random_state=1781,
                    relative_scaling=rScaling,
                    prefer_horizontal=1,
                    stopwords = None,
                    max_words=5000,
                    #mode = 'RGBA',
                    max_font_size = 150,
                    min_font_size = 1
                ).generate(words)
            except:
                continue
            if (wordcloud.layout_ in layouts.values()) == False: # Skip duplicate layouts (stop words)
                layouts[frame] = wordcloud.layout_
            if minframe == None:
                minframe = frame
            maxframe = frame
            # image = wordcloud.to_file(str(frame) + '.png')
    
    ic('Done with words')

    fourcc = VideoWriter_fourcc(*'mp4v')
    video = VideoWriter('alan.mp4', fourcc, 30.0, (1920, 1080))

    # Build the frames
    for fr in range(0, maxframe):
        ic(f'New Frame {fr}/{maxframe}')
        wordcloud = WordCloud(
            width=1920,
            height=1080,
            scale=1,
            color_func=lambda *args, **kwargs: "yellow",
            font_path=fontpath,
            relative_scaling=rScaling,
            #random_state=1781,
            prefer_horizontal=1,
            stopwords = None,
            max_font_size = 256,
            min_font_size = 2
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
            oldLayout.sort(key=lambda tup: tup[0][0])
            newLayout.sort(key=lambda tup: tup[0][0])
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
                    if (len(newLayout) >= i+2):
                        if (oldLayout[i][0][0] != newLayout[i][0][0]):
                            j = i+1
                    wordtup = (
                        oldLayout[i][0],
                        int(tween(oldLayout[i][1], newLayout[j][1], t)),
                        (
                            int(tween(oldLayout[i][2][0], newLayout[j][2][0], t)),
                            int(tween(oldLayout[i][2][1], newLayout[j][2][1], t)),
                        ),
                        None,
                        'yellow'
                    )
                    tLayout.append(wordtup)
                    wordcloud.layout_ = tLayout
        image_colors = ImageColorGenerator(alan_coloring)
        wordcloud.recolor(color_func = image_colors)
        #image = wordcloud.to_file('hams3/' + str(fr) + '.png')
        image = wordcloud.to_array()
        video.write(image)
    video.release()

main()