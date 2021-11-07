import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4
import json
import mariadb
from decimal import Decimal
import time
import smbus
import os
import boto3
from pprint import pprint
import MySQLdb
from datetime import datetime
from decimal import *

import os

os.system('mpg321 -q start.mp3 &')

import veml6070
ALL_INTEGRATION_TIMES = [
    veml6070.INTEGRATIONTIME_1_2T, veml6070.INTEGRATIONTIME_1T, veml6070.INTEGRATIONTIME_2T, veml6070.INTEGRATIONTIME_4T
]

# WEB
import face_recognition
import cv2
import numpy as np


video_capture = cv2.VideoCapture(0)

julie_image = face_recognition.load_image_file("julie.jpg")
julie_face_encoding = face_recognition.face_encodings(julie_image)[0]
anita_image = face_recognition.load_image_file("anita.jpg")
anita_face_encoding = face_recognition.face_encodings(anita_image)[0]
nick_image = face_recognition.load_image_file("nick.jpg")
nick_face_encoding = face_recognition.face_encodings(nick_image)[0]
cj_image = face_recognition.load_image_file("cj.jpg")
cj_face_encoding = face_recognition.face_encodings(cj_image)[0]

known_face_encodings = [
    julie_face_encoding,
    anita_face_encoding,
    nick_face_encoding,
    cj_face_encoding
]
known_face_names = [
    "Julie Smith",
    "sleepyhead",
    "Asshole",
    "bitch boi"
]

face_locations = []
face_encodings = []
face_names = []

known_face_found = False
# END WEB

parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint, not including a port. " +
                                                      "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\"")
parser.add_argument('--port', type=int, help="Specify port. AWS IoT supports 443 and 8883.")
parser.add_argument('--cert', help="File path to your client certificate, in PEM format.")
parser.add_argument('--key', help="File path to your private key, in PEM format.")
parser.add_argument('--root-ca', help="File path to root certificate authority, in PEM format. " +
                                      "Necessary if MQTT server uses a certificate that's not already in " +
                                      "your trust store.")
parser.add_argument('--client-id', default="test-" + str(uuid4()), help="Client ID for MQTT connection.")
parser.add_argument('--topic', default="test/topic", help="Topic to subscribe to, and publish messages to.")
parser.add_argument('--message', default="Hello World!", help="Message to publish. " +
                                                              "Specify empty string to publish nothing.")
parser.add_argument('--count', default=0, type=int, help="Number of messages to publish/receive before exiting. " +
                                                          "Specify 0 to run forever.")
parser.add_argument('--use-websocket', default=False, action='store_true',
    help="To use a websocket instead of raw mqtt. If you " +
    "specify this option you must specify a region for signing.")
parser.add_argument('--signing-region', default='us-east-1', help="If you specify --use-web-socket, this " +
    "is the region that will be used for computing the Sigv4 signature")
parser.add_argument('--proxy-host', help="Hostname of proxy to connect to.")
parser.add_argument('--proxy-port', type=int, default=8080, help="Port of proxy to connect to.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()

io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

received_count = 0
received_all_event = threading.Event()

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    received_count += 1
    if received_count == args.count:
        received_all_event.set()

## PENIS
print("not connected")

        
# db = MySQLdb.connect(
#     host="database-1.cdghjpbpi22t.us-east-2.rds.amazonaws.com",
#     user="admin",
#     password="TinyRights67$",
#     db="database-1"
#     )
# cur2 = db.cursor()
dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
#table = dynamodb.create_table(
#    TableName='Weather',
#    KeySchema=[
#        {
#            'KeyType':'HASH',
#            'AttributeName':'id'
#            }
#        ],
#    AttributeDefinitions=[
#        {
#             'AttributeName':'id',
#             'AttributeType':'N'
#             }
#         ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits':2,
#         'WriteCapacityUnits':2
#         }
#     )
# table.meta.client.get_waiter('table_exists').wait(TableName='Weather')
table = dynamodb.Table('Weather')
print("connected to aws")

bus = smbus.SMBus(1)

addr = 0x60

# a0: 16 bits - 1 sign, 12 int, 3 frac
a0 = (bus.read_byte_data(addr, 0x04) <<8) | \
      bus.read_byte_data(addr, 0x05)
if a0 & 0x8000:
    a0d = -((~a0 & 0xffff) + 1)
else:
    a0d = a0
a0f = float(a0d) / 8.0
print("a0 = 0x%4x %5d %4.3f" % (a0, a0d, a0f))

# b1: 16 bits - 1 sign, 2 int, 13 frac
b1 = (bus.read_byte_data(addr, 0x06) << 8 ) | \
      bus.read_byte_data(addr, 0x07)
if b1 & 0x8000:
    b1d = -((~b1 & 0xffff) + 1)
else:
    b1d = b1
b1f = float(b1d) / 8192.0
print("b1 = 0x%4x %5d %1.5f" % (b1, b1d, b1f))

# b2: 16 bits - 1 sign, 1 int, 14 frac
b2 = (bus.read_byte_data(addr, 0x08) << 8) | \
      bus.read_byte_data(addr, 0x09)
if b2 & 0x8000:
    b2d = -((~b2 & 0xffff) + 1)
else:
    b2d = b2
b2f = float(b2d) / 16384.0
print("b2 = 0x%4x %5d %1.5f" % (b2, b2d, b2f))

# c12: 14 bits - 1 sign, 0 int, 13 frac
# (Documentation in the datasheet is poor on this.)
c12 = (bus.read_byte_data(addr, 0x0a) << 8) | \
       bus.read_byte_data(addr, 0x0b)
if c12 & 0x8000:
    c12d = -((~c12 & 0xffff) + 1)
else:
    c12d = c12
c12f = float(c12d) / 16777216.0
print("c12 = 0x%4x %5d %1.5f" % (c12, c12d, c12f))

print("how long")
start = time.time()
now = time.time()

if __name__ == '__main__':
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    proxy_options = None
    if (args.proxy_host):
        proxy_options = http.HttpProxyOptions(host_name=args.proxy_host, port=args.proxy_port)

    if args.use_websocket == True:
        credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
        mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=args.endpoint,
            client_bootstrap=client_bootstrap,
            region=args.signing_region,
            credentials_provider=credentials_provider,
            http_proxy_options=proxy_options,
            ca_filepath=args.root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=30)

    else:
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=args.endpoint,
            port=args.port,
            cert_filepath=args.cert,
            pri_key_filepath=args.key,
            client_bootstrap=client_bootstrap,
            ca_filepath=args.root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=proxy_options)

    print("Connecting to {} with client ID '{}'...".format(
        args.endpoint, args.client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(args.topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if args.message:
        if args.count == 0:
            print ("Sending messages until program killed")
        else:
            print ("Sending {} message(s)".format(args.count))
        
        veml = veml6070.Veml6070()

        loopsSinceFace = 10;
        publish_count = 1
        while (publish_count <= args.count) or (args.count == 0):
            loopsSinceFace = loopsSinceFace+1
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            #process a frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                print("FUCK")
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    os.system('mpg321 -q saw.mp3 &')
                    name = known_face_names[best_match_index]
                    print("Face found:", name)
                    loopsSinceFace = 0

                face_names.append(name)

            # Start conversion and wait 1s

            now = time.time()
            if (now-start) > 60:
            
                bus.write_byte_data(addr, 0x12, 0x0)
                time.sleep(1)
                rawpres = (bus.read_byte_data(addr, 0x00) << 2) | \
                   (bus.read_byte_data(addr, 0x01) >> 6)
                rawtemp = (bus.read_byte_data(addr, 0x02) << 2) | \
                   (bus.read_byte_data(addr, 0x03) >> 6)

                #print("\nRaw pres = 0x%3x %4d" % (rawpres, rawpres))
                #print("Raw temp = 0x%3x %4d" % (rawtemp, rawtemp))

                pcomp = a0f + (b1f + c12f * rawtemp) * rawpres + b2f * rawtemp
                pkpa = pcomp / 15.737 + 50
                print("Pres = %3.2f kPa" % pkpa)

                temp = 25.0 - (rawtemp - 498.0) / 5.35
                temp2 = float("%3.2f" % temp)
                
                print("Temp = " , temp2)
                

                veml.set_integration_time(3)
                uv_raw = veml.get_uva_light_intensity_raw()
                uv = veml.get_uva_light_intensity()
                print("%f W/(m*m) from raw value %d" % (uv, uv_raw))
                
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                dt_id = now.strftime("%Y%m%d%H%M%S")
                print(dt_string)
                table.put_item(
                    TableName='Weather',
                    Item={
                        'id':int(dt_id),
                        'time':dt_string,
                        'temp':int(temp2*1000),
                        'UV':int(uv*1000),
                        'pres':int(pkpa*1000)
                        }
                    )
                
                valid = (loopsSinceFace<10);
                valid2 = "false"
                if(valid):
                    valid2 = "true"
                
                f = open("weather.json", "w")
                f.write("{\"valid\": "+valid2+",\"temp\":"+str(temp)+",\"pressure\":"+str(pkpa)+",\"uv\":"+str(uv)+"}")
                f.close()
                start=time.time()
                print("done")


    # CAM
    video_capture.release()
    cv2.destroyAllWindows()

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if args.count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")