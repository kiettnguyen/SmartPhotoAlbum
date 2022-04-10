import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
def lambda_handler(event, context):
    # TODO implement
    print(event)
    print(context)
    inputText = event['params']['querystring']['q']
    print(inputText)
    keywords = searching_keywords(inputText)
    print("Passing the lex")
    print(keywords)
    print ("Before entering ES")
    pictures = search_intent(keywords)
    print(pictures)
    return {
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True
        },
        'body': {
            'results':pictures
        }
    }
def searching_keywords(inputText):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName = 'Search',
        botAlias = '$LATEST',
        userId = 'searchPhotosLambda',
        inputText = inputText
    )
    keywords = []
    slots = response['slots']
    keywords = [v for _, v in slots.items() if v]
    print(keywords)
    return keywords
def search_intent(labels):
    
    endpoint = 'search-photos-gxqn2umld523c4jkeya7gtbugi.us-east-1.es.amazonaws.com'
    headers = {'Content-Type':'application/json'}
    os = OpenSearch(
        hosts=[{'host': endpoint,'port': 443}], 
        http_auth=("kiettnguyen","Kiet@0802"), 
        use_ssl = True, 
        verify_certs=True, 
        connection_class=RequestsHttpConnection
    )
    
    resp = []
    for label in labels:
        if (label is not None) and label != '':
            response = os.search(
            body = query(label),
            index = "photo_index"
            )
            print(response)
            resp.append(response)
    print (resp)
  
    output = []
    for r in resp:
        if 'hits' in r:
             for val in r['hits']['hits']:
                key = val['_source']['objectKey']
                if key not in output:
                    output.append(key)
    return output
def query(q):
     return {
        "size": 2,
        "query": {
            "match":{
                'labels': q 
            }
        }
    }


