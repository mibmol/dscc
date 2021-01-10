import os
import re

# return the value of the given environment variable.
# remove the char (") and (') from string
# due to difference of enviroments variables on windows and linux
def get_env(env_name, default=None):
    return re.sub(r"[\'\"]", "", os.environ.get(env_name, default))
