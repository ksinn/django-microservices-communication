from services_communication.consumer import utils


def run_consumer():
    utils.check_consumer_settings()
    consumer = utils.build_consumer_by_settings()
    consumer.run()
