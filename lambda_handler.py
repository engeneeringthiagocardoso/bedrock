import json
import boto3
import os
import logging
import botocore

bedrock_agent_runtime = boto3.client(
    service_name = "bedrock-agent-runtime"
)

# declare model id for calling RetrieveAndGenerate API
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"


model_id = os.environ.get("model_id")
boto3_session = boto3.session.Session()
region = boto3_session.region_name
print(model_id, boto3_session, region)

kb_id = os.environ.get("KNOWLEDGE_BASE_ID")

model_arn = f'arn:aws:bedrock:{region}::foundation-model/{model_id}'



prompt_base=os.environ.get("PROMPT_BASE")

    
def retrieveAndGenerate(prompt, retrieveParam):
    return bedrock_agent_runtime.retrieve_and_generate(
        input={
        'text': prompt
        },
        retrieveAndGenerateConfiguration=retrieveParam
    )
            
    
def lambda_handler(event, context):

    print(event)
    prompt = prompt_base.format(texto=event["prompt"])
    
    print(boto3.__version__)
    print(botocore.__version__)
    
    if event["filter"] != "undefined":
        retrieveParam={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': model_arn,
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'filter': {
                            'equals': {
                                'key': 'disciplina',
                                'value': event["filter"]
                            }
                        }
                    }
                }
            }
        }
    else:
        retrieveParam={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': model_arn
            }
        }
        
    #promptTemplate = '$search_results$ $output_format_instructions$'
    print(prompt, retrieveParam) 
    response = retrieveAndGenerate(prompt, retrieveParam)
    generated_text = response['output']['text']
    print(generated_text)
    sessionId = response['sessionId']
    citations = response['citations']
    
    
    return {
        'body': {"Parameters": retrieveParam, "question": prompt.strip(), "answer": generated_text.strip(), "sessionId":sessionId, "citations":citations}
    }