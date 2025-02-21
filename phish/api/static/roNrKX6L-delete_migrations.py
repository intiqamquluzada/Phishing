import os
from core.settings import LOCAL_APPS as APPS

for app in APPS:
    files = os.listdir(f"{app}/migrations/")
    for file in files:
        if file != '__init__.py':
            if os.path.isfile(f"{app}/migrations/{file}"):
                os.remove(f"{app}/migrations/{file}")