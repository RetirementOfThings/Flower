import datetime
import time
import json
import sys
import thread

import mosquitto

mqttc = None
config = dict()

reminders = dict()
pending = None

beacons = set()
last_movement = None


def to_beacon_topic(server_topic):
    offset = len(config['server_topic']) + 1
    return server_topic[offset:]


def set_reminder(name, time_):
    reminders[name] = time_
    print 'Reminder "{0}" set to {1}.'.format(name, time_)


def unset_reminder(name):
    if name not in reminders:
        print 'No reminder called "{0}".'.format(name)
        return
    del reminders[name]
    print 'Reminder "{0}" cancelled.'.format(name)


def remind(name):
    global pending
    print 'Reminder: "{0}"'.format(name)
    pending = 0
    for beacon in beacons:
        mqttc.publish(beacon, 'do:' + name)
        print '--> ' + beacon


def dismiss_reminder():
    global pending
    pending = None
    for beacon in beacons:
        mqttc.publish(beacon, 'clear')
        print '--> ' + beacon


def sound_alarm():
    print 'ALARM'
    for beacon in beacons:
        mqttc.publish(beacon, 'alarm')
        print '--> ' + beacon


def update_movement(beacon_topic, moving):
    global last_movement
    beacon_topic = to_beacon_topic(beacon_topic)
    beacons.add(beacon_topic)
    print '{0}:{1} movement'.format(beacon_topic, '' if moving else ' no')
    if not moving:
        sound_alarm()
    last_movement = 0


def drop_beacon(topic):
    beacon_topic = to_beacon_topic(topic)
    beacons.remove(beacon_topic)
    print 'Beacon "{0}" dropped.'.format(beacon_topic)


# noinspection PyUnusedLocal
def on_connect(mqttc_, obj, rc):
    print 'Server "{0}" connected'.format(config['server_topic'])


# noinspection PyUnusedLocal
def on_message(mqttc_, obj, msg):
    print '({0} {1})'.format(msg.topic, str(msg.payload))

    parts = msg.payload.split(':')

    if parts[0] == 'set':
        set_reminder(parts[1], datetime.time(*map(int, parts[2:4])))
    elif parts[0] == 'unset':
        unset_reminder(parts[1])
    elif parts[0] == 'movement':
        update_movement(msg.topic, parts[1][0] == 'y')
    elif parts[0] == 'goodbye':
        drop_beacon(msg.topic)
    elif parts[0] == 'alarm':
        sound_alarm()
    elif parts[0] == 'clear':
        dismiss_reminder()


def minute_thread():
    global pending
    global last_movement
    while True:
        if pending is None:
            time_tuple = datetime.datetime.now().timetuple()[3:5]
            now = datetime.time(*time_tuple)
            for reminder_name, reminder_time in reminders.iteritems():
                if reminder_time == now:
                    remind(reminder_name)
                    break
        else:
            pending += 1
            if pending >= config['reminder_timeout']:
                pending = None
                sound_alarm()
        if last_movement is not None:
            last_movement += 1
            if last_movement >= config['movement_timeout']:
                sound_alarm()
        time.sleep(60)


def main():
    global config
    global mqttc

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
    mqttc.subscribe(config['server_topic'] + '/#')

    thread.start_new_thread(minute_thread, ())

    mqttc.loop_forever()


if __name__ == '__main__':
    main()
