import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if http_method == 'GET' and path == '/items':
            # Get all items
            response = table.scan()
            return {
                'statusCode': 200,
                'body': json.dumps(response['Items'], cls=DecimalEncoder),
                'headers': {'Content-Type': 'application/json'}
            }
        
        elif http_method == 'GET' and path.startswith('/items/'):
            # Get single item
            item_id = path.split('/')[-1]
            response = table.get_item(Key={'id': item_id})
            if 'Item' in response:
                return {
                    'statusCode': 200,
                    'body': json.dumps(response['Item'], cls=DecimalEncoder),
                    'headers': {'Content-Type': 'application/json'}
                }
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Item not found'})}
        
        elif http_method == 'POST' and path == '/items':
            # Create item
            body = json.loads(event['body'])
            table.put_item(Item=body)
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Item created', 'item': body}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        elif http_method == 'PUT' and path.startswith('/items/'):
            # Update item
            item_id = path.split('/')[-1]
            body = json.loads(event['body'])
            body['id'] = item_id
            table.put_item(Item=body)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Item updated', 'item': body}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        elif http_method == 'DELETE' and path.startswith('/items/'):
            # Delete item
            item_id = path.split('/')[-1]
            table.delete_item(Key={'id': item_id})
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Item deleted'}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        else:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid request'})}
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
