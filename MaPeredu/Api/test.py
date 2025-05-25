from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun

# 初始化API Wrapper
wikidata = WikidataQueryRun(api_wrapper=WikidataAPIWrapper())

# 查询“Alan Turing”
result = wikidata.run("Alan Turing")
print(result)