import json
import sys
from copernicus import Copernicus
import mosquitto


should_remind = True
mqttc = None
api = None
config = dict()


def alarm():
    print 'alarm'


def remind():
    global should_remind
    while should_remind:
        print 'take your pill'
    print 'thank you for taking your pill'


def stop_reminding():
    global should_remind
    should_remind = False


def on_connect(mqttc, obj, rc):
    print 'Beacon {0} connected'.format(config['beacon_topic'])
    mqttc.publish(config['server_topic'], 'movement:y')


def on_message(mqttc, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    protoc = map(lambda s: s.strip(), msg.split(':'))
    if protoc[0] == 'alarm':
        alarm()
    elif protoc[0] == 'do':
        remind()
    elif protoc[0] == 'clear':
        stop_reminding()


def button_handler(state):
    if state:
        print 'alarm'
        alarm()
        mqttc.publish(config['server_topic'], 'alarm', 0, True)


def button_handler2(state):
    if state:
        stop_reminding()
        mqttc.publish(config['server_topic'], 'clear', 0, True)


def knob_handler(pos):
    mqttc.publish(config['server_topic'], 'movement:y', 0, True)


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
    api.set_handler('button1', button_handler)
    api.set_handler('button2', button_handler2)
    api.set_handler('knob', knob_handler)
    api.command('subscribe', 'knob')

    mqttc.loop_forever()


if __name__ == '__main__':
    main()
