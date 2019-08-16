"""
Test to verify PVC creation performance
"""
import logging
import pytest

from ocs_ci.framework.testlib import tier1, E2ETest, polarion_id, bugzilla
from ocs_ci.ocs import constants
from tests.helpers import create_pvc, measure_pvc_creation_time, wait_for_resource_state

log = logging.getLogger(__name__)


@tier1
class TestPVCCreationPerformance(E2ETest):
    """
    Test to verify PVC creation performance
    """
    pvc_size = '1Gi'

    @pytest.fixture()
    def base_setup(
        self, request, interface_iterate, storageclass_factory
    ):
        """
        A setup phase for the test

        Args:
            interface_iterate: A fixture to iterate over ceph interfaces
            storageclass_factory: A fixture to create everything needed for a
                storageclass
        """
        self.interface = interface_iterate
        self.sc_obj = storageclass_factory(self.interface)

    @pytest.mark.usefixtures(base_setup.__name__)
    @polarion_id('OCS-1225')
    @bugzilla('1740139')
    def test_pvc_creation_measurement_performance(self, teardown_factory):
        """
        Measuring PVC creation time
        """
        log.info('Start creating new PVC')

        pvc_obj = create_pvc(sc_name=self.sc_obj.name, size=self.pvc_size)
        teardown_factory(pvc_obj)
        wait_for_resource_state(pvc_obj, constants.STATUS_BOUND)
        pvc_obj.reload()
        create_time = measure_pvc_creation_time('CephBlockPool', pvc_obj.name)
        if create_time > 1:
            raise AssertionError(
                f"PVC creation time is {create_time} and greater than 1 second"
            )
        logging.info("PVC creation took less than a 1 second")