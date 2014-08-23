#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, re, logging, time, json, codecs, urllib2, lxml.html

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#sys.stderrへ出力するハンドラーを定義
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
#rootロガーにハンドラーを登録する
logger.addHandler(sh)

global page_prefix
page_prefix = 'http://actress.dmm.co.jp' 

global user_agent
user_agent='Mozilla/5.0'

def LoadDevData():
    with codecs.open('./dev_data/actress_page', 'r', 'utf-8') as f:
        actress_page = f.read()

    return actress_page

def GetTopPage(url_page):
    req = urllib2.Request(url_page)
    req.add_header("User-agent", user_agent)
    top_html_data = urllib2.urlopen(req).read() 
    top_html_data = unicode(top_html_data, 'euc-jp')

    return top_html_data

def GetActressInfo(actress_page):
    """
    女優の情報と出演ビデオの情報を取得する
    
    RETURN:
    map actress_info_map { 'actress_name': actress_name,
                           'birth', 
                           'start_charta', 
                           'blood_type', 
                           'body_size', 
                           'place_from', 
                           'intresting', 
                           'actress_image_src',
                            'fetched_video_map_list': list [ fetched_video_map {'video_name', 'published_date'} ]
                            }
    """
    actress_page_node = lxml.html.fromstring(actress_page) 
    
    actress_info_node = actress_page_node.xpath("//body[@name='dmm_main']/table[@id='w']/tr/td[@id='mu']")[0]
   
    basic_info_node = actress_info_node.xpath("table[@width='100%'][@border='0'][@align='center']")[0]
    actress_name = (basic_info_node.xpath("tr/td/table/tr/td[@class='t1']/h1")[0]).text
    actress_image_src = basic_info_node.xpath("tr/td/table/tr/td/img[@src]")[0]  #  顔写真のurlを取得
    img_url = actress_image_src.attrib['src']
    actress_info_map = {}
    actress_info_map['actress_name'] = actress_name
    actress_info_map['actress_image_src'] = img_url 
    
    basic_info_map = GetBasicInfo(basic_info_node)
    fetched_video_map_list = GetVideoInfo(actress_info_node)
   
    actress_info_map.update(basic_info_map)
    actress_info_map['video_info'] = fetched_video_map_list

    return actress_info_map

def GetVideoInfo(actress_info_node):
    """
    ビデオ一覧情報を取得する
    """
    fetched_video_indo_list = []
    
    video_list_index_list = actress_info_node.xpath("table[@width='100%'][@style='margin-bottom:10px;']/tr/td/a")
    video_list_url = ['{}{}'.format(page_prefix, link.attrib['href']) for link in video_list_index_list]

    video_info_url = list(set(video_list_url))
    video_page_prefix=video_info_url[0].split('page=')[0]
    video_page_one='{}page=1'.format(video_page_prefix)
    video_list_url.append(video_page_one) 
    
    for video_info_url in video_list_url:
        if '#list' in video_info_url: continue
        
        video_html = GetTopPage(video_info_url)
        logger.debug('{}'.format(video_info_url))
        time.sleep(60)
        
        video_info_page_top_node = lxml.html.fromstring(video_html)
        per_video_info_list = video_info_page_top_node.xpath("//body[@name='dmm_main']/table[@id='w']/tr/td[@id='mu']/table[@style='margin-bottom:15px;']/tr")
        # ビデオ情報を取得する
        for video_index, per_video_info_node in enumerate(per_video_info_list):
            if video_index==0: continue 
            video_name_node = per_video_info_node.xpath("td[@class='info_works1']/a")[0]  # ビデオ名を取得
            video_url = video_name_node.attrib['href']
            video_name = video_name_node.text
            published_date = list(per_video_info_node)[7].text 

            per_video_info_map = {'video_name': video_name,
                                  'published_date': published_date} 

            fetched_video_indo_list.append(per_video_info_map)

        break

    return fetched_video_indo_list

def GetBasicInfo(basic_info_node):
    actress_attr_info_list = basic_info_node.xpath("tr/td/table/tr/td/table//tr/td[@nowrap]")

    birth = actress_attr_info_list[1].text
    start_charta = actress_attr_info_list[3].text
    blood_type = actress_attr_info_list[5].text
    body_size = actress_attr_info_list[7].text
    place_from = actress_attr_info_list[9].text
    intresting = actress_attr_info_list[11].text

    tall = None
    west = None
    bust = None
    bust_cup = None
    hip = None

    try:
        t, b, w, h = body_size.split()
        tall = int(t.strip('T').strip('cm'))
        waist = int(w.strip('W').strip('cm'))
        hip = int(h.strip('H').strip('cm'))
        bust = int(b.split('cm(')[0].strip('B'))
        bust_cup = b.split('cm(')[1].strip(')')
    except:
        pass

    basic_info_map = {'bitrh': birth, 
                      'start_charta': start_charta,
                      'blood_type': blood_type,
                      'body_size': body_size,
                      'bust': bust,
                      'bust_cup': bust_cup,
                      'tall': tall,
                      'hip': hip,
                      'waist': waist,
                      'place_from': place_from,
                      'intresting': intresting}

    return basic_info_map

def Main(actress_page):
    actress_info_map = GetActressInfo(actress_page)

    return actress_info_map

if __name__=='__main__':
    actress_page = LoadDevData()
    actress_info_map = GetActressInfo(actress_page)
    with codecs.open('actress_info_map.json', 'w', 'utf-8') as f:
        json.dump(actress_info_map, f, indent=4)
