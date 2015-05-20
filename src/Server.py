import mosquitto
import copernicus


def alarm(beacon_channels):
    for channel in beacon_channels:
        pass
    pass


def on_connect(mqttc, obj, rc):
    print('on connect')


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


def main():
    beacons = {}  # chanel:movement
    mqttc = mosquitto.Mosquitto()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.connect("127.0.0.1", 1883, 60)
    mqttc.subscribe("flower/#", 0)
    mqttc.loop_forever()


if __name__ == '__main__':
    main()
