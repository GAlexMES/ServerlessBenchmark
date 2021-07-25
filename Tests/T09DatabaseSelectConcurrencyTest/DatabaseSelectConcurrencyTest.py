import os
from Tests.Provider import Provider
from Tests.T08DatabaseConcurrencyTest.DatabaseConcurrencyTest import DatabaseConcurrencyTest


class DatabaseSelectConcurrencyTest(DatabaseConcurrencyTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "DatabaseSelectConcurrency.jmx")
    options = {
        Provider.aws: ["Select", "Write", "SelectAgain"],
    }

    def get_test_name(self):
        return "T09DatabaseSelectConcurrencyTest"


