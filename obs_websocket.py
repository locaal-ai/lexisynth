import json
from os import path
import time
import obsws_python as obs
from ls_logging import logger
from queue import Queue
from PyQt6.QtCore import QThread

from storage import fetch_data


def open_obs_websocket(server_info):
    # Open a websocket connection to OBS
    try:
        cl = obs.ReqClient(
            host=server_info["ip"],
            port=server_info["port"],
            password=server_info["password"],
            timeout=10,
        )
        resp = cl.get_version()
        logger.info(f"OBS Version: {resp.obs_version}")
        return cl
    except Exception as e:
        logger.warn(f"Error: {e}")
        return None


def open_obs_websocket_from_settings():
    # Open a websocket connection to OBS using settings
    settings = fetch_data("settings.json", "settings", {})
    obs_host = settings.get("obs_host", "localhost")
    obs_port = settings.get("obs_port", "4455")
    obs_password = settings.get("obs_password", "")
    return open_obs_websocket(
        {"ip": obs_host, "port": obs_port, "password": obs_password}
    )


def disconnect_obs_websocket(obs_client: obs.ReqClient):
    # Disconnect the OBS websocket
    try:
        obs_client.base_client.ws.close()
    except Exception as e:
        logger.warn(f"Error: {e}")


def get_all_sources(obs_client: obs.ReqClient):
    # Get all the sources from OBS
    try:
        # get all scenes
        resp = obs_client.get_scene_list()
        scenes = resp.scenes
        # get all sources from all scenes
        sources = []
        for scene in scenes:
            resp = obs_client.get_scene_item_list(scene["sceneName"])
            # add the sources with their scene name
            for source in resp.scene_items:
                source["sceneName"] = scene["sceneName"]
                sources.append(source)
        return sources
    except Exception as e:
        logger.exception("Error: unable to get all sources")
        return None


def get_all_text_sources(obs_client: obs.ReqClient):
    # Get all the text sources from OBS
    sources = get_all_sources(obs_client)
    if sources is None:
        return None
    text_sources = []
    for source in sources:
        if str(source["inputKind"]).startswith("text_"):
            source_settings = obs_client.get_input_settings(
                source["sourceName"]
            ).input_settings
            # check if source has text
            if "text" in source_settings:
                text_sources.append(source)
    return text_sources


def get_source_by_name(obs_client: obs.ReqClient, source_name):
    # Get a source from OBS by name
    try:
        # get all scenes
        resp = obs_client.get_scene_list()
        scenes = resp.scenes
        # get all sources from all scenes
        sources = []
        for scene in scenes:
            resp = obs_client.get_scene_item_list(scene["sceneName"])
            # add the sources with their scene name
            for source in resp.scene_items:
                source["sceneName"] = scene["sceneName"]
                sources.append(source)
        # find the source by name
        for source in sources:
            if source["sourceName"] == source_name:
                return source
        return None
    except Exception as e:
        logger.exception("Error: unable to get source by name")
        return None


class OBSPoller(QThread):
    def __init__(
        self,
        obs_client: obs.ReqClient,
        obs_source_name: str,
        queue: Queue,
        polling_freq=1000,
    ):
        super().__init__()
        self.obs_client = obs_client
        self.obs_source_name = obs_source_name
        self.queue = queue
        self.polling_freq = polling_freq
        self.running = False
        self.last_content = None

    def stop(self):
        self.running = False

    def run(self):
        logger.info("OBS polling thread started")
        self.running = True
        while self.running:
            try:
                # get the value of the source
                source = get_source_by_name(self.obs_client, self.obs_source_name)
                if source is None:
                    logger.error(f"Source {self.obs_source_name} not found")
                    break
                source_settings = self.obs_client.get_input_settings(
                    source["sourceName"]
                ).input_settings
                source_content = (
                    source_settings["text"] if "text" in source_settings else None
                )
                if source_content and source_content != self.last_content:
                    self.queue.put_nowait(source_content)
                    self.last_content = source_content
            except Exception as e:
                logger.exception(f"Error: {e}")
            time.sleep(self.polling_freq / 1000)
        logger.info("OBS polling thread stopped")
