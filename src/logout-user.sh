#!/bin/bash

echo "$1 user will be killed in 10 seconds..."

sleep 11.5

loginctl kill-user "$1"
