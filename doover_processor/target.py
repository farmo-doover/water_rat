import logging
from datetime import datetime, timezone

from pydoover.cloud import ProcessorBase, Channel
from pydoover import ui

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
        self.significant_event_channel = self.api.create_channel("significantEvent", self.agent_id)

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

        msg_inner = raw_message.get("message", None)
        if msg_inner is None:
            logging.info("No message field in message - skipping processing")
            return

        ## TODO - Publish the location
        if "gps_lat" in msg_inner and msg_inner["gps_lat"] != 0 and "gps_lng" in msg_inner and msg_inner["gps_lng"] != 0:
            position = {
                'lat': msg_inner["gps_lat"],
                'long': msg_inner["gps_lng"],
            }
            self.location_channel.publish(position)

        if "status" in msg_inner:
            status = msg_inner["status"]
            if status > 0:
                self.ui_manager.update_variable("waterRatStatus", True)
                self.ui_manager.update_variable("waterRatElement", 0)
            else:
                self.ui_manager.update_variable("waterRatStatus", False)
                self.ui_manager.update_variable("waterRatElement", 75)
                self.ui_manager.add_children(
                    ui.WarningIndicator("waterRatProblem", "Problem Here")
                )

                try:
                    if self.alert_required():
                        msg = "Water Rat has detected a problem"
                        self.significant_event_channel.publish(msg, save_log=True)
                except Exception as e:
                    logging.error("Error in alert_required: " + str(e))

        if "batv" in msg_inner:
            self.ui_manager.update_variable("batteryVoltage", msg_inner["batv"])

        if "rsrp" in msg_inner:
            rsrp = msg_inner["rsrp"]
            signal_strength_percent = self.rsrp_to_percentage(rsrp)
            self.ui_manager.update_variable("signalStrength", signal_strength_percent)

        self.ui_manager.push(should_remove=True, even_if_empty=True)


    ## Helpers to assess wether alerts required
    def alert_required(self, current_status=True):
        state_messages = self.uplink_channel.fetch_messages()

        ## Search through the last few messages to find the last battery level
        if len(state_messages) < 2:
            logging.info("Not enough data to get previous levels")
            return current_status
        
        last_message = state_messages[1].fetch_payload()
        second_last_message = state_messages[2].fetch_payload()

        if self.alarm_in_message(last_message) and not self.alarm_in_message(second_last_message):
            return True
        return False

    def alarm_in_message(self, message):
        if "message" in message:
            message = message["message"]
        if "status" in message:
            return message["status"] > 0
        return False

    def rsrp_to_percentage(self, rsrp):
        
        min_rsrp = -100
        max_rsrp = -75
        signal_strength_percent = int(((rsrp - max_rsrp) / (max_rsrp - min_rsrp) + 1) * 100)
        signal_strength_percent = max(signal_strength_percent, 0)
        signal_strength_percent = min(signal_strength_percent, 100)

        return signal_strength_percent