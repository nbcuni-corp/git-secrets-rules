# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 12:04:36 2021

@author: will-schneble
"""

import json
import boto3
import hashlib
import argparse
import os

def main(region, filename, elapsed_time, lines_scanned, files_scanned):
    session = boto3.Session(
        region_name=region,
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )
    table = session.resource('dynamodb').Table('git-secrets')
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line)
            uuid = data['branch']+data['commitHash']+''.join(sorted(data['stringsFound']))
            data['uuid'] = hashlib.sha256(bytes(
                uuid,
                'utf-8'
            )).hexdigest()
            data['elapsed_time'] = elapsed_time
            data['lines_scanned'] = lines_scanned
            data['files_scanned'] = files_scanned
            try:
                table.put_item(
                    Item=data,
                    ConditionExpression='attribute_not_exists(#uuid)',
                    ExpressionAttributeNames={
                        '#uuid': 'uuid'
                    }
                )
            except table.meta.client.exceptions.ConditionalCheckFailedException:
                pass
        
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Git-secrets results upload for metrics tracking.')
  parser.add_argument('--region', '-r', type=str, help='Region the AWS resources are in.', default='us-east-1')
  parser.add_argument('--file', '-f', type=str, help='Filename with the trufflehog results in JSON format', required=True)
  parser.add_argument('--elapsed-time', type=int, help='Total elasped scanning time in seconds', required=True)
  parser.add_argument('--lines-scanned', type=int, help='Total number of lines scanned for secrets', required=True)
  parser.add_argument('--files-scanned', type=int, help='Total number of files scanned for secrets', required=True)
  args = parser.parse_args()
  main(args.region, args.file, args.elapsed_time, args.lines_scanned, args.files_scanned)
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 12:04:36 2021

@author: will-schneble
"""

import json
import boto3
import hashlib
import argparse
import os
import re

def parse_git_diff(git_diff):
    m = re.findall(r'(\d) files? changed(?:, (\d) insertion\(\+\))?(?:, (\d) deletion\(-\))?', git_diff)
    if not m:
        return 0, 0
    else:
        m = m[0]
    files_scanned = int(m[0]) if m[0] else 0
    lines_scanned = int(m[1] if m[1] else 0) + int(m[2] if m[2] else 0)
    return files_scanned, lines_scanned

def main(region, filename, elapsed_time, git_diff):
    session = boto3.Session(
        region_name=region,
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )
    table = session.resource('dynamodb').Table('git-secrets')
    files_scanned, lines_scanned = parse_git_diff(git_diff)
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line)
            uuid = data['branch']+data['commitHash']+''.join(sorted(data['stringsFound']))
            data['uuid'] = hashlib.sha256(bytes(
                uuid,
                'utf-8'
            )).hexdigest()
            data['elapsed_time'] = elapsed_time
            data['lines_scanned'] = lines_scanned
            data['files_scanned'] = files_scanned
            try:
                table.put_item(
                    Item=data,
                    ConditionExpression='attribute_not_exists(#uuid)',
                    ExpressionAttributeNames={
                        '#uuid': 'uuid'
                    }
                )
            except table.meta.client.exceptions.ConditionalCheckFailedException:
                pass
        
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Git-secrets results upload for metrics tracking.')
  parser.add_argument('--region', '-r', type=str, help='Region the AWS resources are in.', default='us-east-1')
  parser.add_argument('--file', '-f', type=str, help='Filename with the trufflehog results in JSON format', required=True)
  parser.add_argument('--elapsed-time', type=int, help='Total elasped scanning time in seconds', required=True)
  parser.add_argument('--git-diff', type=int, help='git diff --stat summary', required=True)
  args = parser.parse_args()
  main(args.region, args.file, args.elapsed_time, args.git_diff)
