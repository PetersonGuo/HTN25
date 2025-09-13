import boto3
import os
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key, Attr

load_dotenv()  # Load environment variables from .env file

dynamodb = boto3.resource('dynamodb')

def get_connector():
    return dynamodb

def get_table(table_name):
    table = dynamodb.Table(table_name)
    return table

def query_table(table_name, key, value):
    table = get_table(table_name)
    response = table.query(
        KeyConditionExpression=Key(key).eq(value)
    )
    return response.get('Items', [])

def scan_table(table_name, filter_key=None, filter_value=None):
    table = get_table(table_name)
    if filter_key and filter_value:
        response = table.scan(
            FilterExpression=Attr(filter_key).eq(filter_value)
        )
    else:
        response = table.scan()
    return response.get('Items', [])

def put_item(table_name, item):
    table = get_table(table_name)
    table.put_item(Item=item)

def delete_item(table_name, key, value):
    table = get_table(table_name)
    table.delete_item(
        Key={key: value}
    )

def update_item(table_name, key, value, update_expression, expression_values):
    table = get_table(table_name)
    table.update_item(
        Key={key: value},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )
