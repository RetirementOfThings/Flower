import mosquitto


should_remind = True


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
    print('on connetc')


def on_message(mqttc, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    protoc = msg.split(':').strip()
    if protoc[0] == 'alarm':
        alarm()
    elif protoc[0] == 'do':
        remind()
    elif protoc[0] == 'clear':
        stop_reminding()


def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


def button_handler(state):
    if state:
        print 'alarm'
        alarm()
        mqttc.publish("flower/1", 'alarm', 0, True)


def button_handler2(state):
    if state:
        stop_reminding()
        mqttc.publish("flower/1", 'clear', 0, True)


def knob_handler(pos):
    mqttc.publish("flower/1", 'movement:y', 0, True)


def main():
    mqttc = mosquitto.Mosquitto() 
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.connect("127.0.0.1", 1883, 60)
    mqttc.subscribe("flower/1", 0)
    api.set_handler('button1', button_handler)
    api.set_handler('button2', button_handler2)
    api.set_handler('knob', knob_handler)
    api.command('subscribe', 'knob')
    mqttc.loop_forever()


if __name__ == '__main__':
    main()