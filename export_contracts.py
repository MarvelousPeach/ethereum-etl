#!/usr/bin/env python3
import argparse

from ethereumetl.file_utils import smart_open
from ethereumetl.ipc import IPCWrapper
from ethereumetl.jobs.export_contracts_job import ExportContractsJob
from ethereumetl.jobs.export_contracts_job_item_exporter import export_contracts_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy

parser = argparse.ArgumentParser(
    description='Exports contracts bytecode using eth_getCode JSON RPC APIs.')
parser.add_argument('-b', '--batch-size', default=100, type=int, help='The number of blocks to filter at a time.')
parser.add_argument('-c', '--contract-addresses', type=str,
                    help='The file containing contract addresses, one per line.')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')
parser.add_argument('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
parser.add_argument('--ipc-path', required=True, type=str, help='The full path to the ipc socket file.')
parser.add_argument('--ipc-timeout', default=300, type=int, help='The timeout in seconds for ipc calls.')

args = parser.parse_args()

with smart_open(args.contract_addresses, 'r') as contract_addresses_file:
    contract_addresses = (contract_address.strip() for contract_address in contract_addresses_file
                          if contract_address.strip())
    job = ExportContractsJob(
        contract_addresses_iterable=contract_addresses,
        batch_size=args.batch_size,
        ipc_wrapper=ThreadLocalProxy(lambda: IPCWrapper(args.ipc_path, timeout=args.ipc_timeout)),
        item_exporter=export_contracts_job_item_exporter(args.output),
        max_workers=args.max_workers)

    job.run()
