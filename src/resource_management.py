from datetime import datetime, timedelta
import logging
from requests.exceptions import RequestException, Timeout
from json import JSONDecodeError


class ResourceCache:

    def __init__(self):
        self.resources = {}

    def add_resource(self, resource):
        self.resources[resource.name] = resource

    def __getitem__(self, name):
        resource = self.resources[name]
        if resource.valid():
            return resource.content
        else:
            return resource.renew().content

    def __contains__(self, name):
        return name in self.resources


class Resource:
    TIME_INF = 1e10
    TIME_DAY = 86400
    TIME_HOUR = 3600

    def __init__(self, name, lifetime=TIME_HOUR / 2, max_retry=3, retry_window=TIME_HOUR / 2, timeout=2):
        self.name = name
        self.lifetime = lifetime
        self.content = {}
        self.last_updated = None
        self.max_retry = max_retry
        self.retry_window = retry_window
        self.prevent_retry_until = datetime.min
        self.timeout = timeout

    def renew(self, attempt=1):
        logging.debug("Renewing resource '{}', attempt #{}".format(self.name, attempt))
        if datetime.now() < self.prevent_retry_until:
            logging.debug("Not allowing retries until {}".format(self.prevent_retry_until))
        elif attempt > self.max_retry:
            self.prevent_retry_until = datetime.now() + timedelta(0, 1800)
            logging.warning("Exceeded {} retries for resource '{}'".format(self.max_retry, self.name))
        else:
            try:
                self.content = self._renew_resource()
                self.last_updated = datetime.now()
            except Timeout:
                self.renew(attempt + 1)
            except JSONDecodeError:
                logging.warning("Failed to parse response for resource '{}'".format(self.name))
            except RequestException as e:
                logging.warning("Request failed for resource '{}' -- {}".format(self.name, str(e)))

        return self

    def _renew_resource(self):
        raise NotImplementedError

    def valid(self):
        return False if self.last_updated is None else (datetime.now() - self.last_updated).seconds < self.lifetime
