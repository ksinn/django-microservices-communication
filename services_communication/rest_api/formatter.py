from services_communication.utils import underscoreize, camelize


json_request = lambda r: camelize(r)
json_response = lambda r: underscoreize(r.json())
file_response = lambda r: r.content
full_response = lambda r: r
