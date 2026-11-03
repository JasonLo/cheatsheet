# Submitting and monitoring HPC batch jobs with htcondor

_Grounded in JasonLo's repos as of 2026-11-03. Current practice is from htcondor.readthedocs.io and chtc.cs.wisc.edu._

## Reference snippet

```ini
# Container universe job for CHTC. Use container_image, not the older docker universe.
container_image         = docker://ghcr.io/jasonlo/my-cuda-proj:latest

executable              = run.sh

output                  = logs/job.$(Cluster).$(Process).out
error                   = logs/job.$(Cluster).$(Process).err
log                     = logs/job.$(Cluster).log

request_gpus            = 1
gpus_minimum_memory     = 8GB
request_cpus            = 4
request_memory          = 16 GB
request_disk            = 20 GB

want_campus_pools       = true
want_ospool             = true

# For array jobs, substitute $(Process) into arguments.
arguments               = --shard $(Process)
queue 10
```

## Typical usage patterns

- **GPU container job.** Use `container_image = docker://ghcr.io/<org>/<image>:tag` with `request_gpus = 1` and `gpus_minimum_memory` to target cards with enough VRAM (`JasonLo/best-in-slot:slots/infra/htcondor/CHEATSHEET.md`, `JasonLo/skill-sommelier:skills/ss-python-to-chtc/scripts/generate_htcondor.py`).

- **Array job with sharding.** Use `queue N` and `$(Process)` in `arguments` to pass each job its shard index (`JasonLo/best-in-slot:slots/infra/htcondor/CHEATSHEET.md`).

- **Large datasets through Pelican, not condor file transfer.** For datasets larger than a few GB, use `pelican:///` or `osdf:///` URLs inside the container instead of listing them in `transfer_input_files`. This avoids slow condor file transfer for large inputs.

## Learnings

- **`universe = docker` with `docker_image`** → **container universe with `container_image = docker://...`**. The docker universe runs with Docker only, not Apptainer. The container universe lets HTCondor choose the runtime on the execute node, which gives better portability across CHTC and OSPool machines.

- **Submitting without a dry run** → **validate locally with `condor_submit -dry-run /dev/stdout job.sub`**. The dry-run flag parses the submit file and shows resolved ClassAds without contacting the schedd. This catches missing files and syntax errors before the job enters the queue.

- **Polling `condor_q` manually** → **use `condor_tail -f <cluster.proc>` for live stdout**. `condor_q` shows queue state but not job output. `condor_tail` streams the live output file directly, which is faster for debugging a running job.

## Agent rules

- ALWAYS use `container_image = docker://...` (container universe) instead of `universe = docker` with `docker_image`.
- ALWAYS set `$(Cluster)` and `$(Process)` in log, output, and error paths so array job files do not overwrite each other.
- ALWAYS use `gpus_minimum_memory` together with `request_gpus` when the workload needs a specific amount of VRAM.
- NEVER list large input datasets in `transfer_input_files`; use Pelican or OSDF URIs inside the container instead.
- ALWAYS run `condor_submit -dry-run /dev/stdout job.sub` before submitting to a live schedd.
