from flask import Flask, request, send_file, jsonify
import service

app = Flask(__name__)