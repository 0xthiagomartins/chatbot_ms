import sys, eventlet
import nameko.cli


eventlet.monkey_patch()
sys.argv.extend(["--config", "src/config.yml", "src.rpc"])
nameko.cli.run()
