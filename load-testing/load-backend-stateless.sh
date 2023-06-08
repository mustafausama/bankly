#!/bin/bash

# Define the target URL
url="http://admin.bankly.mu-stafa.com/admin/"
request_body='{"username": "usertest", "password": "passtest"}'
echo "$request_body" > request.json

# Perform load testing and measure average response time
# ab -n $concurrency -c $concurrency $url | grep "Time taken" | awk '{total += $4} END {print "Average response time:", total/NR}'
ab -n 10000 -c 1000 $url