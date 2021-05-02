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
    val = (1 - math.cos(t * 3.1415927)) / 2
    return start + ((end - start) * val)

def main():
    processScript('steamedhams.json', 'steamTest.mp4', 'a.png', './per.ttf')

def processScript(script, outFile, colorMaskFile=None, fontPath=None):
    words = ''
    oldLayout = []
    newLayout = []
    maxframe = 0
    minframe = None
    lastframe = 0
    nextFrame = 0
    lastFrame = 0

    # Initialize video
    fourcc = VideoWriter_fourcc(*'mp4v')
    video = VideoWriter(outFile, fourcc, 30.0, (1920, 1080))

    # Load file
    with open(script) as f:
        transcript = json.load(f)

    # Load color mask
    if (colorMaskFile):
        colorMask = np.array(Image.open(colorMaskFile))

    # Build the layouts
    for item in transcript['results']['items']:
        if item['type'] == 'pronunciation':
            newWord = item['alternatives'][0]['content']
            ic(newWord)
            # It's a word! Add it to the list and build a cloud
            words += newWord + ' '
            # Frame number at 30fps
            curFrame = int(float(item['start_time']) * 30)
            if (curFrame >= nextFrame):
                nextFrame = curFrame + 90  # 3 seconds @ 30fps
                try:
                    wordcloud = WordCloud(
                        width=1920,
                        height=1080,
                        scale=1,
                        font_path=fontpath,
                        random_state=82397,
                        prefer_horizontal=1,
                        stopwords=None,
                        max_words=5000,
                        max_font_size=150,
                        min_font_size=1,
                        color_func=lambda *args, **kwargs: 'white'
                    )
                    if fontPath != None:
                        wordcloud.font_path = fontPath
                    wordcloud.generate(words)
                except:
                    continue

                # Sync the old/new word lists for tweening
                newLayout = wordcloud.layout_
                for newLayoutWord in newLayout:
                    if any(wrd[0][0] == newLayoutWord[0][0] for wrd in oldLayout) == False:
                        oldLayout.append(
                            (newLayoutWord[0], 1, (540, 960), None, 'white'))

                # Generate the actual frames
                for vidFrame in range(lastFrame, curFrame, 1):
                    ic(vidFrame)
                    oldLayout.sort(key=lambda tup: tup[0][0])
                    newLayout.sort(key=lambda tup: tup[0][0])
                    frameLayout = []
                    frameRange = curFrame - lastFrame
                    t = (vidFrame - lastFrame) / frameRange
                    for i in range(0, len(newLayout)):
                        wordtup = (
                            newLayout[i][0],
                            int(tween(oldLayout[i][1], newLayout[i][1], t)),
                            (
                                int(tween(oldLayout[i][2][0],
                                    newLayout[i][2][0], t)),
                                int(tween(oldLayout[i][2][1],
                                    newLayout[i][2][1], t)),
                            ),
                            None,
                            'white'
                        )
                        frameLayout.append(wordtup)
                    wordcloud.layout_ = frameLayout
                    if (colorMaskFile):
                        image_colors = ImageColorGenerator(colorMask)
                        wordcloud.recolor(color_func=image_colors)
                    image = wordcloud.to_array()
                    video.write(image)
                oldLayout = newLayout
                lastFrame = curFrame
    video.release()
    ic('All done!')

main()
