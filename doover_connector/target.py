#!/usr/bin/python3
import os, sys, time, json, traceback, logging

from pydoover.cloud import ProcessorBase, Channel
# from pydoover.cloud import Client


class target(ProcessorBase):


    def setup(self):
        ## Do any setup you would like to do here
        pass

    def process(self):

        payload = self.message.fetch_payload()
        if not isinstance(payload, dict):
            payload = json.loads(payload)

        if not 'unitID' in payload:
            logging.info( "No unit ID passed - skipping processing" )
            return
        
        serial_num = payload['unitID']
        try: serial_num = int(serial_num)
        except: 
            logging.warning("Unit ID is not an integer - skipping processing")
            return

        agents = self.api.get_agent_list()
        logging.info(str(len(agents)) + " accessible agents to process")

        for a in agents:
            if a.deployment_config is not None and 'FARMO_IMEI' in a.deployment_config:
                if serial_num == a.deployment_config['FARMO_IMEI']:
                    agent_key = a.agent_id
                    logging.info('Found agent ' + str(agent_key) + " with matching serial number " + str(serial_num))

                    self.api.publish_to_channel_name(
                        agent_id=agent_key,
                        channel_name="farmo_uplink_recv",
                        data=json.dumps(payload)
                    )

                    logging.info("Published to farmo_uplink_recv channel")
                    return

        logging.warning("Did not find an agent with matching FARMO_IMEI == " + str(serial_num) + " in deployment config")
