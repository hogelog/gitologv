#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import yaml
from subprocess import Popen, PIPE
from git import Git
from ansi2html import Ansi2HTMLConverter

class GitoLogvConfig:
  def __init__(self, path):
    with open(path, "r") as file:
      self.conf = yaml.load(file)
      self.repos = self.conf["repositories"]

  def repos_path(self, name):
    return "%s/%s" % (self.conf["reposdir"], name)

  def html_path(self, name):
    return "%s/%s" % (self.conf["htmldir"], name)

  def repositories(self):
    return self.repos

  def repository(self, name):
    return self.repos[name]

  def command(self):
    return self.conf["command"]

class GitoLogv:
  def __init__(self, conf, name, url):
    self.conf = conf
    self.name = name
    self.url = url
    self.path = conf.repos_path(name)
    self.git = Git()
    if not os.path.exists(self.path):
      print >> sys.stderr, "Create local repository %s:%s" % (name, url)
      self.git.clone(("--mirror %s %s" % (url, self.path)).split())

  def fetch(self):
    self.git.fetch()

  def shell(self, args):
    return Popen(args, stdout=PIPE).communicate()[0]

  def log(self):
    return self.shell(["sh", "-c", "cd %s && %s" % (self.path, self.conf.command())])

config = GitoLogvConfig("repos.yaml")
for repos in config.repositories():
  url = config.repository(repos)
  logv = GitoLogv(config, repos, url)
  print >> sys.stderr, "Fetching %s" % url
  logv.fetch()
  log = logv.log()
  html = Ansi2HTMLConverter(linkify=True).convert(log)
  html_path = "%s.html" % config.html_path(repos)
  with open(html_path, "w") as html_file:
    print >> sys.stderr, "Generating %s" % html_path
    print >> html_file, html
