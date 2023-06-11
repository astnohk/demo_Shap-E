import asyncio
import hashlib
import json
import mimetypes
import os
import pathlib
import queue
import random
import ssl
import threading
from urllib.parse import urlparse, parse_qs

from http.server import HTTPServer, BaseHTTPRequestHandler

from util import txt2mesh, gltf_util, json_util, xyz_util

resultDir = None
requestQueue = queue.Queue(3)
resultIndex = {}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        print(parsed_path)
        absolutePath = pathlib.Path(parsed_path.path).resolve()
        queries = parse_qs(parsed_path.query)
        try:
            if parsed_path.path == '/request':
                prompt = queries['prompt'][0]
                fileformat = queries['fileformat'][0]
                key = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=24))
                try:
                    requestQueue.put({
                            'prompt': prompt,
                            'fileformat': fileformat,
                            'key': key,
                        })
                except queue.Full:
                    print('[ERROR] do_GET(): /request: request queue is Full.')
                    key = None
                    pass
                if key is not None:
                    response_data = json.dumps({
                            'path': parsed_path.path,
                            'response_data': {
                                'key': key,
                            },
                        }).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(response_data))
                    self.end_headers()
                    self.wfile.write(response_data)
                else:
                    response_data = json.dumps({
                            'path': parsed_path.path,
                            'message': 'Shap-E is busy',
                        }).encode()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(response_data))
                    self.end_headers()
                    self.wfile.write(response_data)
            elif parsed_path.path == '/getResult':
                key = queries['key'][0]
                if resultIndex.get(key) is not None:
                    result = resultIndex.get(key)
                    if result.get('fileformat') == 'json':
                        response_data = json.dumps({
                                'path': parsed_path.path,
                                'response_data': {
                                    'key': key,
                                    'data': result['data'],
                                },
                            }).encode()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Content-Length', len(response_data))
                        self.end_headers()
                        self.wfile.write(response_data)
                    else:
                        filepath = result.get('output_path')
                        if (filepath is not None and
                                os.path.exists(filepath)):
                            with open(filepath, 'rb') as f:
                                data = f.read()
                            self.send_response(200)
                            self.send_header('Content-Type', mimetypes.guess_type(filepath))
                            self.send_header('Content-Length', len(data))
                            self.end_headers()
                            self.wfile.write(data)
                        else:
                            response_data = json.dumps({
                                    'path': parsed_path.path,
                                    'message': 'File Not Found',
                                }).encode()
                            self.send_response(404)
                            self.send_header('Content-Type', 'application/json')
                            self.send_header('Content-Length', len(response_data))
                            self.end_headers()
                            self.wfile.write(response_data)
                else:
                    response_data = json.dumps({
                            'path': parsed_path.path,
                            'message': 'Not Found',
                        }).encode()
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(response_data))
                    self.end_headers()
                    self.wfile.write(response_data)
            else:
                ## GET specified path
                if str(absolutePath).startswith(resultDir) and os.path.exists(absolutePath):
                    ## Secure Contain Protect (inside resultDir)
                    with open(absolutePath, 'rb') as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', mimetypes.guess_type(absolutePath))
                    self.send_header('Content-Length', len(data))
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    response_data = json.dumps({
                            'path': parsed_path.path,
                            'message': 'Not Found',
                        }).encode()
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(response_data))
                    self.end_headers()
                    self.wfile.write(response_data)
        except Exception as err:
            print('[ERROR] MyHTTPRequestHandler.do_GET(): ', end='')
            print(err)
            response_data = json.dumps({
                    'path': parsed_path.path,
                    'message': 'Internal Server Error',
                }).encode()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        print(parsed_path)
        absolutePath = pathlib.Path(parsed_path.path).resolve()
        queries = parse_qs(parsed_path.query)
        content_length = int(self.headers['content-length'])
        content = self.rfile.read(content_length).decode('utf-8')
        try:
            if parsed_path.path == '/request':
                prompt = content
                fileformat = queries['fileformat'][0]
                key = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=24))
                try:
                    requestQueue.put({
                            'prompt': prompt,
                            'fileformat': fileformat,
                            'key': key,
                        })
                except queue.Full:
                    print('[ERROR] do_GET(): /request: request queue is Full.')
                    key = None
                    pass
                if key is not None:
                    response_data = json.dumps({
                            'path': parsed_path.path,
                            'response_data': {
                                'key': key,
                            },
                        }).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(response_data))
                    self.end_headers()
                    self.wfile.write(response_data)
                else:
                    response_data = json.dumps({
                            'path': parsed_path.path,
                            'message': 'Shap-E is busy',
                        }).encode()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', len(response_data))
                    self.end_headers()
                    self.wfile.write(response_data)
        except Exception as err:
            print('[ERROR] MyHTTPRequestHandler.do_POST(): ', end='')
            print(err)
            response_data = json.dumps({
                    'path': parsed_path.path,
                    'message': 'Internal Server Error',
                }).encode()
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data)

def startHTTPServer(server_address):
    print('Start HTTP Server...')
    server = HTTPServer(server_address, MyHTTPRequestHandler)
    server.serve_forever()
    print('End HTTP Server.')



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', help='Output Directory', type=str, default='./results')
    parser.add_argument('--hostname', help='Hostname', type=str, default='0.0.0.0')
    parser.add_argument('--port', help='Port', type=int, default=8080)
    args = parser.parse_args()

    resultDir = pathlib.Path(args.output).resolve()
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    httpAddress = (args.hostname, args.port)
    thread_httpServer = threading.Thread(
            target=startHTTPServer,
            args=(httpAddress,),
            daemon=True)
    thread_httpServer.start()

    # Initialize Point-E models
    shap_e = txt2mesh.shap_e_wrapper()

    while True:
        request = None
        try:
            request = requestQueue.get(block=True)
            print(request)
        except Exception as err:
            print('[ERROR] Get Request: ', end='')
            print(err)

        try:
            print('Generate new 3D Model with the prompt "{}"...'.format(request['prompt']))
            mesh = shap_e.sample(request['prompt'])
        except Exception as err:
            print('[ERROR] Generate Point Cloud and Convert to Mesh: ', end='')
            print(err)

        try:
            if request['fileformat'] == 'ply':
                # Write the mesh to a PLY file to import into some other program.
                output_path = os.path.join(resultDir, '{}.ply'.format(request['key']))
                with open(output_path, 'wb') as f:
                    mesh.write_ply(f)
                resultIndex[request['key']] = {
                        'fileformat': request['fileformat'],
                        'output_path': output_path,
                    }
            elif request['fileformat'] == 'xyz':
                # Write the mesh to a PLY file to import into some other program.
                output_path = os.path.join(resultDir, '{}.xyz'.format(request['key']))
                xyz_util.write_xyz(
                        output_path,
                        mesh)
                resultIndex[request['key']] = {
                        'fileformat': request['fileformat'],
                        'output_path': output_path,
                    }
            elif request['fileformat'] == 'glTF':
                # Write the mesh to a PLY file to import into some other program.
                output_path = os.path.join(resultDir, '{}.glb'.format(request['key']))
                gltf_util.write_gltf(
                        output_path,
                        mesh)
                resultIndex[request['key']] = {
                        'fileformat': request['fileformat'],
                        'output_path': output_path,
                    }
            elif request['fileformat'] == 'json':
                data = json_util.generate_json(mesh)
                resultIndex[request['key']] = {
                        'fileformat': request['fileformat'],
                        'data': data,
                    }
        except Exception as err:
            print('[ERROR] Save : ', end='')
            print(err)

