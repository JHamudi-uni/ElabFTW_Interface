import elabapy
# json is used for encoding and decoding JSON data.
import json
# imports the HTTPError exception from the requests library, which is used to handle errors that occur
# during HTTP requests.
from requests.exceptions import HTTPError


# creates an instance of the Manager class from the elabapy library, initializing it with the endpoint and API token
manager = elabapy.Manager(endpoint="https://demo.elabftw.net/api/v1/", token="1ddbf1d38905d0b8d48c8992783a50320d0103fb19c9079259b9defbeb4bc11447da883ac6facbff1152210")
params = { "tag": "some-tag"}

# get experiment with id 13170
try:
    exp = manager.get_experiment(13170)

    # add tag "some-tag" to experiment 13170
    print(manager.add_tag_to_experiment(13170, params))

    # uses the json.dumps function to convert the exp variable (which contains information about an experiment)
    # into a string representation in JSON format. The indent parameter is set to 4 to make the JSON output more
    # readable, and the sort_keys parameter is set to True to sort the keys in the JSON output.
    print(json.dumps(exp, indent=4, sort_keys=True))

# if something goes wrong, the corresponding HTTPError will be raised
except HTTPError as e:
    print(e)
    
