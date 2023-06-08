#!/bin/bash

# Define the target URL
url="http://admin.bankly.mu-stafa.com/api/authentication/token/"
request_body='{"username": "usertest", "password": "passtest"}'
echo "$request_body" > request.json

# Perform load testing and measure average response time
# ab -n $concurrency -c $concurrency $url | grep "Time taken" | awk '{total += $4} END {print "Average response time:", total/NR}'
ab -n 100 -c 5 -p request.json -T "application/json" $url