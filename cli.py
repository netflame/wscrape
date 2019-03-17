#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import click
from scrapy import cmdline
from scrapyd_api import ScrapydAPI
from wscrape import NAME


CATEGORIES = ['edu', 'ent', 'finance', 'tech', 'world']
SITES = ['netease', 'sohu', 'tencent', 'toutiao']


TARGET, PROJECT = 'dev', NAME
DEPLOY = {
    'dev': {
        'wscrape': 'http://localhost:6800/',
    },
}

scrapyd = None


@click.group(help='cli for crawler')
def cfc():
    pass


@cfc.command(name='list', help='list spiders')
def show():
    cmdline.execute('scrapy list'.split())


@cfc.command(help='crawl `spider`')
@click.option('-c', '--category', type=click.Choice(['all']+CATEGORIES), default='all', show_default=True, help='type of crawler')
@click.option('-s', '--site', type=click.Choice(['all']+SITES), default='all', show_default=True, help='site to be crawled')
def crawl(category, site):
    if category == 'all':
        if site == 'all':
            _crawl_all()
        else:
            _crawl_all('categories', site)
    else:
        if site == 'all':
            _crawl_all('sites', category)
        else:
            cmds = 'scrapy crawl %s_%s' % (category, site)
            cmdline.execute(cmds.split())

def _crawl_all(type_=None, *args):
    loop = asyncio.get_event_loop()
    if type_ is None:
        tasks = [_crawl(spider) for spider in SITES]
    elif type_ == 'categories':
        site = args[0]
        tasks = [_crawl(site)]
    elif type_ == 'sites':
        category = args[0]
        tasks = [_crawl(category+"_"+site) for site in SITES]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

async def _crawl(spider):
    cmds = 'scrapy crawl %s' % spider
    cmdline.execute(cmds.split())


@cfc.group(name='sd', help='scrapyd commands')
def scrapyd_():
    pass

# the job status returned can be one of: '', 'running', 'pending' or 'finished'
@scrapyd_.command(name='status', help='check the load status of a service or the job status for a certain job')
@click.option('-p', '--project', default=PROJECT, show_default=True, help='project name')
@click.option('-j', '--job', default=None, help="the job id")
def status(project, job):
    def daemonstatus():
        DAEMON_STATUS_ENDPOINT = 'daemonstatus'
        dse = {DAEMON_STATUS_ENDPOINT: '/daemonstatus.json'}
        scrapyd.endpoints.update(dse)
        url = scrapyd._build_url(DAEMON_STATUS_ENDPOINT)
        json_ = scrapyd.client.get(url, timeout=scrapyd.timeout)
        click.secho(message=str(json_), fg='green')

    def jobstatus(project, job):
        r = scrapyd.job_status(project, job)
        click.secho(message=r, fg='green')
    
    if job is None:
        daemonstatus()
    else:
        jobstatus(project, job)

@scrapyd_.command(help='cancel a scheduled job')
@click.option('-p', '--project', default=PROJECT, show_default=True, help='project name')
@click.argument('job')
def cancel(project, job):
    prev_state = scrapyd.cancel(project, job)
    click.secho(message=prev_state, fg='red')

@scrapyd_.command(help='delete a project with an optional version')
@click.option('-p', '--project', default=PROJECT, show_default=True, help='project name')
@click.option('-v', '--version', default=None, help='the project version')
def delete(project, version):
    if not version:
        r = scrapyd.delete_project(project)
    else:
        r = scrapyd.delete_version(project, version)
    click.secho(message=str(r), fg='red')

@scrapyd_.command(name='list', help='list projects, jobs, spiders or versions')
@click.option('-P/ ', '--projects/--no-p', default=False, show_default=True, help='list all avaliable projects')
@click.option('-p', '--project', default=PROJECT, show_default=True, help='project name')
@click.option('-J/ ', '--jobs/--no-j', default=False, show_default=True, help='list all running, finished & pending spider jobs of a given project')
@click.option('-S/ ', '--spiders/--no-s', default=False, show_default=True, help='Lists all available spiders of a given project')
@click.option('-V/ ', '--versions/--no-v', default=False, show_default=True, help='list all available versions of a given project')
def list_(projects, project, jobs, spiders, versions):
    def _show(message):
        message = str(message)
        click.secho(message, fg='green')

    def list_projects():
        lpr = scrapyd.list_projects()
        _show(lpr)

    def list_jobs(project):
        ljr = scrapyd.list_jobs(project)
        _show(ljr)

    def list_spiders(project):
        lsr = scrapyd.list_spiders(project)
        _show(lsr)
    
    def list_versions(project):
        lvr = scrapyd.list_versions(project)
        _show(lvr)

    if projects:
        list_projects()
    if jobs:
        list_jobs(project)
    if spiders:
        list_spiders(project)
    if versions:
        list_versions(project)

@scrapyd_.command(help='schedule a job to run')
@click.option('-p', '--project', default=PROJECT, show_default=True, help='project name')
@click.argument('spider')
@click.option('-s', '--settings', default=None, help='a dict of scrapy settings keys you wish to override for this run')
def schedule(project, spider, settings):
    job_id = scrapyd.schedule(project, spider, settings)
    click.secho(job_id, fg='green')


def _init_scrapyd(target=TARGET, project=PROJECT):
    global scrapyd
    if not scrapyd:
        scrapyd = ScrapydAPI(DEPLOY[target][project])


def main():
    _init_scrapyd()
    cfc()

if __name__ == '__main__':
    main()
