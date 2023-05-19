#!/usr/bin/python3
# -*- coding: utf-8 -*-
import PyRSS2Gen
import feedparser
import datetime
import sys
LOG = r'./script.log'

URL = "https://hackermonica.me/rss"


def write_log(string):
    f = open(LOG, 'a')
    f.write(string + "\n")
    f.close()

def readRss():
    global myfeed
    myfeed = feedparser.parse("./rss.xml")

def writeRss(m_title, m_link, m_description):
    write_log("break point0")
    readRss()
    write_log("break point1")
    global myfeed
    myitems = []
    for item in myfeed.entries:
        myitems.append(PyRSS2Gen.RSSItem(
            title=item.title,
            description=item.description,
            pubDate=item.published,
            link=item.link,
            guid=item.guid
        ))
    write_log("break point2")
    # remove oldest item for the limit of 10
    myitems.sort(key=lambda x: x.pubDate, reverse=True)
    while len(myitems) > 10:
        myitems.pop()
    # add new item
    myitems.insert(0,PyRSS2Gen.RSSItem(
        title=m_title,
        description=m_description,
        pubDate=datetime.datetime.now(),
        link=m_link,
        guid=PyRSS2Gen.Guid(m_link)
    ))
    write_log("break point3")
    rss = PyRSS2Gen.RSS2(
        title="hackermonica.me",
        description="Monica的动漫资源站",
        link=URL,
        lastBuildDate=datetime.datetime.now(),
        items=myitems
    )
    write_log("break point4")
    rss.write_xml(open("./rss.xml", "w"), encoding="utf-8")
    write_log("break point5")

if __name__ == "__main__":
    title = "test"
    link = "test"
    description = "test"
    writeRss(title, link, description)