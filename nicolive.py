# -*- coding: utf-8 -*-

# ニコ生クラス

import re
import urllib2
from BeautifulSoup import BeautifulSoup

class NicoLive:
  
  TABS = ['common', 'try', 'live', 'req', 'r18']
  WATCH_URL_REGEX = re.compile(r'(http://live.nicovideo.jp)?/watch/lv(\d+)')
  
  def __init__(self):
    self.opener = urllib2.build_opener()

  def fetch_lives(self):
    liveid_set = set()
    for tab in self.TABS:
      url = 'http://live.nicovideo.jp/recent?tab=%s&p=1' % tab
      self.fetch_live_ids_from_html(url, liveid_set)
    live_list = []
    for live_id in sorted(list(liveid_set)):
      live_detail = self.fetch_live_detail_from_live_id(live_id)
      live_list.append(live_detail)
    print live_list

  def fetch_live_ids_from_html(self, url, id_set):
    html = self.opener.open(url).read()
    soup = BeautifulSoup(html)
    
    for a in soup.findAll('a', href = self.WATCH_URL_REGEX):
      m = self.WATCH_URL_REGEX.match(a['href'])
      if m:
        id_set.add(int(m.group(2)))

  def fetch_live_detail_from_live_id(self, live_id):
    url = 'http://live.nicovideo.jp/watch/lv%d' % live_id
    html = self.opener.open(url).read()
    soup = BeautifulSoup(html)
    
    tmdl = soup.find('div', {'class': 'tmdl'})
    # tmdlの中は、詳細コメント・主・コミュニティ・注意書きの順で<p>が入ってる
    desct, nusit, comt, txt10 = tmdl.findAll('p')
    desc = desct.contents[0]
    nusi = nusit.find('span', {'class': 'nicopedia'}).contents[0]
    com_url = comt.a['href']
    com_id = com_url[com_url.rindex('/') + 1:]
    com_text = comt.a.contents[0]

    return {'live_id': live_id,
            'desc': desc,
            'nusi': nusi,
            'com_id': com_id,
            'com_text': com_text}
