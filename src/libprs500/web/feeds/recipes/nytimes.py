#!/usr/bin/env  python

__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'
'''
nytimes.com
'''
import time, string
from libprs500.web.feeds.recipes import BasicNewsRecipe

class NYTimes(BasicNewsRecipe):
    
    title       = 'The New York Times'
    __author__  = 'Kovid Goyal'
    description = 'Daily news from the New York Times'
    timefmt = ' [%a, %d %b, %Y]'
    needs_subscription = True
    
    remove_tags_before = dict(name='h1')
    remove_tags_after  = dict(id='footer')
    remove_tags = [dict(attrs={'class':['articleTools', 'post-tools', 'side_tool']}), 
                   dict(id=['footer', 'navigation', 'archive', 'side_search', 'blog_sidebar', 'side_tool', 'side_index']), 
                   dict(name=['script', 'noscript'])]
    encoding = 'cp1252'
    no_stylesheets = True
    extra_css = 'h1 {font: sans-serif large;}\n.byline {font:monospace;}'
    html2lrf_options = ['--base-font-size', '14']
    
    def get_browser(self):
        br = BasicNewsRecipe.get_browser()
        if self.username is not None and self.password is not None:
            br.open('http://www.nytimes.com/auth/login')
            br.select_form(name='login')
            br['USERID']   = self.username
            br['PASSWORD'] = self.password
            br.submit()
        return br
    
    def parse_index(self):
        soup = self.index_to_soup('http://www.nytimes.com/pages/todayspaper/index.html')
        
        def feed_title(div):
            return ''.join(div.findAll(text=True, recursive=False)).strip()
        
        articles = {}
        key = None
        ans = []
        for div in soup.findAll(True, 
            attrs={'class':['section-headline', 'story', 'story headline']}):
            
            if div['class'] == 'section-headline':
                key = string.capwords(feed_title(div))
                articles[key] = []
                ans.append(key)
            
            elif div['class'] in ['story', 'story headline']:
                a = div.find('a', href=True)
                if not a:
                    continue
                url = self.print_version(a['href'])
                title = self.tag_to_string(a, use_alt=True).strip()
                description = ''
                pubdate = time.strftime('%a, %d %b', time.localtime())
                summary = div.find(True, attrs={'class':'summary'})
                if summary:
                    description = self.tag_to_string(summary, use_alt=False)
                
                feed = key if key is not None else 'Uncategorized'
                if not articles.has_key(feed):
                    articles[feed] = []
                if not 'podcasts' in url:
                    articles[feed].append(
                                  dict(title=title, url=url, date=pubdate, 
                                       description=description,
                                       content=''))
        ans = self.sort_index_by(ans, {'The Front Page':-1, 'Dining In, Dining Out':1, 'Obituaries':2})
        ans = [(key, articles[key]) for key in ans if articles.has_key(key)]
        return ans
    
    def print_version(self, url):
        return url + '?&pagewanted=print'
