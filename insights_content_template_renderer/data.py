import json


request_data_example = {}
with open("insights_content_template_renderer/data/request_data_example.json", encoding="UTF-8") as f:
    request_data_example = json.load(f)

response_data_example = {}
with open("insights_content_template_renderer/data/response_data_example.json", encoding="UTF-8") as f:
    response_data_example = json.load(f)

content_example = {}
with open("insights_content_template_renderer/data/content_example.json", encoding="UTF-8") as f:
    content_example = json.load(f)
