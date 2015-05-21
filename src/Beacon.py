import json
import sys
import thread
import time
from copernicus import Copernicus
import mosquitto


should_remind = True
mqttc = None
api = None
config = dict()
listen_loop = True


def alarm():
    global listen_loop
    api.command('led', True)
    listen_loop = False
    val = 0
    while True:
        val = 31 - val
        api.command('servo', val)
        time.sleep(0.5)


def remind(reminder):
    global should_remind
    global listen_loop
    print 'Reminder: "{0}"'.format(reminder)
    listen_loop = False
    api.command('rgb', 'green')
    listen_loop = True


def stop_reminding():
    global should_remind
    global listen_loop
    should_remind = False
    print 'Reminder dismissed.'
    listen_loop = False
    api.command('rgb', 'off')
    listen_loop = True


def on_connect(mqttc, obj, rc):
    print 'Beacon {0} connected'.format(config['beacon_topic'])
    mqttc.publish(config['server_topic'], 'movement:y')


def on_message(mqttc, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    protoc = map(lambda s: s.strip(), msg.payload.split(':'))
    if protoc[0] == 'alarm':
        alarm()
    elif protoc[0] == 'do':
        remind(protoc[1])
    elif protoc[0] == 'clear':
        stop_reminding()


def button_handler(state):
    if state:
        mqttc.publish(config['server_topic'], 'alarm')


def button_handler2(state):
    if state:
        mqttc.publish(config['server_topic'], 'clear')


def knob_handler(pos):
    if pos < 12:
        mqttc.publish(config['server_topic'], 'movement:y')


def serial_thread():
    while True:
        if listen_loop:
            api.listen()


def main():
    global mqttc
    global api
    global config

    with open(sys.argv[1]) as config_file:
        for key, value in json.load(config_file).iteritems():
            if type(value) is unicode:
                config[key] = value.encode('ascii', 'ignore')
            else:
                config[key] = value

    mqttc = mosquitto.Mosquitto() 
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.connect(config['broker_ip'], 1883, 60)
    mqttc.subscribe(config['beacon_topic'], 0)

    mqttc.will_set(config['server_topic'], 'goodbye')

    api = Copernicus()
    api.command('led', False)
    api.set_handler('button1', button_handler)
    api.set_handler('button2', button_handler2)
    api.set_handler('knob', knob_handler)
    api.command('subscribe', '*')

    thread.start_new_thread(serial_thread, ())

    mqttc.loop_forever()


if __name__ == '__main__':
    main()
