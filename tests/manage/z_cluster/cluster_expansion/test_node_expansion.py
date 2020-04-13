import logging
import pytest

from ocs_ci.utility.utils import TimeoutSampler
from tests import helpers
from ocs_ci.framework.testlib import tier1, ignore_leftovers, ManageTest, aws_platform_required, ipi_deployment_required
from ocs_ci.ocs import machine as machine_utils
from ocs_ci.ocs import constants
from ocs_ci.ocs.node import wait_for_nodes_status
from ocs_ci.framework import config
from ocs_ci.ocs.platform_nodes import PlatformNodesFactory
logger = logging.getLogger(__name__)


@ignore_leftovers
@tier1
class TestAddNode(ManageTest):
    """
    Automates adding worker nodes to the cluster while IOs
    """
    @aws_platform_required
    def test_add_node_aws(self):
        """
        Test for adding worker nodes to the cluster while IOs
        """
        dt = config.ENV_DATA['deployment_type']
        if dt == 'ipi':
            before_replica_counts = dict()
            machines = machine_utils.get_machinesets()
            for machine in machines:
                before_replica_counts.update(
                    {machine: machine_utils.get_replica_count(machine)}
                )
                logger.info(machine_utils.get_replica_count(machine))
            logger.info(f'The worker nodes number before {len(helpers.get_worker_nodes())}')
            after_replica_counts = dict()
            total_count = 0
            for machine in machines:
                machine_utils.add_node(
                    machine, count=machine_utils.get_replica_count(machine) + 1
                )
                after_replica_counts.update(
                    ({machine: machine_utils.get_replica_count(machine)})
                )
                total_count += machine_utils.get_replica_count(machine)
                logger.info(total_count)
            logger.info(after_replica_counts)
            for sample in TimeoutSampler(
                timeout=600, sleep=6, func=helpers.get_worker_nodes
            ):
                if len(sample) == total_count:
                    break

            logger.info(f'The worker nodes number after {len(helpers.get_worker_nodes())}')
            wait_for_nodes_status(
                node_names=helpers.get_worker_nodes(),
                status=constants.NODE_READY
            )
        else:
            logger.info(f'The worker nodes number before {len(helpers.get_worker_nodes())}')
        #    before_exp = len(helpers.get_worker_nodes())
            plt = PlatformNodesFactory()
            node_util = plt.get_nodes_platform()
            node_util.create_and_attach_nodes_to_cluster({}, 'RHEL', 3)
            # for sample in TimeoutSampler(
            #     timeout=600, sleep=6, func=helpers.get_worker_nodes
            # ):
            #     if len(sample) == before_exp + 3:
            #         break
            # 
            # logger.info(f'The worker nodes number after {len(helpers.get_worker_nodes())}')
        # ToDo run IOs
