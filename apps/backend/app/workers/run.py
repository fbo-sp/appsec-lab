"""Processo de worker: ``python -m app.workers.run`` (provisioner + reconciler no mesmo loop).

Com o FakeRuntimeAdapter o estado do runtime vive neste processo; por isso, em desenvolvimento,
execute um único worker. Adapters reais (IMP-301) não têm essa restrição.
"""

from __future__ import annotations

import logging
import os
import signal
import socket
import time
from datetime import timedelta
from types import FrameType

from app.config import Settings
from app.db.engine import make_engine, make_session_factory
from app.runtime.factory import build_runtime
from app.shared.clock import SystemClock
from app.shared.logging import configure_logging
from app.workers.provisioner import WorkerContext, run_once
from app.workers.reconciler import reconcile_once

_log = logging.getLogger("app.worker")


def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    engine = make_engine(settings.database_url)
    ctx = WorkerContext(
        session_factory=make_session_factory(engine),
        runtime=build_runtime(settings),
        clock=SystemClock(),
        worker_id=f"{socket.gethostname()}-{os.getpid()}",
        lease=timedelta(seconds=settings.worker_lease_seconds),
        job_max_attempts=settings.job_max_attempts,
    )
    stopping = False

    def _stop(signum: int, _frame: FrameType | None) -> None:
        nonlocal stopping
        stopping = True
        _log.info("worker_stopping", extra={"event": "worker.stopping", "signal": signum})

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    _log.info(
        "worker_started",
        extra={"event": "worker.started", "worker_id": ctx.worker_id, "runtime": ctx.runtime.provider},
    )
    last_reconcile = 0.0
    while not stopping:
        worked = run_once(ctx)
        if time.monotonic() - last_reconcile >= settings.reconcile_interval_seconds:
            reconcile_once(ctx)
            last_reconcile = time.monotonic()
        if not worked:
            time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
