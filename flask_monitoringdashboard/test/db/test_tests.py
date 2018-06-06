"""
    This file contains all unit tests for the monitor-rules-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/tests.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, add_fake_test_runs,\
    EXECUTION_TIMES, NAME, TEST_NAMES

NAME2 = 'main2'
SUITE = 3


class TestDBTests(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()
        add_fake_test_runs()

    def test_add_test_result(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import add_test_result, get_suite_measurements, add_or_update_test
        from flask_monitoringdashboard.database.tested_endpoints import add_endpoint_hit
        from flask_monitoringdashboard import config
        import datetime
        with session_scope() as db_session:
            self.assertEqual(get_suite_measurements(db_session, SUITE), [0])
            for exec_time in EXECUTION_TIMES:
                for test in TEST_NAMES:
                    add_or_update_test(db_session, test, True, datetime.datetime.utcnow(), config.version,
                                       datetime.datetime.utcnow())
                    add_test_result(db_session, test, exec_time, datetime.datetime.utcnow(), config.version, SUITE, 0)
                add_endpoint_hit(db_session, NAME, exec_time, test, config.version, SUITE)
            result = get_suite_measurements(db_session, SUITE)
            self.assertEqual(len(result), len(EXECUTION_TIMES) * len(TEST_NAMES))

    def test_get_results(self):
        """
            Test whether the function returns the right values.
        """
        self.test_add_test_result()  # can be replaced by test_add_test_result, since this function covers two tests

    def test_get_suites(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_test_suites
        self.test_add_test_result()
        with session_scope() as db_session:
            self.assertEqual(get_test_suites(db_session), [SUITE])

    def test_get_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_suite_measurements
        with session_scope() as db_session:
            self.assertEqual(get_suite_measurements(db_session, SUITE), [0])
            self.test_add_test_result()
            result = get_suite_measurements(db_session, SUITE)
            self.assertEqual(len(EXECUTION_TIMES) * 2, len(result))

    def test_get_test_measurements(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard.database.tests import get_endpoint_measurements_job
        with session_scope() as db_session:
            initial_len = len(get_endpoint_measurements_job(db_session, NAME, SUITE))
            self.test_add_test_result()
            result = get_endpoint_measurements_job(db_session, NAME, SUITE)
            self.assertEqual(initial_len + len(EXECUTION_TIMES), len(result))
