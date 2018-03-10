myetc
=====
These are main configuration files on my FreeBSD 9.2.
Its main purpose is to reuse these files in the future. 
Mainly focus on contents is zh_CN.UTF-8, which I used for localization, thus I 
can input Chinese character into konsole terminal.


sbt-repositories
----------------
rename to `repositories` and put into `~/.sbt` directory
`sbt` put downloaded jars into `~/.ivy2` directory

maven-settings.xml
------------------
rename to `settings.xml` and put into `/etc/maven/`
`maven` put downloaded jars into `~/.m2` directory
