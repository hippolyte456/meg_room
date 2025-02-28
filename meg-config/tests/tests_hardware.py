receive_port1 = '/dev/parport0' 
receive_port2 = '/dev/parport1' 
receive_port3 = '/dev/parport4'


if __name__ == '__main__':

    available_ports = check_parallel_ports()
    print(f"Available parallel ports: {available_ports}")
    expyriment.control.defaults.window_mode = True
    exp = design.Experiment(name="Explore+", text_size=30)
    response_meg = response_in_MEG(exp, receive_port1, receive_port2, receive_port3)
    port2send = response_meg.port2
    port2send.send(data=0)
    responses = []
    while len(responses)<9:
        key, rt = response_meg.wait(duration=20)

