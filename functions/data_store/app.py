import json
from tempfile import mkdtemp
import requests
import hashlib
import uuid
from elasticsearch import Elasticsearch
import boto3

class FbAdsLibDataStore:

    def __init__(self):
        self.s3 = boto3.client(
            service_name='s3',
            region_name='us-east-1',
            aws_access_key_id='AKIASP3TS2DPZRHM2DBG',
            aws_secret_access_key='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'
            )

        # self.s3 =boto3.client("s3")

        self.es=Elasticsearch(['https://search-testfbadslib-arkod77br4pscry5r4hqaacnfy.us-east-1.es.amazonaws.com/'],
                              http_auth=('jeylearner2022','Jey@aws1290'))

        self.es.indices.create(index='scraping_project',ignore=400)
        print(self.es.ping())
        self.bucket_name = "fbadlibtest"

    def generate_hash(self, fbAdlibItem):

        # Get Data from media URL.
        media_data=requests.get(fbAdlibItem["adMediaURL"],stream=True).raw

        # Create an Object to generate Hash From.
        data={
            'media_data':str(media_data.data),
            'headline':fbAdlibItem["headline"],
            'page_name':fbAdlibItem["pageInfo"]["name"],
            'ad_id':fbAdlibItem["adID"],
            'purchase_url':fbAdlibItem["purchaseURL"],
            'displayURL':fbAdlibItem['displayURL'],
            'purchase_description':fbAdlibItem["purchaseDescription"],
            }
        
        # cobvert to Json Object to string
        a_string = str(data)

        # Generated HASH from String
        hashed_string = hashlib.sha256(a_string.encode('utf-8')).hexdigest()

        #return generated HASH.
        return hashed_string

    def create_new_ad(self, fbAdlibItem):
        mediaResponse = requests.get(fbAdlibItem['adMediaURL'], stream=True).raw

        if fbAdlibItem['adMediaType']=='image':
            filename = "%s.%s" % (uuid.uuid4(), 'jpeg')
        if fbAdlibItem['adMediaType']=='video':
            filename = "%s.%s" % (uuid.uuid4(), 'mp4')
        self.s3.upload_fileobj(mediaResponse, self.bucket_name, fbAdlibItem['adMediaType']+'/'+filename)

        s3_url = f'https://{self.bucket_name}.s3.amazonaws.com/'+fbAdlibItem['adMediaType']+f'/{filename}'

        # where we are storing s3 url + why deleting pageInfo ?
        del fbAdlibItem['pageInfo']
        
        res=self.es.index(index="scraping_project", body=fbAdlibItem, ignore=400)
        
        return

    def update_ad(self, oldFbAdlibItem, updateQuery):
        # why we can't use Hash to update record ?
        query1={
                "script":{
                    "inline":updateQuery,
                    "lang": "painless"
                },
                "query":{
                    "bool": {
                        "must": [
                        {
                            "match": {
                            "adID": oldFbAdlibItem["adID"]
                            }
                        }
                        ]
                    }
                    }
            }

        # Why same thing in both try and ex except ?
        try:
            query_res=self.es.update_by_query(index="scraping_project",body=query1)
            print("Record updated successfully !!!!!")
            print(query_res["updated"])
        except Exception as e:
            self.es.indices.refresh(index = "scraping_project")
            query_res=self.es.update_by_query(index="scraping_project",body=query1)
        finally:
            return

    def save_ad(self,newFbAdlibItem):
        newFbAdlibItem["hash"]=self.generate_hash(newFbAdlibItem)

        query={
          "query": {
            "bool": {
              "must": [
                {
                  "match": {
                    "hash.keyword": newFbAdlibItem["hash"]
                  }
                }
              ]
            }
          }
        }

        result=self.es.search(index="scraping_project", body=query)

        if result["hits"]["hits"]:
            hits_data=result["hits"]["hits"][0]["_source"]

            if hits_data["status"]==newFbAdlibItem["status"] and hits_data["adMediaURL"]==newFbAdlibItem["adMediaURL"]:

                self.update_ad(hits_data, "ctx._source.noOfCopyAds={}".format(newFbAdlibItem['noOfCopyAds']))
                
            if hits_data["status"]==newFbAdlibItem["status"] and hits_data["adMediaURL"]!=newFbAdlibItem["adMediaURL"]:

                self.update_ad(hits_data, "ctx._source.status='Inactive'")
                self.create_new_ad(newFbAdlibItem)
                    
            if hits_data["status"]!=newFbAdlibItem["status"] and hits_data["status"]=="Inactive" and hits_data["adMediaURL"]==newFbAdlibItem["adMediaURL"]:

                self.update_ad(hits_data, "ctx._source.status='Active';ctx._source.noOfCopyAds={}".format(i['noOfCopyAds']))
            
        else:
            self.create_new_ad(newFbAdlibItem)

def lambda_handler(event, context):

    fbAdsLibDataStore = FbAdsLibDataStore()
    fbAdsLibDataStore.save_ad(event["cleanedAdData"])

    return {
        "statusCode": 200
    }
