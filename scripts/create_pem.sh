#!/bin/bash

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./api/pem/certServ_new.pem -out ./api/pem/certServ_new.pem


