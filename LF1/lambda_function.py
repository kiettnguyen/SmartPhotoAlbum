import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

def lambda_handler(event, context):
    # TODO implement
    print(event)
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    timestamp =event['Records'][0]['eventTime']
    #print(bucket_name)
    client = boto3.client('rekognition')
    #Image = {"S3Object":{"Bucket":bucket_name,"Name":key_name}}
    resp = client.detect_labels(Image={"S3Object":{"Bucket":bucket_name,"Name":key_name}})
    
    client = boto3.client('s3')
    response = client.head_object(Bucket=bucket_name,Key =key_name) #x-amz-meta-customLabels
    #print(response)
    
    labels = []
    for i in range(len(resp['Labels'])):
        labels.append(resp['Labels'][i]['Name'])
   
   
    new_doc = {
        'objectKey':key_name,
        'bucket':bucket_name,
        'createdTimestamp':timestamp,
        'labels':labels}
    #Send format to the ElasticSearch, do later due to paying for hosting ElasticSearch
    index_into_es(key_name,json.dumps(new_doc))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
def index_into_es(id, new_doc):
    
    endpoint = 'search-photos-gxqn2umld523c4jkeya7gtbugi.us-east-1.es.amazonaws.com'
    headers = {'Content-Type':'application/json'}
    os = OpenSearch(
        hosts=[{'host': endpoint,'port': 443}], 
        http_auth=("kiettnguyen","Kiet@0802"), 
        use_ssl = True, 
        verify_certs=True, 
        connection_class=RequestsHttpConnection
    )
    print("Start access the ES")
    os.index(index= "photo_index",id= id,body= new_doc)
    print("After access the ES")
    #print(res.content)

