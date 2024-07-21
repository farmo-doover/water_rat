import logging
from datetime import datetime, timezone

from pydoover.cloud import ProcessorBase, Channel

from ui import construct_ui


class target(ProcessorBase):

    ui_state_channel: Channel
    # ui_cmds_channel: Channel


    def setup(self):

        self.include_vocs = False

        # Get the required channels        
        self.ui_state_channel = self.api.create_channel("ui_state", self.agent_id)
        self.ui_cmds_channel = self.api.create_channel("ui_cmds", self.agent_id)
        self.location_channel = self.api.create_channel("location", self.agent_id)

        self.uplink_channel = self.api.create_channel("farmo_uplink_recv", self.agent_id)

        ## Construct the UI
        self._ui_elements = construct_ui()
        self.ui_manager.set_children(self._ui_elements)
        self.ui_manager.pull()
    

    def process(self):
        message_type = self.package_config.get("message_type")

        if message_type == "DEPLOY":
            self.on_deploy()
        elif message_type == "DOWNLINK":
            self.on_downlink()
        elif message_type == "UPLINK":
            self.on_uplink()


    def on_deploy(self):
        ## Run any deployment code here

        # Construct the UI
        self.ui_manager.push(should_remove=True)

        # Publish a dummy message to uplink to trigger a new process of data
        last_uplink_packet = self.uplink_channel.fetch_aggregate()
        if last_uplink_packet is not None:
            self.uplink_channel.publish(last_uplink_packet)

    def on_downlink(self):
        # Run any downlink processing code here
        pass

        # ## An updates of deployment start time processed in setup
        # ## Just need to push any changes here
        # self.ui_manager.push(should_remove=False)


    def on_uplink(self):
        # Run any uplink processing code here
        if not (self.message and self.message.id):
            logging.info("No trigger message passed - fetching last message")
            self.message = self.uplink_channel.last_message
            if self.message is None:
                logging.info("No message found - skipping processing")
                return

        raw_message = self.message.fetch_payload()
        logging.info("Received message: " + str(raw_message))


        ## TODO - Publish the location

        angle = 7
        battery = 6.2

        self.ui_manager.update_variable("waterRatAngle", angle)
        self.ui_manager.update_variable("batteryVoltage", battery)

        self.ui_manager.push(should_remove=False)