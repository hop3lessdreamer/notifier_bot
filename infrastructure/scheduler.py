from taskiq.schedule_sources import LabelScheduleSource
from taskiq_faststream import AppWrapper, StreamScheduler

from infrastructure.tasks import faststream_app

taskiq_broker = AppWrapper(faststream_app)

taskiq_broker.task(
    message=None,
    routing_key='price-check',
    schedule=[
        {
            'cron': '0 */8 * * *',
        }
    ],
)

scheduler = StreamScheduler(
    broker=taskiq_broker,
    sources=[LabelScheduleSource(taskiq_broker)],
)
