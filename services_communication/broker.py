import logging
import random
from datetime import time

import pika
from pika.exceptions import AMQPConnectionError

from services_communication.error import MessageNotConsumed

logger_consumer = logging.getLogger('services_communication.consumer')
logger_publisher = logging.getLogger('services_communication.publisher')


# class AsynchronousConsumer(object):
#     """This is an example consumer that will handle unexpected interactions
#     with RabbitMQ such as channel and connection closures.
#
#     If RabbitMQ closes the connection, this class will stop and indicate
#     that reconnection is necessary. You should look at the output, as
#     there are limited reasons why the connection may be closed, which
#     usually are tied to permission related issues or socket timeouts.
#
#     If the channel is closed, it will indicate a problem with one of the
#     commands that were issued and that should surface in the output as well.
#
#     """
#
#     def __init__(self,
#                  broker_url=None,
#                  queue=None,
#                  exchanges=None,
#                  binds=None,
#                  on_message_callback=None,
#                  **kwargs):
#         """Create a new instance of the consumer class, passing in the AMQP
#         URL used to connect to RabbitMQ.
#
#         :param str amqp_url: The AMQP url to connect with
#
#         """
#
#         if not queue:
#             logger.warning('Consumer will listen new unnamed queue')
#
#         if not exchanges:
#             logger.warning('Consumer will not create exchanges')
#
#         if not binds:
#             logger.warning('Consumer will not bind queue "%s" to any exchanges' % queue)
#
#         self.ioloop = asyncio.new_event_loop()
#         self._in_flight_tasks = set()
#
#         self.should_reconnect = False
#         self.was_consuming = False
#
#         self._connection = None
#         self._channel = None
#         self._closing = False
#         self._consumer_tag = None
#         self._url = broker_url
#         self._consuming = False
#         # In production, experiment with higher prefetch values
#         # for higher consumer throughput
#         self._prefetch_count = 1
#
#         self._QUEUE = queue
#         self._EXCHANGES = exchanges
#         self._BINDS = binds
#         self.on_message_callback = on_message_callback
#
#     def connect(self):
#         """This method connects to RabbitMQ, returning the connection handle.
#         When the connection is established, the on_connection_open method
#         will be invoked by pika.
#
#         :rtype: pika.adapters.asyncio_connection.AsyncioConnection
#
#         """
#         logger.debug('Connecting to %s', self._url)
#         return AsyncioConnection(
#             custom_ioloop=self.ioloop,
#             parameters=pika.URLParameters(self._url),
#             on_open_callback=self.on_connection_open,
#             on_open_error_callback=self.on_connection_open_error,
#             on_close_callback=self.on_connection_closed)
#
#     def close_connection(self):
#         self._consuming = False
#         if self._connection.is_closing or self._connection.is_closed:
#             logger.debug('Connection is closing or already closed')
#         else:
#             logger.debug('Closing connection')
#             self._connection.close()
#
#     def on_connection_open(self, _unused_connection):
#         """This method is called by pika once the connection to RabbitMQ has
#         been established. It passes the handle to the connection object in
#         case we need it, but in this case, we'll just mark it unused.
#
#         :param pika.adapters.asyncio_connection.AsyncioConnection _unused_connection:
#            The connection
#
#         """
#         logger.debug('Connection opened')
#         self.open_channel()
#
#     def on_connection_open_error(self, _unused_connection, err):
#         """This method is called by pika if the connection to RabbitMQ
#         can't be established.
#
#         :param pika.adapters.asyncio_connection.AsyncioConnection _unused_connection:
#            The connection
#         :param Exception err: The error
#
#         """
#         logger.error('Connection open failed: %s', err)
#         self.reconnect()
#
#     def on_connection_closed(self, _unused_connection, reason):
#         """This method is invoked by pika when the connection to RabbitMQ is
#         closed unexpectedly. Since it is unexpected, we will reconnect to
#         RabbitMQ if it disconnects.
#
#         :param pika.connection.Connection connection: The closed connection obj
#         :param Exception reason: exception representing reason for loss of
#             connection.
#
#         """
#         self._channel = None
#         if self._closing:
#             self._connection.ioloop.stop()
#         else:
#             logger.warning('Connection closed, reconnect necessary: %s', reason)
#             self.reconnect()
#
#     def reconnect(self):
#         """Will be invoked if the connection can't be opened or is
#         closed. Indicates that a reconnect is necessary then stops the
#         ioloop.
#
#         """
#         self.should_reconnect = True
#         self.stop()
#
#     def open_channel(self):
#         """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
#         command. When RabbitMQ responds that the channel is open, the
#         on_channel_open callback will be invoked by pika.
#
#         """
#         logger.debug('Creating a new channel')
#         self._connection.channel(on_open_callback=self.on_channel_open)
#
#     def on_channel_open(self, channel):
#         """This method is invoked by pika when the channel has been opened.
#         The channel object is passed in so we can make use of it.
#
#         Since the channel is now open, we'll declare the exchange to use.
#
#         :param pika.channel.Channel channel: The channel object
#
#         """
#         logger.debug('Channel opened')
#         self._channel = channel
#         self.add_on_channel_close_callback()
#         self.setup_exchanges()
#
#     def add_on_channel_close_callback(self):
#         """This method tells pika to call the on_channel_closed method if
#         RabbitMQ unexpectedly closes the channel.
#
#         """
#         logger.debug('Adding channel close callback')
#         self._channel.add_on_close_callback(self.on_channel_closed)
#
#     def on_channel_closed(self, channel, reason):
#         """Invoked by pika when RabbitMQ unexpectedly closes the channel.
#         Channels are usually closed if you attempt to do something that
#         violates the protocol, such as re-declare an exchange or queue with
#         different parameters. In this case, we'll close the connection
#         to shutdown the object.
#
#         :param pika.channel.Channel: The closed channel
#         :param Exception reason: why the channel was closed
#
#         """
#         logger.warning('Channel %i was closed: %s', channel, reason)
#         self.close_connection()
#
#     def setup_exchanges(self):
#         """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
#         command. When it is complete, the on_exchange_declareok method will
#         be invoked by pika.
#         """
#         self.on_exchange_declareok(None, self._EXCHANGES)
#
#     def on_exchange_declareok(self, _unused_frame, exchanges):
#         """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
#         command.
#
#         :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
#         :param List[Exchange] exchanges: exchanges ned declarate
#
#         """
#
#         if not exchanges:
#             logger.debug('All exchange declared')
#             self.setup_queue(self._QUEUE)
#             return
#
#         exchange, *other_exchanges = exchanges
#         logger.debug('Declaring exchange: %s', exchange.name)
#         cb = functools.partial(self.on_exchange_declareok, exchanges=other_exchanges)
#
#         self._channel.exchange_declare(
#             exchange=exchange.name,
#             exchange_type=exchange.type,
#             callback=cb)
#
#     def setup_queue(self, queue_name):
#         """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
#         command. When it is complete, the on_queue_declareok method will
#         be invoked by pika.
#
#         :param str|unicode queue_name: The name of the queue to declare.
#
#         """
#         logger.debug('Declaring queue %s', queue_name)
#         cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
#         self._channel.queue_declare(queue=queue_name, callback=cb, durable=True)
#
#     def on_queue_declareok(self, _unused_frame, userdata):
#         """Method invoked by pika when the Queue.Declare RPC call made in
#         setup_queue has completed. In this method we will bind the queue
#         and exchange together with the routing key by issuing the Queue.Bind
#         RPC command. When this command is complete, the on_bindok method will
#         be invoked by pika.
#
#         :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
#         :param str|unicode userdata: Extra user data (queue name)
#
#         """
#         self.setup_binds()
#
#     def setup_binds(self):
#         self.on_bindok(None, binds=self._BINDS)
#
#     def on_bindok(self, _unused_frame, binds=None):
#         """Invoked by pika when the Queue.Bind method has completed. At this
#         point we will set the prefetch count for the channel.
#
#         :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
#         :param list subscribes: Extra user data (subscribe for bind)
#
#         """
#
#         if not binds:
#             self.set_qos()
#             return
#
#         bind, *other_binds = binds
#         logger.debug('Binding %s to %s with %s', bind.exchange, self._QUEUE, bind.routing_key)
#         cb = functools.partial(self.on_bindok, binds=other_binds)
#
#         self._channel.queue_bind(
#             self._QUEUE,
#             bind.exchange,
#             routing_key=bind.routing_key,
#             callback=cb)
#
#     def set_qos(self):
#         """This method sets up the consumer prefetch to only be delivered
#         one message at a time. The consumer must acknowledge this message
#         before RabbitMQ will deliver another one. You should experiment
#         with different prefetch values to achieve desired performance.
#
#         """
#         self._channel.basic_qos(
#             prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)
#
#     def on_basic_qos_ok(self, _unused_frame):
#         """Invoked by pika when the Basic.QoS method has completed. At this
#         point we will start consuming messages by calling start_consuming
#         which will invoke the needed RPC commands to start the process.
#
#         :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
#
#         """
#         logger.debug('QOS set to: %d', self._prefetch_count)
#         self.start_consuming()
#
#     def start_consuming(self):
#         """This method sets up the consumer by first calling
#         add_on_cancel_callback so that the object is notified if RabbitMQ
#         cancels the consumer. It then issues the Basic.Consume RPC command
#         which returns the consumer tag that is used to uniquely identify the
#         consumer with RabbitMQ. We keep the value to use it when we want to
#         cancel consuming. The on_message method is passed in as a callback pika
#         will invoke when a message is fully received.
#
#         """
#         logger.debug('Issuing consumer related RPC commands')
#         self.add_on_cancel_callback()
#         self._consumer_tag = self._channel.basic_consume(
#             self._QUEUE, self.on_message)
#         self.was_consuming = True
#         self._consuming = True
#
#     def add_on_cancel_callback(self):
#         """Add a callback that will be invoked if RabbitMQ cancels the consumer
#         for some reason. If RabbitMQ does cancel the consumer,
#         on_consumer_cancelled will be invoked by pika.
#
#         """
#         logger.debug('Adding consumer cancellation callback')
#         self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
#
#     def on_consumer_cancelled(self, method_frame):
#         """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
#         receiving messages.
#
#         :param pika.frame.Method method_frame: The Basic.Cancel frame
#
#         """
#         logger.debug('Consumer was cancelled remotely, shutting down: %r',
#                      method_frame)
#         if self._channel:
#             self._channel.close()
#
#     def on_message(self, _unused_channel, basic_deliver, properties, body):
#         """Invoked by pika when a message is delivered from RabbitMQ. The
#         channel is passed for your convenience. The basic_deliver object that
#         is passed in carries the exchange, routing key, delivery tag and
#         a redelivered flag for the message. The properties passed in is an
#         instance of BasicProperties with the message properties and the body
#         is the message that was sent.
#
#         :param pika.channel.Channel _unused_channel: The channel object
#         :param pika.Spec.Basic.Deliver: basic_deliver method
#         :param pika.Spec.BasicProperties: properties
#         :param bytes body: The message body
#
#         """
#         logger.debug('Received message # %s from %s(%s): %s',
#                      basic_deliver.delivery_tag, basic_deliver.exchange, properties.app_id, body)
#
#         self.on_message_callback(basic_deliver, properties, body)
#         self.acknowledge_message(basic_deliver.delivery_tag)
#
#     def acknowledge_message(self, delivery_tag):
#         """Acknowledge the message delivery from RabbitMQ by sending a
#         Basic.Ack RPC method for the delivery tag.
#
#         :param int delivery_tag: The delivery tag from the Basic.Deliver frame
#
#         """
#         logger.debug('Acknowledging message %s', delivery_tag)
#         self._channel.basic_ack(delivery_tag)
#
#     def stop_consuming(self):
#         """Tell RabbitMQ that you would like to stop consuming by sending the
#         Basic.Cancel RPC command.
#
#         """
#         if self._channel:
#             logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
#             cb = functools.partial(
#                 self.on_cancelok, userdata=self._consumer_tag)
#             self._channel.basic_cancel(self._consumer_tag, cb)
#
#     def on_cancelok(self, _unused_frame, userdata):
#         """This method is invoked by pika when RabbitMQ acknowledges the
#         cancellation of a consumer. At this point we will close the channel.
#         This will invoke the on_channel_closed method once the channel has been
#         closed, which will in-turn close the connection.
#
#         :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
#         :param str|unicode userdata: Extra user data (consumer tag)
#
#         """
#         self._consuming = False
#         logger.debug(
#             'RabbitMQ acknowledged the cancellation of the consumer: %s',
#             userdata)
#         self.close_channel()
#
#     def close_channel(self):
#         """Call to close the channel with RabbitMQ cleanly by issuing the
#         Channel.Close RPC command.
#
#         """
#         logger.info('Closing the channel')
#         self._channel.close()
#
#     def run(self):
#         """Run the example consumer by connecting to RabbitMQ and then
#         starting the IOLoop to block and allow the AsyncioConnection to operate.
#
#         """
#         self._connection = self.connect()
#         self.ioloop.run_forever()
#
#     def stop(self):
#         """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
#         with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
#         will be invoked by pika, which will then closing the channel and
#         connection. The IOLoop is started again because this method is invoked
#         when CTRL-C is pressed raising a KeyboardInterrupt exception. This
#         exception stops the IOLoop which needs to be running for pika to
#         communicate with RabbitMQ. All of the commands issued prior to starting
#         the IOLoop will be buffered but not processed.
#
#         """
#         if not self._closing:
#             self._closing = True
#             logger.info('Stopping')
#             if self._consuming:
#                 self.stop_consuming()
#                 self._connection.ioloop.run_forever()
#             else:
#                 self._connection.ioloop.stop()
#             logger.info('Stopped')
#
#
# class ReconnectingAsyncConsumer(object):
#     """This is an example consumer that will reconnect if the nested
#     ExampleConsumer indicates that a reconnect is necessary.
#
#     """
#
#     def __init__(self, *args, **kwargs):
#         '''
#         :param args:
#         :param broker_url: str,
#         :param queue: str,
#         :param exchanges: List[Exchanges],
#         :param binds: List[Bind],
#         :param on_message_callback,
#         :param kwargs:
#         '''
#         self._reconnect_delay = 0
#         self.args = args
#         self.kwargs = kwargs
#         self._consumer = AsynchronousConsumer(*args, **kwargs)
#
#     def run(self):
#         while True:
#             try:
#                 self._consumer.run()
#             except KeyboardInterrupt:
#                 self._consumer.stop()
#                 break
#             self._maybe_reconnect()
#
#     def _maybe_reconnect(self):
#         if self._consumer.should_reconnect:
#             self._consumer.stop()
#             reconnect_delay = self._get_reconnect_delay()
#             logger.info('Reconnecting after %d seconds', reconnect_delay)
#             time.sleep(reconnect_delay)
#             self._consumer = AsynchronousConsumer(*self.args, **self.kwargs)
#
#     def _get_reconnect_delay(self):
#         if self._consumer.was_consuming:
#             self._reconnect_delay = 0
#         else:
#             self._reconnect_delay += 1
#         if self._reconnect_delay > 30:
#             self._reconnect_delay = 30
#         return self._reconnect_delay


class BlockedMixin:

    def _declare_queue(self, channel):
        channel.queue_declare(self._queue, durable=True)

    def _declare_exchanges(self, channel):
        for exchange in self._exchanges:
            channel.exchange_declare(exchange.name, exchange_type=exchange.type, durable=True)

    def _declare_binds(self, channel):
        for bind in self._binds:
            channel.queue_bind(self._queue, bind.exchange, routing_key=bind.routing_key)


class BlockedConsumer(BlockedMixin):

    def __init__(self,
                 broker_connection_parameters=None,
                 queue=None,
                 exchanges=None,
                 binds=None,
                 on_message_callback=None,
                 ignore_callback_error=False,
                 **kwargs):
        logger_consumer.info('Init {} with callback {}'.format(type(self).__name__, on_message_callback))
        self._broker_connection_parameters = broker_connection_parameters
        self._queue = queue
        self._exchanges = exchanges
        self._binds = binds
        self._on_message_callback = on_message_callback
        self._ignore_callback_error = ignore_callback_error

    def on_message(self, channel, method_frame, header_frame, body):
        logger_consumer.debug('Received message (dt:{}) from exchange {} with key {}'.format(method_frame.delivery_tag,
                                                                                             method_frame.exchange,
                                                                                             method_frame.routing_key))
        try:
            self._on_message_callback(method_frame, header_frame, body)
        except MessageNotConsumed as e:
            logger_consumer.debug('Message (dt:{}) not consume'.format(method_frame.delivery_tag))
            channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
            return
        except Exception as e:
            logger_consumer.exception('Message (dt:{}) consume raise error'.format(method_frame.delivery_tag))
            channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
            if self._ignore_callback_error:
                return
            raise
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def declair(self, channel):
        self._declare_queue(channel)
        self._declare_exchanges(channel)
        self._declare_binds(channel)

    def run(self):
        try:
                logger_consumer.debug("Connect to rabbit")
                with pika.BlockingConnection(parameters=self._broker_connection_parameters) as connection:
                    logger_consumer.debug("Open channel")
                    with connection.channel() as channel:
                        # channel.basic_qos(prefetch_count=15)
                        self.declair(channel)

                        channel.basic_consume(self._queue, self.on_message)
                        try:
                            logger_consumer.debug("Starting consuming")
                            channel.start_consuming()
                        except KeyboardInterrupt:
                            logger_consumer.info("Consuming interrupted")
                            channel.stop_consuming()
        except Exception:
            logger_consumer.exception("Error happened in consumer")


class BlockedReconnectingConsumer(BlockedConsumer):

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_reconnect_attempts = 3
        self.max_total_reconnect_attempts = self.max_reconnect_attempts * 5
        self.total_reconnect_attempts = 0
        self.is_declared = False

    def on_message(self, *args, **kwargs):
        self.total_reconnect_attempts = 0
        super().on_message(*args, **kwargs)

    def declair(self, channel):
        if not self.is_declared:
            super().declair(channel)
            self.is_declared = True

    def reconnect_pause_random_gen(self):
        yield random.randint(3, 8)

    def run(self):
        self.total_reconnect_attempts = 0
        reconnect_attempts = self.max_reconnect_attempts

        while True:
            try:
                    logger_consumer.info("Connect to rabbit")
                    with pika.BlockingConnection(parameters=self._broker_connection_parameters) as connection:
                        logger_consumer.info("Open channel")
                        with connection.channel() as channel:
                            reconnect_attempts = 0
                            # channel.basic_qos(prefetch_count=15)
                            self.declair(channel)

                            channel.basic_consume(self._queue, self.on_message)
                            try:
                                logger_consumer.info("Starting consuming")
                                channel.start_consuming()
                            except KeyboardInterrupt:
                                logger_consumer.info("Consuming interrupted")
                                channel.stop_consuming()
                                break
            except AMQPConnectionError as err:
                logger_consumer.error("Connection error on %s attempt: %s", reconnect_attempts, err)
                self.total_reconnect_attempts = self.total_reconnect_attempts + 1
                reconnect_attempts = reconnect_attempts + 1
                allow_reconnect = reconnect_attempts <= self.max_reconnect_attempts and self.total_reconnect_attempts <= self.max_total_reconnect_attempts
                if allow_reconnect:
                    pause = next(self.reconnect_pause_random_gen())
                    logger_consumer.info('Await {} before reconnect attempt'.format(pause))
                    time.sleep(pause)
                else:
                    logger_consumer.exception("Can not connect to broker")
                    break
            except Exception as err:
                logger_consumer.exception("Error happened in consumer")
                break


class BlockedPublisher(BlockedMixin):

    def __init__(self,
                 app_id=None,
                 broker_connection_parameters=None,
                 exchanges=None,
                 **kwargs):
        self._broker_connection_parameters = broker_connection_parameters
        self._exchanges = exchanges
        self._connection = None
        self._channel = None
        self._app_id = app_id or 'anonymous'

    def _publish(self,
                 exchange,
                 routing_key,
                 body):

        if not self._connection:
            logger_publisher.debug("Connect to rabbit")
            self._connection = pika.BlockingConnection(parameters=self._broker_connection_parameters)
        if not self._channel:
            logger_publisher.debug("Open channel")
            self._channel = self._connection.channel()
            self._channel.confirm_delivery()

        self._declare_exchanges(self._channel)

        return self._channel.basic_publish(
            exchange,
            routing_key,
            body,
            properties=pika.BasicProperties(
                content_type='text/json',
                delivery_mode=pika.DeliveryMode.Persistent,
                app_id=self._app_id
            ),
        )

    def publish(self, *args, **kwargs):
        try:
            self._publish(*args, **kwargs)
        except pika.exceptions.ConnectionClosedByBroker as err:
            # Uncomment this to make the example not attempt recovery
            # from server-initiated connection closure, including
            # when the node is stopped cleanly
            #
            # break
            logger_publisher.debug("Caught a connection error: {}, retrying...".format(err))
            self._retry_publish(*args, **kwargs)
        # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            logger_publisher.exception("Caught a channel error: {}, stopping...".format(err))
            raise err
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            logger_publisher.exception("Connection was closed, retrying...")
            self._retry_publish(*args, **kwargs)
        except Exception as err:
            logger_publisher.exception("Caught a error: {}, stopping...".format(err))
            raise err

    def _retry_publish(self, *args, **kwargs):
        logger_publisher.info("Retrying publish...")
        self._channel = None
        self._connection = None
        self._publish(*args, **kwargs)
