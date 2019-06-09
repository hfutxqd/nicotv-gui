#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import the appJar library
from appJar import gui
from appJar.appjar import ItemLookupError
from nicotv_cli import detail
from nicotv_cli import search
from urllib import parse
import threading
import json

video_infos = []


def do_search():
    global video_infos
    keyword = app.getEntry("动漫名称")
    video_infos = search.search(keyword)
    video_titles = []
    for video_info in video_infos:
        video_titles.append('{}-{}'.format(video_info['name'], video_info['status']))
    app.updateListBox("list", video_titles)


def lst_changed():
    selected = app.getListBoxPos('list')
    if len(selected) > 0:
        selected = selected[0]
        video_info = video_infos[selected]
        show_video_list(video_info)


def load_details(video_info):
    channels = detail.get_video_channels(video_info['url'])
    print(channels)
    app.emptyCurrentContainer()
    app.startTabbedFrame("TabbedFrame")
    channel_index = 1
    for channel in channels:
        app.startTab('源{}'.format(channel_index))

        video_details = []
        detail_list = []
        load_title = 'loading_text:' + str(channel_index)
        try:
            app.addLabel(load_title, '正在解析')
        except:
            pass
        for url in channel:
            video_detail = detail.get_video_detail(url)
            video_details.append(video_detail)
            detail_list.append(video_detail['episode'])
            print(video_detail)
            app.setLabel(load_title, '正在解析 源{}-{}'.format(channel_index, video_detail['episode']))
        index = 0
        for info in video_details:
            if info['title'] and info['episode']:
                app.addWebLink(title='源{}'.format(channel_index) + ':' + info['episode'], page='https://player.xqd.one/?data={}'.format(
                    parse.quote_plus(json.dumps(info, ensure_ascii=False), encoding='utf-8')), row=index // 6, column=index % 6)
                index += 1
        if index == 0:
            app.setLabel(load_title, '没有内容')
        else:
            app.removeLabel(load_title)
        channel_index += 1
        app.stopTab()
    app.stopTabbedFrame()


def show_video_list(video_info):
    try:
        app.destroySubWindow("video_list")
    except:
        pass
    print(video_info)
    app.startSubWindow("video_list", modal=True)
    app.title = video_info['name']
    app.setSize(800, 600)
    app.addLabel('loading_text', text='正在加载...')
    app.showSubWindow('video_list')
    threading.Thread(target=load_details, args=(video_info, )).start()


app = gui()
app.title = '动漫搜索'
app.setSize(400, 300)
app.addLabelEntry("动漫名称")
app.addButton('搜索', func=do_search)
app.addListBox("list", [])
app.setListBoxChangeFunction("list", lst_changed)

app.go()
