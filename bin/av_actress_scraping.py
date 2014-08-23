#! /usr/bin/python
#- coding:utf-8 -*-
"""
AV女優の情報を取得するコード

TopPage: http://actress.dmm.co.jp/-/top/

TopPageから階層を下って、ページをparseしていく
"""
import logging, time, json, codecs, urllib2, lxml.html
import actress_page_parser as parser

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#sys.stderrへ出力するハンドラーを定義
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
#rootロガーにハンドラーを登録する
logger.addHandler(sh)

global top_page_url
top_page_url = 'http://actress.dmm.co.jp/-/top/'

global page_prefix
page_prefix = 'http://actress.dmm.co.jp' 

global user_agent
user_agent='Mozilla/5.0'

global dev_save_path
dev_save_path='./tmp_saved'

global path_to_save_fetched_data
path_to_save_fetched_data = '../fetched_data/list_of_fetched.json'

def GetTopPage(url_page):
    req = urllib2.Request(url_page)
    req.add_header("User-agent", user_agent)
    top_html_data = urllib2.urlopen(req).read() 
    top_html_data = unicode(top_html_data, 'euc-jp')
    
    return top_html_data 

def SaveTmpFile(top_html_data):
    """
    開発用のため、ローカルにファイル保存する
    """
    with codecs.open(dev_save_path, 'w', 'utf-8') as f:
        f.write(top_html_data)

def LoadLocalFile():
    with codecs.open(dev_save_path, 'r', 'utf-8') as f:
        html_data=f.read()
    return html_data

def GetActressIndexPage(top_html_data):
    """
    ５０音順ではじめるインデックスページを取得する。
    具体的には、このページを取得する　http://actress.dmm.co.jp/-/list/=/keyword=a/
    """
    link_index_list=[]
    
    top_node = lxml.html.fromstring(top_html_data)
    actress_index_page_list = top_node.xpath("//html/body[@name='dmm_main']/table[@id='w']/tr/td[@id='su']/div[@id='side-l']/div[@class='side-contents']/div[@class='side-menu']/table[@class='menu_aiueo']/tr/td/a")
    for index_page_node in actress_index_page_list:
        link_to_index_page = index_page_node.attrib['href']
        url_link_to_page = u'{}{}'.format(page_prefix, link_to_index_page)        
        link_index_list.append(url_link_to_page)
        
        logger.debug('{}'.format(url_link_to_page))      
        time.sleep(30)
    return link_index_list

def UpdateWithAllIndexPage(link_index_list):
    """
    全インデックスページを取得する
    """
    all_index_list = []

    for page_url in link_index_list:
        html_data = GetTopPage(page_url)
        page_node = lxml.html.fromstring(html_data) 
        next_page_info_nodes_list = page_node.xpath("//body[@name='dmm_main']/table[@id='w']/tr/td[@id='mu']/div[@class='line']/a") 
        next_page_list = ['{}{}'.format(page_prefix, i.attrib['href']) for i in next_page_info_nodes_list]
        
        all_index_list = all_index_list + next_page_list 
        
        logger.debug('link list is updated')
        time.sleep(30)
    
    return all_index_list 

def IndexPageParser(link_index_list):
    """
    インデックスページの解析
    女優の個人ページへのアドレス一覧を取得する
    """
    actress_page_list = []  # 各女優ページへのリンクリスト
    
    for page_url in link_index_list:
        html_data = GetTopPage(page_url)
        page_node = lxml.html.fromstring(html_data) 
        actress_nodes = page_node.xpath("//body[@name='dmm_main']/table[@id='w']/tr/td[@id='mu']/table/tr[@class='list']/td[@class='pic']/a[@href]") 
        tmp_actress_list = [i.attrib['href'] for i in actress_nodes]
        
        actress_page_list = actress_page_list + tmp_actress_list
        
    return actress_page_list

def ActressPageParser(actress_page_list):
    """
    女優の個人ページを解析する
    INPUT: list actress_page_list
    
    RETURN:
        actress_info_list list [ actress_info_map ]
    """
    actress_info_list = []

    for actress_index, actress_page in enumerate(actress_page_list):
      	logger.debug(actress_page)	

        actress_info_map = parser.Main(actress_page) 
        actress_info_list.append(actress_info_map) 
        
        with codecs.open('../fetched_data/{}.json'.format(actress_index), 'w', 'utf-8') as f:
            json.dump(actress_info_map, f, indent=4, ensure_ascii=False)
        logger.debug('saved to ../fetched_data/{}.json'.format(actress_index))

    return actress_info_list

def Main():
    #top_html_data = GetTopPage(top_page_url)
    #link_index_list = GetActressIndexPage(top_html_data)
    #all_index_list = UpdateWithAllIndexPage(link_index_list)
    #actress_page_list = IndexPageParser(all_index_list)  # 女優の個人ページ一覧を取得する
    #with codecs.open('all_page.json', 'w', 'utf-8') as f: json.dump(actress_page_list, f, indent=4)
    with codecs.open('all_page.json', 'r', 'utf-8') as f: actress_page_list = json.load(f)
    actress_info_list = ActressPageParser(actress_page_list)

    with codecs.open(path_to_save_fetched_data, 'w', 'utf-8')  as f: json.dump(actress_info_list, f,
                                                                               indent=4, ensure_ascii=False)

if __name__=="__main__":
    Main()
