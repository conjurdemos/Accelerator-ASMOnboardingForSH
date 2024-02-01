#!/bin/bash

LAMBDA_URL=https://ntwy3m9upd.execute-api.us-east-1.amazonaws.com/Test/ASMOnboarder

if [[ $# != 1 ]]; then
  echo "Usage:"
  echo "   $0 <ASM-secret-name>"
  exit -1 
fi

secretName=$1

echo "Deleting secret $secretName..."
response=$(curl -s -X DELETE $LAMBDA_URL		\
        --write-out '\n%{http_code}'                    \
  	-H 'content-type: application/json' 		\
	-d "{						\
	      \"detail\": {				\
    		  \"eventName\": \"DeleteSecret\",	\
		  \"requestParameters\": {		\
			\"name\": \"$secretName\"	\
		   }					\
	      }						\
	    }")
http_code=$(tail -n1 <<< "$response")  # get http_code on last line
content=$(sed '$ d' <<< "$response")   # trim http_code

case $http_code in
  204)
	echo "Account corresponding to $secretName deleted."
	;;
  *)
	echo $content
	;;
esac
