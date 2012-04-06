#!/usr/bin/ruby

require "yaml"
require "grit"

class GitoLogvConfig
  def initialize(path)
    @conf = YAML.load(File.read(path))
    @repos = @conf["repositories"]
  end
  def localpath(name)
    "#{@conf["localdir"]}/#{name}"
  end
  def htmlpath(name)
    "#{@conf["htmldir"]}/#{name}.html"
  end
  def repositories
    @repos
  end
  def repository(name)
    @repos[name]
  end
  def command
    @conf["command"]
  end
end

class GitoLogv
  def initialize(name, url)
    @name = name
    @url = url
    @localpath = $conf.localpath(@name)
    unless FileTest.exists?(@localpath)
      STDERR.puts "Create local repository #{name}:#{url}"
      Grit::Repo.init_bare(@localpath)
    end
    @grit = Grit::Repo.new(@localpath, :is_bare => true)
    @grit.remote_add(name, url)
  end
  def fetch
    @grit.remote_fetch(@name)
  end
  def log
    `sh -c 'cd #{@localpath} && #{$conf.command}'`
  end
end

$conf = GitoLogvConfig.new("repos.yaml")

$conf.repositories.each{|name, url|
  glog = GitoLogv.new(name, url)
  if glog.fetch then
    html = glog.log
    File.open($conf.htmlpath(name), "wb"){|file|
      file.write(html)
    }
  end
}
