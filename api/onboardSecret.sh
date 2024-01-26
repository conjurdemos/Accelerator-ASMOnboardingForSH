#!/bin/bash

LAMBDA_URL=https://ntwy3m9upd.execute-api.us-east-1.amazonaws.com/Test/ASMOnboarder

if [[ $# != 1 ]]; then
  echo "Usage:"
  echo "   $0 <ASM-secret-name>"
  exit -1 
fi

secretName=$1

curl 	-X POST $LAMBDA_URL				\
  	-H 'content-type: application/json' 		\
	-d "{						\
	      \"detail\": {				\
    		  \"eventName\": \"CreateSecret\",	\
		  \"requestParameters\": {		\
			\"name\": \"$secretName\"	\
		   }					\
	      }						\
	    }"
echo
