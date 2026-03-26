#!/usr/bin/env python3
# 简化版：一个用户同时用多个 Client ID 连接 MQTT，并自动重连
import paho.mqtt.client as mqtt
import time
import threading

# 配置
USERNAME = "admindest"
PASSWORD = "public"
BROKER = "localhost"
PORT = 1883

# 要启动的客户端列表
CLIENT_IDS = ["Client1", "Client2", "Client3"]

def create_client(client_id):
    """创建并配置一个 MQTT 客户端"""
    client = mqtt.Client(client_id=client_id)
    client.username_pw_set(USERNAME, PASSWORD)

    # 定义回调函数，使用闭包捕获 client_id
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"{client_id} 连接成功")
        else:
            print(f"× {client_id} 连接失败，返回码: {rc}")

    def on_disconnect(client, userdata, rc):
        print(f"△ {client_id} 断开连接，正在尝试重连...")
        # 自动重连循环
        while True:
            try:
                if client.reconnect() == 0:
                    print(f"{client_id} 重连成功")
                    break
            except Exception as e:
                print(f"{client_id} 重连中... {e}")
                time.sleep(5)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # 启动连接（带自动重试）
    while True:
        try:
            client.connect(BROKER, PORT, keepalive=60)
            break
        except Exception as e:
            print(f"{client_id} 初始连接失败，5秒后重试... {e}")
            time.sleep(5)

    client.loop_start()
    return client

def main():
    print("开始连接多个客户端...")
    clients = []

    for cid in CLIENT_IDS:
        print(f"创建客户端: {cid}")
        client = create_client(cid)
        clients.append(client)

    print("\n所有客户端已启动，保持运行（按 Ctrl+C 退出）")

    try:
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭所有连接...")
        for c in clients:
            c.loop_stop()
            c.disconnect()
        print("□ 退出完成")

if __name__ == "__main__":
    main()