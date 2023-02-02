import elabapy
import json
from requests.exceptions import HTTPError
# initialize the manager with an endpoint and your token
manager = elabapy.Manager(endpoint="https://elab.example.org/api/v1/", token="3148")
# get experiment with id 42
try:
    exp = manager.get_experiment(42)
    print(json.dumps(exp, indent=4, sort_keys=True))
# if something goes wrong, the corresponding HTTPError will be raised
except HTTPError as e:
    print(e)