#!/usr/bin/env python3
import logging, time, asyncio

from collections.abc import Iterable

import grpc

from .grpc_stubs import platform_iface_pb2, platform_iface_pb2_grpc


class pulse_counter:

    def __init__(self, platform_iface, pin, edge="rising", callback=None, rate_window_secs=60, auto_start=True):
        self.platform_iface = platform_iface
        self.pin = pin
        self.callback = callback
        self.rate_window_secs = rate_window_secs
        self.count = 0

        self.start_time = time.time()
        self.pulse_grace_period = 0.2  # Need to ignore pulses for a short period after starting
        self.pulse_timestamps = []

        if auto_start:
            self.start_listener()

    def start_listener(self):
        self.start_time = time.time()
        self.platform_iface.start_di_pulse_listener(self.pin, self.receive_pulse, edge="rising", start_count=self.count)

    def receive_pulse(self, di, di_value, dt_secs, counter, edge):
        if time.time() - self.start_time < self.pulse_grace_period:
            logging.info("Ignoring pulse on di=" + str(di) + " with dt=" + str(dt_secs) + "s")
            return
        logging.info("Received pulse on di=" + str(di) + " with dt=" + str(dt_secs) + "s")
        self.count += 1
        self.pulse_timestamps += [time.time()]
        if self.callback is not None:
            self.callback(di, di_value, dt_secs, self.count, edge)

    def clean_pulse_timestamps(self):
        if len(self.pulse_timestamps) == 0:
            return

        ## Remove timestamps older than the rate window
        while len(self.pulse_timestamps) > 0 and self.pulse_timestamps[0] < time.time() - self.rate_window_secs:
            self.pulse_timestamps.pop(0)

    def set_rate_window(self, rate_window_secs):
        self.rate_window_secs = rate_window_secs

    def get_rate_window(self):
        return self.rate_window_secs

    def get_pulses_per_minute(self):
        self.clean_pulse_timestamps()
        return len(self.pulse_timestamps) * 60 / self.rate_window_secs

    def set_counter(self, counter):
        self.count = counter

    def get_counter(self):
        return self.count
    


class platform_iface:
    def __init__(
            self, 
            plt_uri="localhost:50053", 
        ):
        
        self.plt_uri = plt_uri

        self.pulse_counter_listeners = []

    def close(self):
        for listener in self.pulse_counter_listeners:
            listener.cancel()
        logging.info("Closing device agent interface...")

    def make_request(self, stub_call, request):
        try:
            with grpc.insecure_channel(self.plt_uri) as channel:
                stub = platform_iface_pb2_grpc.platformIfaceStub(channel)
                response = getattr(stub, stub_call)(request)
                return response
        except Exception as e:
            logging.warning("Error making platform iface request: " + str(e))
            return None
    
    def process_response(self, response, response_field: str = None):
        if response is None:
            logging.warning("Error processing " + str(response_field) + " response: " + str(response))
            return None
        if not response.response_header.success:
            logging.warning("Error processing " + str(response_field) + " response: " + str(response.response_header.message))
            return None

        if not response_field:
            return

        res = getattr(response, response_field, None)
        if isinstance(res, Iterable):
            res = list(res)

        if isinstance(res, list) and len(res) == 1:
            return res[0]

        return res

    def get_di(self, di):
        if type(di) == int:
            di = [di]
        elif type(di) != list:
            logging.error("Invalid type for digital input: " + str(type(di)))
            return None
        
        # Above section is to facilitate the following:
        # get_di(1)
        # get_di([1,4,2])

        result = self.make_request('getDI', platform_iface_pb2.getDIRequest(di=di))
        return self.process_response(result, 'di')
    
    def get_new_pulse_counter(self, di, edge="rising", callback=None, rate_window_secs=20, auto_start=True):
        return pulse_counter(self, di, edge=edge, callback=callback, rate_window_secs=rate_window_secs, auto_start=auto_start)

    def start_di_pulse_listener(self, di, callback, edge="rising", start_count=0):
        ## Callback should be a function that takes the following arguments:
        ## di, di_value, dt_secs, counter, edge

        listener = asyncio.ensure_future(self.recv_di_pulses(di, callback, edge=edge, start_count=start_count))
        self.pulse_counter_listeners += [listener]
    
    async def recv_di_pulses(self, di, callback, edge="rising", start_count=0):
        counter = start_count

        ## Setup the connection to the doover device agent (DDA)
        async with grpc.aio.insecure_channel(self.plt_uri) as channel:

            channel_stream = platform_iface_pb2_grpc.platformIfaceStub(channel).startPulseCounter( platform_iface_pb2.pulseCounterRequest(di=di))
            while True:
                try:
                    response = await channel_stream.read()
                    logging.debug("Received response from pulseCounter for di=" + str(di))
                    
                    if hasattr(response, 'dt_secs') and response.dt_secs is not None and response.dt_secs > 0:
                        ## Increment the counter
                        counter += 1
                        ## Call the callback function with the response
                        callback(di, di_value=response.value, dt_secs=response.dt_secs, counter=counter, edge=edge)
                        
                except StopAsyncIteration:
                    logging.debug("pulseCounter for di=" + str(di) + " ended.")
                    break

                except Exception as e:
                    logging.error("Error receiving pulse for di=" + str(di) + ": " + str(e), exc_info=e)
                    await asyncio.sleep(1)

    ####

    def get_ai(self, ai):
        if type(ai) == int:
            ai = [ai]
        elif type(ai) != list:
            logging.error("Invalid type for analog input: " + str(type(ai)))
            return None
        
        # Above section is to facilitate the following:
        # get_ai(1)
        # get_ai([1,4,2])

        result = self.make_request('getAI', platform_iface_pb2.getAIRequest(ai=ai))
        return self.process_response(result, 'ai')


    def get_do(self, do):

        if type(do) == int:
            do = [do]
        elif type(do) != list:
            logging.error("Invalid type for digital output: " + str(type(do)))
            return None
        
        # Above section is to facilitate the following:
        # get_do(1) 
        # get_do([1,4,2])

        result = self.make_request('getDO', platform_iface_pb2.getDORequest(do=do))
        return self.process_response(result, 'do')
    

    def set_do(self, do, value):

        if type(do) == int:
            do = [do]
        elif type(do) != list:
            logging.error("Invalid type for digital output: " + str(type(do)))
            return None
        
        if type(value) == int:
            value = [value]
        if type(value) == bool:
            value = [value]
        elif type(value) != list:
            logging.error("Invalid type for digital output value: " + str(type(value)))
            return None
        
        if len(do) != len(value):
            if len(value) == 1:
                value = [value[0]] * len(do)
            else:
                logging.error("Digital output and value lists are not the same length.")
                return None
            
        # Above section is to facilitate the following:
        # set_do(1, 1) => [1],[1]
        # set_do([1,4,2], 0) => [1,4,2], [0,0,0]
        # set_do([1,4,2], [0,1,0]) => [1,4,2], [0,1,0]
        
        result = self.make_request('setDO', platform_iface_pb2.setDORequest(do=do, value=value))
        return self.process_response(result, 'do')
    

    def schedule_do(self, do, value, time):
            
            if type(do) == int:
                do = [do]
            elif type(do) != list:
                logging.error("Invalid type for digital output: " + str(type(do)))
                return None
            
            if type(value) == int:
                value = [value]
            elif type(value) != list:
                logging.error("Invalid type for digital output value: " + str(type(value)))
                return None
            
            if len(do) != len(value):
                if len(value) == 1:
                    value = [value[0]] * len(do)
                else:
                    logging.error("Digital output and value lists are not the same length.")
                    return None
                
            # Above section is to facilitate the following:
            # schedule_do(1, 1, 1) => [1],[1],1
            # schedule_do([1,4,2], 0, 1) => [1,4,2], [0,0,0], 1
            # schedule_do([1,4,2], [0,1,0], 1) => [1,4,2], [0,1,0], 1
            
            result = self.make_request('scheduleDO', platform_iface_pb2.scheduleDORequest(do=do, value=value, time_secs=time))
            return self.process_response(result, 'do')
    

    ####

    def get_ao(self, ao):

        if type(ao) == int:
            ao = [ao]
        elif type(ao) != list:
            logging.error("Invalid type for analog output: " + str(type(ao)))
            return None
        
        # Above section is to facilitate the following:
        # get_ao(1) 
        # get_ao([1,4,2])

        result = self.make_request('getAO', platform_iface_pb2.getAORequest(ao=ao))
        return self.process_response(result, 'ao')


    def set_ao(self, ao, value):
        if type(ao) == int:
            ao = [ao]
        elif type(ao) != list:
            logging.error("Invalid type for analog output: " + str(type(ao)))
            return None
        
        if type(value) == int:
            value = [value]
        elif type(value) != list:
            logging.error("Invalid type for analog output value: " + str(type(value)))
            return None
        
        if len(ao) != len(value):
            if len(value) == 1:
                value = [value[0]] * len(ao)
            else:
                logging.error("Digital output and value lists are not the same length.")
                return None
            
        # Above section is to facilitate the following:
        # set_ao(1, 1) => [1],[1]
        # set_ao([1,4,2], 0) => [1,4,2], [0,0,0]
        # set_ao([1,4,2], [0,1,0]) => [1,4,2], [0,1,0]
        
        result = self.make_request('setAO', platform_iface_pb2.setAORequest(ao=ao, value=value))
        return self.process_response(result, 'ao')


    def schedule_ao(self, ao, value, time):

        if type(ao) == int:
            ao = [ao]
        elif type(ao) != list:
            logging.error("Invalid type for analog output: " + str(type(ao)))
            return None
        
        if type(value) == int:
            value = [value]
        elif type(value) != list:
            logging.error("Invalid type for analog output value: " + str(type(value)))
            return None
        
        if len(ao) != len(value):
            if len(value) == 1:
                value = [value[0]] * len(ao)
            else:
                logging.error("Digital output and value lists are not the same length.")
                return None
            
        # Above section is to facilitate the following:
        # schedule_ao(1, 1, 1) => [1],[1],1
        # schedule_ao([1,4,2], 0, 1) => [1,4,2], [0,0,0], 1
        # schedule_ao([1,4,2], [0,1,0], 1) => [1,4,2], [0,1,0], 1
        
        result = self.make_request('scheduleAO', platform_iface_pb2.scheduleAORequest(ao=ao, value=value, time_secs=time))
        return self.process_response(result, 'ao')
    
    def get_system_voltage(self):
        res = self.make_request("getInputVoltage", platform_iface_pb2.getInputVoltageRequest())
        return self.process_response(res, 'voltage')

    def get_system_temperature(self):
        res = self.make_request("getTemperature", platform_iface_pb2.getTemperatureRequest())
        return self.process_response(res, 'temperature')

    def reboot(self):
        res = self.make_request("reboot", platform_iface_pb2.rebootRequest())
        return self.process_response(res)

    def shutdown(self):
        res = self.make_request("shutdown", platform_iface_pb2.shutdownRequest())
        return self.process_response(res)

    def schedule_startup(self, time_secs):
        res = self.make_request("scheduleStartup", platform_iface_pb2.scheduleStartupRequest(time_secs=time_secs))
        return self.process_response(res, 'time_secs')

    def schedule_shutdown(self, time_secs):
        res = self.make_request("scheduleShutdown", platform_iface_pb2.scheduleShutdownRequest(time_secs=time_secs))
        return self.process_response(res, 'time_secs')


if __name__ == "__main__":
    P_IFACE = platform_iface()
    print(P_IFACE.set_ao([3,0,1], 1))