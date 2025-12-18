import os
from coreproject_tracker.singletons import get_redis

r = get_redis()

# Automatically load all .lua files in this folder
for filename in os.listdir(os.path.dirname(__file__)):
    if not filename.endswith(".lua"):
        continue

    name = os.path.splitext(filename)[0]
    path = os.path.join(os.path.dirname(__file__), filename)

    with open(path, "r", encoding="utf-8") as f:
        script = f.read()

    # Register the Lua script with Redis
    lua_func = r.register_script(script)

    # Inject as a callable in this module
    globals()[name] = lua_func
