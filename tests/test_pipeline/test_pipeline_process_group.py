import os

import torch.distributed.rpc as rpc
import torch.multiprocessing as mp
import pytest

from colossalai.pipeline.pipeline_process_group import PipelineProcessGroup
from colossalai.initialize import launch
from colossalai.logging import disable_existing_loggers
from rpc_test_utils import pg_parse_args, rpc_is_initialized


def run_worker(rank, args):
    os.environ['MASTER_ADDR'] = args.master_addr
    os.environ['MASTER_PORT'] = args.master_port

    device = args.device
    world_size = args.world_size
    dp_degree = args.dp_degree
    tp_degree = args.tp_degree
    num_worker_threads = args.num_worker_threads
    host = args.master_addr
    port = args.master_port
    backend = 'nccl' if device == 'cuda' else 'gloo'

    disable_existing_loggers()
    launch(dict(), rank, world_size, host, int(port), backend, verbose=False)

    pg = PipelineProcessGroup(rank=rank,
                              world_size=world_size,
                              dp_degree=dp_degree,
                              tp_degree=tp_degree,
                              num_worker_threads=num_worker_threads,
                              device=device)

    if rpc_is_initialized():
        rpc.shutdown()


if __name__ == "__main__":
    args = pg_parse_args()
    world_size = args.world_size
    mp.spawn(run_worker, args=(args,), nprocs=world_size)