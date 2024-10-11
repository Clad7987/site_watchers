import os

if os.path.exists("scrapers/fapdungeon.py"):
    import scrapers.fapdungeon as fd

    fd.main()

if os.path.exists("scrapers/boobieblog.py"):
    import scrapers.boobieblog as bb

    bb.main()
