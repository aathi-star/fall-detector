import os
import time
from collections import deque

import joblib
import pandas as pd
import paho.mqtt.client as mqtt
import yaml

from utils import ensure_dirs, extract_features, json_to_sample


def main():
    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)

    mqtt_cfg = cfg['mqtt']
    model_path = cfg['model']['path']
    stream_cfg = cfg['stream']
    logic_cfg = cfg['logic']
    log_cfg = cfg['logging']

    sr = stream_cfg['sample_rate_hz']
    win_len = int(sr * stream_cfg['window_seconds'])
    step_len = int(sr * stream_cfg['step_seconds'])

    model = joblib.load(model_path)
    classes = list(model.classes_)
    fall_idx = classes.index('Fall')

    buffer = deque(maxlen=win_len)
    state = {'count': 0, 'last_alert': 0.0}

    def on_connect(client, userdata, flags, rc):
        client.subscribe(mqtt_cfg['topic'])

    def on_message(client, userdata, msg):
        sample = json_to_sample(msg.payload.decode())
        buffer.append(sample)
        state['count'] += 1
        if state['count'] >= win_len and (state['count'] - win_len) % step_len == 0:
            df = pd.DataFrame(list(buffer))
            feats = extract_features(df)
            X = pd.DataFrame([feats])
            proba = model.predict_proba(X)[0]
            fall_p = proba[fall_idx]
            label = 'FALL' if fall_p >= 0.5 else 'Normal'
            now = time.strftime('%H:%M:%S')
            print(f'[{now}] {label} p={fall_p:.2f}')
            if label == 'FALL' and time.time() - state['last_alert'] > logic_cfg['alert_cooldown_seconds']:
                print('*** ALERT: Possible fall detected!')
                ensure_dirs(log_cfg['dir'])
                with open(os.path.join(log_cfg['dir'], 'alerts.log'), 'a') as f:
                    f.write(f"{int(time.time())},fall\n")
                state['last_alert'] = time.time()

    client = mqtt.Client(mqtt_cfg['client_id'])
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_cfg['host'], mqtt_cfg['port'], mqtt_cfg['keepalive'])
    client.loop_forever()


if __name__ == '__main__':
    main()
